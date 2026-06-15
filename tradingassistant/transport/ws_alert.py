"""Alert event push WebSocket route.

This module establishes alert event push connections and handles client
subscribe/unsubscribe requests for alert streams by name.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from tradingassistant.charting.keys import alerts_topic
from tradingassistant.infrastructure.subscription_registry import SubscriptionRegistry
from tradingassistant.infrastructure.topic_bus import TopicBus

from .ws_helpers import (
    SessionConnection,
    cleanup_connection,
    subscribe_topic,
    subscription_ack,
    unsubscribe_topic,
)


async def handle_alert_stream(
    *,
    websocket: WebSocket,
    session_id: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """Handle the full lifecycle of alert event push.

    Args:
        websocket: WebSocket connection.
        session_id: Session identifier.
        connections: Session connection mapping.
        registry: Subscription registry.
        topic_bus: Topic bus.
        service: MarketMonitorService instance.
    """

    await websocket.accept()
    loop = asyncio.get_running_loop()
    connection = SessionConnection(session_id=session_id, websocket=websocket)
    connections[session_id] = connection
    try:
        while True:
            raw = await websocket.receive_text()
            payload = (
                json.loads(raw)
                if raw.strip().startswith("{")
                else {"action": "subscribe"}
            )
            action = payload.get("action", "subscribe")
            topic = alerts_topic(payload.get("name", "default"))
            if action == "unsubscribe":
                unsubscribe_topic(
                    session_id, topic, connections, registry, topic_bus, service
                )
                await websocket.send_json(subscription_ack(action, topic))
                continue
            subscribe_topic(
                session_id=session_id,
                topic=topic,
                loop=loop,
                websocket=websocket,
                connections=connections,
                registry=registry,
                topic_bus=topic_bus,
                service=service,
            )
            await websocket.send_json(subscription_ack(action, topic))
    except WebSocketDisconnect:
        cleanup_connection(session_id, connections, registry, topic_bus, service)
