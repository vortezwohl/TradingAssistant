"""Verify default MEMORY implementations of basic abstractions.

This file covers in-process implementations of cache, topic broadcast, and
subscription registration to ensure upper-layer business logic depends on
stable contracts rather than incidental behavior. Also adds MEMORY-path
requirements like eviction and empty-topic reclamation.
"""

from __future__ import annotations

import unittest

from tradingassistant.infrastructure.cache import MemoryCacheStore
from tradingassistant.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.infrastructure.topic_bus import InMemoryTopicBus


class MemoryCacheStoreTests(unittest.TestCase):
    """Test in-memory cache implementation."""

    def test_set_and_get_value(self) -> None:
        """Cache should support write and read."""
        store = MemoryCacheStore()
        store.set("chart:HK.00700:1m", {"bars": 10})
        self.assertEqual(store.get("chart:HK.00700:1m"), {"bars": 10})
        self.assertTrue(store.has("chart:HK.00700:1m"))

    def test_expired_value_is_evicted_on_read(self) -> None:
        """Expired values should be removed on read."""
        store = MemoryCacheStore()
        store.set("temp", {"v": 1}, ttl_seconds=0)
        self.assertIsNone(store.get("temp"))
        self.assertFalse(store.has("temp"))

    def test_clear_removes_all_entries(self) -> None:
        """clear should remove all cache entries."""
        store = MemoryCacheStore()
        store.set("a", 1)
        store.set("b", 2)
        store.clear()
        self.assertFalse(store.has("a"))
        self.assertFalse(store.has("b"))

    def test_capacity_limit_evicts_oldest_entries(self) -> None:
        """Should evict oldest entries when exceeding capacity to prevent unbounded growth."""
        store = MemoryCacheStore(max_entries=2)
        store.set("k1", 1)
        store.set("k2", 2)
        store.set("k3", 3)
        self.assertIsNone(store.get("k1"))
        self.assertEqual(store.get("k2"), 2)
        self.assertEqual(store.get("k3"), 3)


class InMemoryTopicBusTests(unittest.TestCase):
    """Test in-process topic bus."""

    def test_publish_calls_all_subscribers(self) -> None:
        """All subscribers of the same topic should receive messages."""
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
        """Should not receive messages after unsubscribing."""
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
    """Test in-process subscription registry."""

    def test_register_tracks_session_and_topic(self) -> None:
        """Should support bidirectional query after registration."""
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
        """unregister_all should return the list of unlinked topics."""
        registry = InMemorySubscriptionRegistry()
        registry.register("session-1", "chart:HK.00700:1m")
        registry.register("session-1", "quotes:watchlist")
        topics = registry.unregister_all("session-1")
        self.assertEqual(set(topics), {"chart:HK.00700:1m", "quotes:watchlist"})
        self.assertEqual(registry.topics_for_session("session-1"), set())

    def test_unregister_reclaims_empty_topic(self) -> None:
        """Empty topic mapping should be reclaimed after last session unsubscribes."""
        registry = InMemorySubscriptionRegistry()
        registry.register("session-1", "alerts:default")
        registry.unregister("session-1", "alerts:default")
        self.assertEqual(registry.topic_subscriber_count("alerts:default"), 0)
        self.assertEqual(registry.sessions_for_topic("alerts:default"), set())


if __name__ == "__main__":
    unittest.main()
