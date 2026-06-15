"""WebSocket 会话管理与订阅生命周期公共工具。

该模块提供 transport 层各 WebSocket 路由共用的：
1. 会话连接结构体；
2. 订阅/退订/清理逻辑；
3. 线程安全的消息发送回调。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from tradingassistant.infrastructure.subscription_registry import SubscriptionRegistry
from tradingassistant.infrastructure.topic_bus import SubscriptionHandle, TopicBus


@dataclass(slots=True)
class SessionConnection:
    """记录单个 WebSocket 会话的连接与订阅句柄。

    Args:
        session_id: 会话标识。
        websocket: WebSocket 连接对象。
        handles: 主题到订阅句柄的映射。
    """

    session_id: str
    websocket: WebSocket
    handles: dict[str, SubscriptionHandle] = field(default_factory=dict)


def subscribe_topic(
    *,
    session_id: str,
    topic: str,
    loop: asyncio.AbstractEventLoop,
    websocket: WebSocket,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """统一处理会话订阅。

    Args:
        session_id: 会话标识。
        topic: 主题标识。
        loop: 事件循环。
        websocket: WebSocket 连接。
        connections: 会话连接映射。
        registry: 订阅注册表。
        topic_bus: 主题总线。
        service: MarketMonitorService 实例。
    """

    connection = connections[session_id]
    if topic in connection.handles:
        return
    registry.register(session_id, topic)
    handle = topic_bus.subscribe(
        topic,
        f"{session_id}:{topic}",
        make_sender_callback(loop, websocket),
    )
    connection.handles[topic] = handle
    service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))


def unsubscribe_topic(
    session_id: str,
    topic: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """统一处理会话退订与空主题回收。

    Args:
        session_id: 会话标识。
        topic: 主题标识。
        connections: 会话连接映射。
        registry: 订阅注册表。
        topic_bus: 主题总线。
        service: MarketMonitorService 实例。
    """

    connection = connections.get(session_id)
    if connection is None:
        return
    handle = connection.handles.pop(topic, None)
    if handle is not None:
        topic_bus.unsubscribe(handle)
    registry.unregister(session_id, topic)
    service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))


def make_sender_callback(
    loop: asyncio.AbstractEventLoop,
    websocket: WebSocket,
):
    """为指定连接创建线程安全的消息发送回调。

    Args:
        loop: 事件循环。
        websocket: WebSocket 连接。

    Returns:
        线程安全的消息发送回调函数。
    """

    def sender(_topic: str, payload: Any) -> None:
        """把同步广播事件调度到连接所在事件循环中。"""
        loop.call_soon_threadsafe(
            asyncio.create_task,
            websocket.send_json(payload),
        )

    return sender


def subscription_ack(action: str, topic: str) -> dict[str, str]:
    """构造订阅生命周期确认消息。

    Args:
        action: 订阅动作。
        topic: 主题标识。

    Returns:
        确认消息字典。
    """

    return {
        "payload_type": "subscription_ack",
        "action": action,
        "topic": topic,
    }


def cleanup_connection(
    session_id: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """统一清理连接、主题订阅与运行态计数。

    Args:
        session_id: 会话标识。
        connections: 会话连接映射。
        registry: 订阅注册表。
        topic_bus: 主题总线。
        service: MarketMonitorService 实例。
    """

    topics = registry.unregister_all(session_id)
    connection = connections.pop(session_id, None)
    if connection is not None:
        for handle in connection.handles.values():
            topic_bus.unsubscribe(handle)
    for topic in topics:
        service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))
