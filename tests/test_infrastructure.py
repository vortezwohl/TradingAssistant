"""验证基础抽象的默认 MEMORY 实现。

本文件覆盖缓存、主题广播和订阅注册的进程内实现，确保上层业务依赖的是
稳定契约，而不是偶然行为。同时补充内存淘汰与空主题回收等 MEMORY 路线要求。
"""

from __future__ import annotations

import unittest

from tradingassistant.infrastructure.cache import MemoryCacheStore
from tradingassistant.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.infrastructure.topic_bus import InMemoryTopicBus


class MemoryCacheStoreTests(unittest.TestCase):
    """验证内存缓存实现。"""

    def test_set_and_get_value(self) -> None:
        """缓存应支持写入与读取。"""
        store = MemoryCacheStore()
        store.set("chart:HK.00700:1m", {"bars": 10})
        self.assertEqual(store.get("chart:HK.00700:1m"), {"bars": 10})
        self.assertTrue(store.has("chart:HK.00700:1m"))

    def test_expired_value_is_evicted_on_read(self) -> None:
        """过期值在读取时应被移除。"""
        store = MemoryCacheStore()
        store.set("temp", {"v": 1}, ttl_seconds=0)
        self.assertIsNone(store.get("temp"))
        self.assertFalse(store.has("temp"))

    def test_clear_removes_all_entries(self) -> None:
        """clear 应清空全部缓存。"""
        store = MemoryCacheStore()
        store.set("a", 1)
        store.set("b", 2)
        store.clear()
        self.assertFalse(store.has("a"))
        self.assertFalse(store.has("b"))

    def test_capacity_limit_evicts_oldest_entries(self) -> None:
        """超过容量时应淘汰最旧条目，避免热状态无限增长。"""
        store = MemoryCacheStore(max_entries=2)
        store.set("k1", 1)
        store.set("k2", 2)
        store.set("k3", 3)
        self.assertIsNone(store.get("k1"))
        self.assertEqual(store.get("k2"), 2)
        self.assertEqual(store.get("k3"), 3)


class InMemoryTopicBusTests(unittest.TestCase):
    """验证进程内主题总线。"""

    def test_publish_calls_all_subscribers(self) -> None:
        """同一主题的所有订阅者都应收到消息。"""
        bus = InMemoryTopicBus()
        received: list[tuple[str, object]] = []

        bus.subscribe(
            "chart:HK.00700:1m",
            "session-1",
            lambda topic, payload: received.append((topic, payload)),
        )
        bus.subscribe(
            "chart:HK.00700:1m",
            "session-2",
            lambda topic, payload: received.append((topic, payload)),
        )

        count = bus.publish("chart:HK.00700:1m", {"close": 501.2})
        self.assertEqual(count, 2)
        self.assertEqual(len(received), 2)
        self.assertTrue(all(topic == "chart:HK.00700:1m" for topic, _ in received))

    def test_unsubscribe_removes_subscriber(self) -> None:
        """取消订阅后不应再收到消息。"""
        bus = InMemoryTopicBus()
        received: list[tuple[str, object]] = []
        handle = bus.subscribe(
            "quotes:watchlist",
            "session-1",
            lambda topic, payload: received.append((topic, payload)),
        )
        bus.unsubscribe(handle)
        count = bus.publish("quotes:watchlist", {"symbol": "HK.00700"})
        self.assertEqual(count, 0)
        self.assertEqual(received, [])
        self.assertEqual(bus.subscriber_count("quotes:watchlist"), 0)


class InMemorySubscriptionRegistryTests(unittest.TestCase):
    """验证进程内订阅注册表。"""

    def test_register_tracks_session_and_topic(self) -> None:
        """注册后应能双向查询。"""
        registry = InMemorySubscriptionRegistry()
        registry.register("session-1", "chart:HK.00700:1m")
        self.assertEqual(
            registry.topics_for_session("session-1"),
            {"chart:HK.00700:1m"},
        )
        self.assertEqual(
            registry.sessions_for_topic("chart:HK.00700:1m"),
            {"session-1"},
        )
        self.assertEqual(
            registry.topic_subscriber_count("chart:HK.00700:1m"),
            1,
        )

    def test_unregister_all_returns_affected_topics(self) -> None:
        """unregister_all 应返回解除关联的主题列表。"""
        registry = InMemorySubscriptionRegistry()
        registry.register("session-1", "chart:HK.00700:1m")
        registry.register("session-1", "quotes:watchlist")
        topics = registry.unregister_all("session-1")
        self.assertEqual(set(topics), {"chart:HK.00700:1m", "quotes:watchlist"})
        self.assertEqual(registry.topics_for_session("session-1"), set())

    def test_unregister_reclaims_empty_topic(self) -> None:
        """最后一个会话退订后应回收空主题映射。"""
        registry = InMemorySubscriptionRegistry()
        registry.register("session-1", "alerts:default")
        registry.unregister("session-1", "alerts:default")
        self.assertEqual(registry.topic_subscriber_count("alerts:default"), 0)
        self.assertEqual(registry.sessions_for_topic("alerts:default"), set())


if __name__ == "__main__":
    unittest.main()
