"""Document interface adaptation notes and verification checklist for upgrading from MEMORY to Redis.

The current phase does not implement the Redis backend, but codifies the
upgrade path as in-code documentation to prevent migration knowledge from
existing only in external documentation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RedisUpgradePlan:
    """Describe the migration plan for upgrading infrastructure to Redis."""

    cache_store_adapter: str = (
        "RedisCacheStore SHALL implement the same CacheStore contract."
    )
    topic_bus_adapter: str = "RedisTopicBus SHALL implement the same TopicBus contract."
    subscription_registry_adapter: str = "RedisSubscriptionRegistry SHALL implement the same SubscriptionRegistry contract."

    def validation_checklist(self) -> list[str]:
        """Return the upgrade verification checklist.

        Returns:
            Migration check items that must be verified one by one.
        """
        return [
            "Single-instance Redis backend can replace MemoryCacheStore without changing service signatures.",
            "Chart topic keys and quote topic keys remain stable after backend switch.",
            "Snapshot payload shapes remain compatible after backend switch.",
            "Session unsubscribe cleanup still releases topic registrations after backend switch.",
            "Multi-worker publish and subscribe behavior remains consistent across workers.",
        ]
