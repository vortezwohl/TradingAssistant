"""验证 MEMORY 稳定化与 Redis 升级预留。

本文件覆盖运行态可观测性、稳定 key 结构、可替换基础设施契约以及
从 MEMORY 平滑升级到 Redis 所需的说明与验证清单。
"""

from __future__ import annotations

import unittest

from tradingassistant.charting.keys import (
    alerts_topic,
    bar_history_key,
    chart_snapshot_key,
    chart_topic,
    indicator_snapshot_key,
    quotes_topic,
)
from tradingassistant.diagnostics import RuntimeMetrics
from tradingassistant.infrastructure.cache import MemoryCacheStore
from tradingassistant.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.redis_upgrade import RedisUpgradePlan


class RuntimeMetricsTests(unittest.TestCase):
    """验证运行态基础观测。"""

    def test_runtime_metrics_snapshot_contains_counts(self) -> None:
        """指标快照应记录关键计数。"""

        metrics = RuntimeMetrics()
        metrics.record_cache_hit()
        metrics.record_cache_miss()
        metrics.record_publish("chart:HK.00700:1m", {"bar": 1}, 2, latency_ms=3.5)
        metrics.record_reconnect()
        metrics.record_error()
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["cache_hits"], 1)
        self.assertEqual(snapshot["cache_misses"], 1)
        self.assertEqual(snapshot["publish_count"], 1)
        self.assertEqual(snapshot["reconnect_count"], 1)
        self.assertEqual(snapshot["error_count"], 1)
        self.assertEqual(snapshot["last_publish_latency_ms"], 3.5)

    def test_update_topic_subscribers_overwrites_latest_count(self) -> None:
        """订阅数快照应反映最近一次主题状态。"""

        metrics = RuntimeMetrics()
        metrics.update_topic_subscribers("quotes:watchlist", 2)
        metrics.update_topic_subscribers("quotes:watchlist", 0)
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["topic_subscribers"]["quotes:watchlist"], 0)


class StableKeyTests(unittest.TestCase):
    """验证缓存键与 topic 结构稳定。"""

    def test_chart_and_snapshot_keys_are_stable(self) -> None:
        """chart / snapshot / indicator key 应保持固定格式。"""

        self.assertEqual(chart_topic("HK.00700", "1m"), "chart:HK.00700:1m")
        self.assertEqual(chart_snapshot_key("HK.00700", "1m"), "snapshot:chart:HK.00700:1m")
        self.assertEqual(indicator_snapshot_key("HK.00700", "1m"), "indicator:HK.00700:1m")
        self.assertEqual(bar_history_key("HK.00700", "1m", 240), "history:HK.00700:1m:240")
        self.assertEqual(quotes_topic(), "quotes:watchlist")
        self.assertEqual(alerts_topic(), "alerts:default")


class ReplaceableImplementationsTests(unittest.TestCase):
    """验证默认实现满足可替换后端的基础契约。"""

    def test_memory_cache_behaves_like_replaceable_store(self) -> None:
        """MemoryCacheStore 至少应满足 set/get/delete/clear 流程。"""

        store = MemoryCacheStore()
        store.set("k", {"v": 1})
        self.assertEqual(store.get("k"), {"v": 1})
        store.delete("k")
        self.assertIsNone(store.get("k"))
        store.set("k2", {"v": 2})
        store.clear()
        self.assertIsNone(store.get("k2"))

    def test_topic_bus_and_registry_are_replaceable_contracts(self) -> None:
        """TopicBus 与 SubscriptionRegistry 默认实现应具备可替换语义。"""

        bus = InMemoryTopicBus()
        registry = InMemorySubscriptionRegistry()
        received = []
        handle = bus.subscribe(
            "chart:HK.00700:1m",
            "session-1",
            lambda topic, payload: received.append((topic, payload)),
        )
        registry.register("session-1", "chart:HK.00700:1m")
        count = bus.publish("chart:HK.00700:1m", {"bar": 1})
        self.assertEqual(count, 1)
        self.assertEqual(registry.topic_subscriber_count("chart:HK.00700:1m"), 1)
        bus.unsubscribe(handle)
        registry.unregister_all("session-1")
        self.assertEqual(registry.topic_subscriber_count("chart:HK.00700:1m"), 0)


class RedisUpgradePlanTests(unittest.TestCase):
    """验证 Redis 升级说明。"""

    def test_upgrade_plan_contains_validation_items(self) -> None:
        """迁移计划应包含关键验证项。"""

        plan = RedisUpgradePlan()
        checklist = plan.validation_checklist()
        self.assertGreaterEqual(len(checklist), 5)
        self.assertIn(
            "Multi-worker publish and subscribe behavior remains consistent across workers.",
            checklist,
        )


if __name__ == "__main__":
    unittest.main()
