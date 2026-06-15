"""列表行情推送 WebSocket 路由。

该模块负责建立行情列表增量推送连接，处理客户端按名称订阅/退订行情流。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from tradingassistant.charting.keys import quotes_topic
from tradingassistant.infrastructure.subscription_registry import SubscriptionRegistry
from tradingassistant.infrastructure.topic_bus import TopicBus

from .ws_helpers import (
    SessionConnection,
    cleanup_connection,
    subscribe_topic,
    subscription_ack,
    unsubscribe_topic,
)


async def handle_quote_stream(
    *,
    websocket: WebSocket,
    session_id: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: Any,
) -> None:
    """处理列表行情推送的完整生命周期。

    Args:
        websocket: WebSocket 连接。
        session_id: 会话标识。
        connections: 会话连接映射。
        registry: 订阅注册表。
        topic_bus: 主题总线。
        service: MarketMonitorService 实例。
    """

    await websocket.accept()
    loop = asyncio.get_running_loop()
    connection = SessionConnection(session_id=session_id, websocket=websocket)
    connections[session_id] = connection
    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw) if raw.strip().startswith("{") else {"action": "subscribe"}
            action = payload.get("action", "subscribe")
            topic = quotes_topic(payload.get("name", "watchlist"))
            if action == "unsubscribe":
                unsubscribe_topic(session_id, topic, connections, registry, topic_bus, service)
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
