"""记录从 MEMORY 升级到 Redis 所需的接口适配说明与验证清单。

当前阶段不实现 Redis 后端，但需要把升级路径固化为程序内可引用的说明，
避免迁移知识只存在于外部文档中。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RedisUpgradePlan:
    """描述基础设施升级到 Redis 的迁移计划。"""

    cache_store_adapter: str = "RedisCacheStore SHALL implement the same CacheStore contract."
    topic_bus_adapter: str = "RedisTopicBus SHALL implement the same TopicBus contract."
    subscription_registry_adapter: str = (
        "RedisSubscriptionRegistry SHALL implement the same SubscriptionRegistry contract."
    )

    def validation_checklist(self) -> list[str]:
        """返回升级验证清单。

        Returns:
            需要逐项验证的迁移检查项。
        """
        return [
            "Single-instance Redis backend can replace MemoryCacheStore without changing service signatures.",
            "Chart topic keys and quote topic keys remain stable after backend switch.",
            "Snapshot payload shapes remain compatible after backend switch.",
            "Session unsubscribe cleanup still releases topic registrations after backend switch.",
            "Multi-worker publish and subscribe behavior remains consistent across workers.",
        ]
