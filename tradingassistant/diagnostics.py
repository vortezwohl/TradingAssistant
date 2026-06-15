"""提供 MEMORY 路线的基础诊断与运行观测支持。

当前阶段不引入完整监控系统，但仍需要有一个集中位置记录：
1. 缓存命中与未命中；
2. topic 订阅数；
3. 延迟与发布次数；
4. 上游重连与错误计数。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RuntimeMetrics:
    """收集基础运行指标。"""

    cache_hits: int = 0
    cache_misses: int = 0
    publish_count: int = 0
    reconnect_count: int = 0
    error_count: int = 0
    last_publish_latency_ms: float | None = None
    topic_subscribers: dict[str, int] = field(default_factory=dict)
    last_publish_payload: dict[str, Any] | None = None

    def record_cache_hit(self) -> None:
        """记录一次缓存命中。"""
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        """记录一次缓存未命中。"""
        self.cache_misses += 1

    def record_publish(
        self,
        topic: str,
        payload: dict[str, Any],
        subscriber_count: int,
        latency_ms: float | None = None,
    ) -> None:
        """记录一次发布行为。"""
        self.publish_count += 1
        self.topic_subscribers[topic] = subscriber_count
        self.last_publish_payload = payload
        self.last_publish_latency_ms = latency_ms

    def update_topic_subscribers(self, topic: str, subscriber_count: int) -> None:
        """更新某个主题当前的订阅数。"""
        self.topic_subscribers[topic] = subscriber_count

    def record_reconnect(self) -> None:
        """记录一次重连。"""
        self.reconnect_count += 1

    def record_error(self) -> None:
        """记录一次错误。"""
        self.error_count += 1

    def snapshot(self) -> dict[str, Any]:
        """返回可序列化的指标快照。"""
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
