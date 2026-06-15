"""WebSocket session management and subscription lifecycle shared utilities.

This module provides shared utilities for all transport-layer WebSocket routes:
1. Session connection structure;
2. Subscribe/unsubscribe/cleanup logic;
3. Thread-safe message send callbacks.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from tradingassistant.backend.infrastructure.subscription_registry import (
    SubscriptionRegistry,
)
from tradingassistant.backend.infrastructure.topic_bus import (
    SubscriptionHandle,
    TopicBus,
)


@dataclass(slots=True)
class SessionConnection:
    """Record connection and subscription handles for a single WebSocket session.

    Args:
        session_id: Session identifier.
        websocket: WebSocket connection object.
        handles: Topic to subscription handle mapping.
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
    """Unified session subscription handling.

    Args:
        session_id: Session identifier.
        topic: Topic identifier.
        loop: Event loop.
        websocket: WebSocket connection.
        connections: Session connection mapping.
        registry: Subscription registry.
        topic_bus: Topic bus.
        service: MarketMonitorService instance.
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
    service.metrics.update_topic_subscribers(
        topic, registry.topic_subscriber_count(topic)
    )


def unsubscribe_topic(
    session_id: str,
    topic: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """Unified session unsubscription and empty topic cleanup.

    Args:
        session_id: Session identifier.
        topic: Topic identifier.
        connections: Session connection mapping.
        registry: Subscription registry.
        topic_bus: Topic bus.
        service: MarketMonitorService instance.
    """

    connection = connections.get(session_id)
    if connection is None:
        return
    handle = connection.handles.pop(topic, None)
    if handle is not None:
        topic_bus.unsubscribe(handle)
    registry.unregister(session_id, topic)
    service.metrics.update_topic_subscribers(
        topic, registry.topic_subscriber_count(topic)
    )


def make_sender_callback(
    loop: asyncio.AbstractEventLoop,
    websocket: WebSocket,
):
    """Create a thread-safe message send callback for a connection.

    Args:
        loop: Event loop.
        websocket: WebSocket connection.

    Returns:
        Thread-safe message send callback function.
    """

    def sender(_topic: str, payload: Any) -> None:
        """Schedule a synchronous broadcast event onto the connection event loop."""
        loop.call_soon_threadsafe(
            asyncio.create_task,
            websocket.send_json(payload),
        )

    return sender


def subscription_ack(action: str, topic: str) -> dict[str, str]:
    """Build a subscription lifecycle acknowledgment message.

    Args:
        action: Subscription action.
        topic: Topic identifier.

    Returns:
        Acknowledgment message dict.
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
    """Unified cleanup of connection, topic subscriptions, and runtime counters.

    Args:
        session_id: Session identifier.
        connections: Session connection mapping.
        registry: Subscription registry.
        topic_bus: Topic bus.
        service: MarketMonitorService instance.
    """

    topics = registry.unregister_all(session_id)
    connection = connections.pop(session_id, None)
    if connection is not None:
        for handle in connection.handles.values():
            topic_bus.unsubscribe(handle)
    for topic in topics:
        service.metrics.update_topic_subscribers(
            topic, registry.topic_subscriber_count(topic)
        )
