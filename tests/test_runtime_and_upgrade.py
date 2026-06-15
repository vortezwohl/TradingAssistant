"""Verify MEMORY stabilization and Redis upgrade provisions.

This file covers runtime observability, stable key structures, replaceable
infrastructure contracts, and the documentation and verification checklist
for smooth MEMORY-to-Redis upgrade.
"""

from __future__ import annotations

import unittest

from tradingassistant.backend.charting.keys import (
    alerts_topic,
    bar_history_key,
    chart_snapshot_key,
    chart_topic,
    indicator_snapshot_key,
    quotes_topic,
)
from tradingassistant.backend.diagnostics import RuntimeMetrics
from tradingassistant.backend.infrastructure.cache import MemoryCacheStore
from tradingassistant.backend.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.backend.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.backend.redis_upgrade import RedisUpgradePlan


class RuntimeMetricsTests(unittest.TestCase):
    """Test basic runtime observability."""

    def test_runtime_metrics_snapshot_contains_counts(self) -> None:
        """Metrics snapshot should record key counts."""
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
        """Subscriber count snapshot should reflect latest topic state."""
        metrics = RuntimeMetrics()
        metrics.update_topic_subscribers("quotes:watchlist", 2)
        metrics.update_topic_subscribers("quotes:watchlist", 0)
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["topic_subscribers"]["quotes:watchlist"], 0)


class StableKeyTests(unittest.TestCase):
    """Verify cache key and topic structure stability."""

    def test_chart_and_snapshot_keys_are_stable(self) -> None:
        """Chart/snapshot/indicator keys should maintain fixed format."""
        self.assertEqual(chart_topic("HK.00700", "1m"), "chart:HK.00700:1m")
        self.assertEqual(
            chart_snapshot_key("HK.00700", "1m"), "snapshot:chart:HK.00700:1m"
        )
        self.assertEqual(
            indicator_snapshot_key("HK.00700", "1m"), "indicator:HK.00700:1m"
        )
        self.assertEqual(
            bar_history_key("HK.00700", "1m", 240), "history:HK.00700:1m:240"
        )
        self.assertEqual(quotes_topic(), "quotes:watchlist")
        self.assertEqual(alerts_topic(), "alerts:default")


class ReplaceableImplementationsTests(unittest.TestCase):
    """Verify default implementations satisfy replaceable backend contracts."""

    def test_memory_cache_behaves_like_replaceable_store(self) -> None:
        """MemoryCacheStore should at least fulfill set/get/delete/clear flow."""
        store = MemoryCacheStore()
        store.set("k", {"v": 1})
        self.assertEqual(store.get("k"), {"v": 1})
        store.delete("k")
        self.assertIsNone(store.get("k"))
        store.set("k2", {"v": 2})
        store.clear()
        self.assertIsNone(store.get("k2"))

    def test_topic_bus_and_registry_are_replaceable_contracts(self) -> None:
        """TopicBus and SubscriptionRegistry defaults should have replaceable semantics."""
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
    """Test Redis upgrade documentation."""

    def test_upgrade_plan_contains_validation_items(self) -> None:
        """Migration plan should contain key verification items."""
        plan = RedisUpgradePlan()
        checklist = plan.validation_checklist()
        self.assertGreaterEqual(len(checklist), 5)
        self.assertIn(
            "Multi-worker publish and subscribe behavior remains consistent across workers.",
            checklist,
        )


if __name__ == "__main__":
    unittest.main()
