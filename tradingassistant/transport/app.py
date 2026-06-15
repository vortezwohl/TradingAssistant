"""实现 FastAPI 传输门面与会话级推送编排。

该模块负责：
1. 暴露图表 bootstrap REST 接口；
2. 通过 TopicBus 与 SubscriptionRegistry 编排 WebSocket 路由；
3. 把高频运行态数据隔离在传输与服务层，不直接压入 Reflex State。

WebSocket 路由实现已提取到独立模块：
- `ws_chart.py` — 图表增量推送
- `ws_quote.py` — 列表行情推送
- `ws_alert.py` — 告警事件推送
- `ws_helpers.py` — 公共订阅生命周期工具
"""

from __future__ import annotations

from time import perf_counter
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

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
from tradingassistant.indicators.engine import IncrementalIndicatorEngine
from tradingassistant.infrastructure.cache import CacheStore
from tradingassistant.infrastructure.subscription_registry import SubscriptionRegistry
from tradingassistant.infrastructure.topic_bus import TopicBus

from .ws_alert import handle_alert_stream
from .ws_chart import handle_chart_stream
from .ws_helpers import SessionConnection
from .ws_quote import handle_quote_stream


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

    def publish_quote_update(self, *, event: QuoteEvent) -> int:
        """发布列表行情增量更新。"""

        payload = {
            "topic": quotes_topic(),
            "payload_type": "quote_update",
            "symbol": event.symbol,
            "last_price": event.last_price,
            "open_price": event.open_price,
            "high_price": event.high_price,
            "low_price": event.low_price,
            "prev_close": event.prev_close,
            "volume": event.volume,
            "turnover": event.turnover,
            "event_time": event.event_time.isoformat(),
        }
        return self._publish(payload["topic"], payload)

    def publish_alert(
        self,
        *,
        symbol: str,
        alert_type: str,
        message: str,
        severity: str = "info",
        name: str = "default",
    ) -> int:
        """发布告警事件。"""

        payload = {
            "topic": alerts_topic(name),
            "payload_type": "alert",
            "symbol": symbol,
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
        }
        return self._publish(payload["topic"], payload)

    def runtime_snapshot(self) -> dict[str, Any]:
        """返回当前运行态快照。"""

        return self.metrics.snapshot()

    def _publish(self, topic: str, payload: dict[str, Any]) -> int:
        """向主题总线发布并记录指标。"""

        start = perf_counter()
        subscriber_count = self.topic_bus.publish(topic, payload)
        latency_ms = (perf_counter() - start) * 1000
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
    """创建 FastAPI 应用，挂载 REST 和 WebSocket 路由。

    WebSocket 路由实现已提取到独立模块（ws_chart/ws_quote/ws_alert.py），
    本函数仅负责装配 app 实例、注册 CORS 和挂载端点。

    Args:
        service: 行情监控服务。
        topic_bus: 主题总线。
        registry: 订阅注册表。

    Returns:
        已完成路由挂载的 FastAPI 应用。
    """

    app = FastAPI(title="TradingAssistant")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:3000",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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
        await handle_chart_stream(
            websocket=websocket,
            session_id=session_id,
            connections=connections,
            registry=registry,
            topic_bus=topic_bus,
            service=service,
        )

    @app.websocket("/ws/quotes/{session_id}")
    async def quote_stream(websocket: WebSocket, session_id: str) -> None:
        """建立列表行情推送连接。"""
        await handle_quote_stream(
            websocket=websocket,
            session_id=session_id,
            connections=connections,
            registry=registry,
            topic_bus=topic_bus,
            service=service,
        )

    @app.websocket("/ws/alerts/{session_id}")
    async def alert_stream(websocket: WebSocket, session_id: str) -> None:
        """建立告警事件推送连接。"""
        await handle_alert_stream(
            websocket=websocket,
            session_id=session_id,
            connections=connections,
            registry=registry,
            topic_bus=topic_bus,
            service=service,
        )

    return app
