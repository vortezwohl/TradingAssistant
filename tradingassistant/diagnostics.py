"""Basic diagnostics and runtime observability support for the MEMORY path.

The current phase does not introduce a full monitoring system, but provides
a centralized place to record:
1. Cache hits and misses;
2. Topic subscriber counts;
3. Latency and publish counts;
4. Upstream reconnect and error counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeMetrics:
    """Collect basic runtime metrics."""

    cache_hits: int = 0
    cache_misses: int = 0
    publish_count: int = 0
    reconnect_count: int = 0
    error_count: int = 0
    last_publish_latency_ms: float | None = None
    topic_subscribers: dict[str, int] = field(default_factory=dict)
    last_publish_payload: dict[str, Any] | None = None

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.cache_misses += 1

    def record_publish(
        self,
        topic: str,
        payload: dict[str, Any],
        subscriber_count: int,
        latency_ms: float | None = None,
    ) -> None:
        """Record a publish action."""
        self.publish_count += 1
        self.topic_subscribers[topic] = subscriber_count
        self.last_publish_payload = payload
        self.last_publish_latency_ms = latency_ms

    def update_topic_subscribers(self, topic: str, subscriber_count: int) -> None:
        """Update the current subscriber count for a topic."""
        self.topic_subscribers[topic] = subscriber_count

    def record_reconnect(self) -> None:
        """Record a reconnect."""
        self.reconnect_count += 1

    def record_error(self) -> None:
        """Record an error."""
        self.error_count += 1

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable metrics snapshot."""
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "publish_count": self.publish_count,
            "reconnect_count": self.reconnect_count,
            "error_count": self.error_count,
            "last_publish_latency_ms": self.last_publish_latency_ms,
            "topic_subscribers": dict(self.topic_subscribers),
            "last_publish_payload": self.last_publish_payload,
        }
