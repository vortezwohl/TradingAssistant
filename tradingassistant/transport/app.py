"""实现 FastAPI 传输门面与会话级推送编排。

该模块负责：
1. 暴露图表 bootstrap REST 接口；
2. 暴露图表、列表行情与告警 WebSocket 推送通道；
3. 通过 TopicBus 与 SubscriptionRegistry 协调会话订阅、退订和连接清理；
4. 把高频运行态数据隔离在传输与服务层，不直接压入 Reflex State。
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from tradingassistant.charting.history import HistoryBackfillService
from tradingassistant.charting.keys import (
    alerts_topic,
    chart_snapshot_key,
    chart_topic,
    quotes_topic,
)
from tradingassistant.charting.models import ChartSnapshot, RuntimeBar
from tradingassistant.diagnostics import RuntimeMetrics
from tradingassistant.events import KlineEvent, QuoteEvent
from tradingassistant.infrastructure.cache import CacheStore
from tradingassistant.infrastructure.subscription_registry import SubscriptionRegistry
from tradingassistant.infrastructure.topic_bus import SubscriptionHandle, TopicBus
from tradingassistant.indicators.engine import IncrementalIndicatorEngine


@dataclass(slots=True)
class SessionConnection:
    """记录单个 WebSocket 会话的连接与订阅句柄。"""

    session_id: str
    websocket: WebSocket
    handles: dict[str, SubscriptionHandle] = field(default_factory=dict)


class MarketMonitorService:
    """编排历史回填、指标初始化、缓存写入与主题推送。"""

    def __init__(
        self,
        *,
        history_service: HistoryBackfillService,
        cache_store: CacheStore,
        topic_bus: TopicBus,
        registry: SubscriptionRegistry,
        indicator_engine: IncrementalIndicatorEngine,
        metrics: RuntimeMetrics | None = None,
    ) -> None:
        """初始化服务依赖。"""

        self.history_service = history_service
        self.cache_store = cache_store
        self.topic_bus = topic_bus
        self.registry = registry
        self.indicator_engine = indicator_engine
        self.metrics = metrics or RuntimeMetrics()

    def bootstrap_chart(
        self,
        *,
        region: str,
        code: str,
        period: str,
        bars: int,
    ) -> ChartSnapshot:
        """构造图表 bootstrap 快照。"""

        symbol = f"{region.upper()}.{code}"
        snapshot_key = chart_snapshot_key(symbol, period)
        cached = self.cache_store.get(snapshot_key)
        if cached is not None:
            self.metrics.record_cache_hit()
            return cached

        self.metrics.record_cache_miss()
        history = self.history_service.get_bars(
            region=region,
            code=code,
            period=period,
            limit=bars,
        )
        runtime_bars = [
            RuntimeBar(
                symbol=bar.symbol,
                period=bar.period,
                bar_time=bar.bar_time,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price,
                close_price=bar.close_price,
                volume=bar.volume or 0.0,
                turnover=bar.turnover or 0.0,
                provisional=False,
            )
            for bar in history
        ]
        indicator_key = f"{symbol}:{period}"
        indicator_snapshot = self.indicator_engine.initialize(indicator_key, runtime_bars)
        snapshot = ChartSnapshot(
            topic=chart_topic(symbol, period),
            symbol=symbol,
            period=period,
            bars=[bar.to_dict() for bar in runtime_bars],
            indicators=indicator_snapshot.to_dict(),
            metadata={
                "source": "bootstrap",
                "cache_key": snapshot_key,
                "bar_count": len(runtime_bars),
            },
        )
        self.cache_store.set(snapshot_key, snapshot, ttl_seconds=30)
        return snapshot

    def publish_chart_update(
        self,
        *,
        event: KlineEvent,
        indicators: dict[str, Any],
    ) -> int:
        """发布图表增量更新。"""

        payload = {
            "topic": chart_topic(event.symbol, event.period),
            "payload_type": "bar_update",
            "symbol": event.symbol,
            "period": event.period,
            "provisional": event.provisional,
            "bar": {
                "bar_time": event.bar_time.isoformat() if event.bar_time else None,
                "open_price": event.open_price,
                "high_price": event.high_price,
                "low_price": event.low_price,
                "close_price": event.close_price,
                "volume": event.volume,
                "turnover": event.turnover,
            },
            "indicators": indicators,
        }
        return self._publish(payload["topic"], payload)

    def publish_quote_update(self, event: QuoteEvent) -> int:
        """发布列表行情更新。"""

        payload = {
            "topic": quotes_topic(),
            "payload_type": "quote_update",
            "symbol": event.symbol,
            "last_price": event.last_price,
            "volume": event.volume,
            "turnover": event.turnover,
        }
        return self._publish(payload["topic"], payload)

    def publish_alert(
        self,
        *,
        symbol: str,
        alert_type: str,
        message: str,
        level: str = "info",
        topic_name: str = "default",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """发布告警事件。"""

        payload = {
            "topic": alerts_topic(topic_name),
            "payload_type": "alert_event",
            "symbol": symbol,
            "alert_type": alert_type,
            "message": message,
            "level": level,
            "metadata": metadata or {},
        }
        return self._publish(payload["topic"], payload)

    def runtime_snapshot(self) -> dict[str, Any]:
        """返回当前运行态观测快照。"""

        return self.metrics.snapshot()

    def _publish(self, topic: str, payload: dict[str, Any]) -> int:
        """发布消息并记录最小可观测性指标。"""

        started_at = perf_counter()
        subscriber_count = self.topic_bus.publish(topic, payload)
        latency_ms = (perf_counter() - started_at) * 1000
        self.metrics.record_publish(
            topic,
            payload,
            subscriber_count,
            latency_ms=latency_ms,
        )
        return subscriber_count


def create_app(
    *,
    service: MarketMonitorService,
    topic_bus: TopicBus,
    registry: SubscriptionRegistry,
) -> FastAPI:
    """创建 FastAPI 应用。"""

    app = FastAPI(title="TradingAssistant")
    connections: dict[str, SessionConnection] = {}

    @app.get("/api/chart/bootstrap")
    async def bootstrap_chart(
        region: str,
        code: str,
        period: str = "1m",
        bars: int = 240,
    ) -> dict[str, Any]:
        """返回图表 bootstrap 快照。"""

        return service.bootstrap_chart(
            region=region,
            code=code,
            period=period,
            bars=bars,
        ).to_dict()

    @app.get("/api/runtime/metrics")
    async def runtime_metrics() -> dict[str, Any]:
        """返回 MEMORY 路线的最小运行态指标。"""

        return service.runtime_snapshot()

    @app.websocket("/ws/chart/{session_id}")
    async def chart_stream(websocket: WebSocket, session_id: str) -> None:
        """建立图表增量推送连接。"""

        await websocket.accept()
        loop = asyncio.get_running_loop()
        connection = SessionConnection(session_id=session_id, websocket=websocket)
        connections[session_id] = connection
        try:
            while True:
                raw = await websocket.receive_text()
                payload = json.loads(raw)
                action = payload.get("action", "subscribe")
                symbol = payload["symbol"]
                period = payload.get("period", "1m")
                topic = chart_topic(symbol, period)
                if action == "unsubscribe":
                    _unsubscribe_topic(session_id, topic, connections, registry, topic_bus, service)
                    await websocket.send_json(_subscription_ack(action, topic))
                    continue
                _subscribe_topic(
                    session_id=session_id,
                    topic=topic,
                    loop=loop,
                    websocket=websocket,
                    connections=connections,
                    registry=registry,
                    topic_bus=topic_bus,
                    service=service,
                )
                await websocket.send_json(_subscription_ack(action, topic))
        except WebSocketDisconnect:
            _cleanup_connection(session_id, connections, registry, topic_bus, service)

    @app.websocket("/ws/quotes/{session_id}")
    async def quote_stream(websocket: WebSocket, session_id: str) -> None:
        """建立列表行情推送连接。"""

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
                    _unsubscribe_topic(session_id, topic, connections, registry, topic_bus, service)
                    await websocket.send_json(_subscription_ack(action, topic))
                    continue
                _subscribe_topic(
                    session_id=session_id,
                    topic=topic,
                    loop=loop,
                    websocket=websocket,
                    connections=connections,
                    registry=registry,
                    topic_bus=topic_bus,
                    service=service,
                )
                await websocket.send_json(_subscription_ack(action, topic))
        except WebSocketDisconnect:
            _cleanup_connection(session_id, connections, registry, topic_bus, service)

    @app.websocket("/ws/alerts/{session_id}")
    async def alert_stream(websocket: WebSocket, session_id: str) -> None:
        """建立告警事件推送连接。"""

        await websocket.accept()
        loop = asyncio.get_running_loop()
        connection = SessionConnection(session_id=session_id, websocket=websocket)
        connections[session_id] = connection
        try:
            while True:
                raw = await websocket.receive_text()
                payload = json.loads(raw) if raw.strip().startswith("{") else {"action": "subscribe"}
                action = payload.get("action", "subscribe")
                topic = alerts_topic(payload.get("name", "default"))
                if action == "unsubscribe":
                    _unsubscribe_topic(session_id, topic, connections, registry, topic_bus, service)
                    await websocket.send_json(_subscription_ack(action, topic))
                    continue
                _subscribe_topic(
                    session_id=session_id,
                    topic=topic,
                    loop=loop,
                    websocket=websocket,
                    connections=connections,
                    registry=registry,
                    topic_bus=topic_bus,
                    service=service,
                )
                await websocket.send_json(_subscription_ack(action, topic))
        except WebSocketDisconnect:
            _cleanup_connection(session_id, connections, registry, topic_bus, service)

    return app


def _subscribe_topic(
    *,
    session_id: str,
    topic: str,
    loop: asyncio.AbstractEventLoop,
    websocket: WebSocket,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: MarketMonitorService,
) -> None:
    """统一处理会话订阅。"""

    connection = connections[session_id]
    if topic in connection.handles:
        return
    registry.register(session_id, topic)
    handle = topic_bus.subscribe(
        topic,
        f"{session_id}:{topic}",
        _make_sender_callback(loop, websocket),
    )
    connection.handles[topic] = handle
    service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))


def _unsubscribe_topic(
    session_id: str,
    topic: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: MarketMonitorService,
) -> None:
    """统一处理会话退订与空主题回收。"""

    connection = connections.get(session_id)
    if connection is None:
        return
    handle = connection.handles.pop(topic, None)
    if handle is not None:
        topic_bus.unsubscribe(handle)
    registry.unregister(session_id, topic)
    service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))


def _make_sender_callback(
    loop: asyncio.AbstractEventLoop,
    websocket: WebSocket,
):
    """为指定连接创建线程安全的消息发送回调。"""

    def sender(_topic: str, payload: Any) -> None:
        """把同步广播事件调度到连接所在事件循环中。"""

        loop.call_soon_threadsafe(
            asyncio.create_task,
            websocket.send_json(payload),
        )

    return sender


def _subscription_ack(action: str, topic: str) -> dict[str, str]:
    """构造订阅生命周期确认消息。"""

    return {
        "payload_type": "subscription_ack",
        "action": action,
        "topic": topic,
    }


def _cleanup_connection(
    session_id: str,
    connections: dict[str, SessionConnection],
    registry: SubscriptionRegistry,
    topic_bus: TopicBus,
    service: MarketMonitorService,
) -> None:
    """统一清理连接、主题订阅与运行态计数。"""

    topics = registry.unregister_all(session_id)
    connection = connections.pop(session_id, None)
    if connection is not None:
        for handle in connection.handles.values():
            topic_bus.unsubscribe(handle)
    for topic in topics:
        service.metrics.update_topic_subscribers(topic, registry.topic_subscriber_count(topic))
