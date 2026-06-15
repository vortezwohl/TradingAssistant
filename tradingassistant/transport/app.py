"""FastAPI transport facade and session-level push orchestration.

This module is responsible for:
1. Exposing chart bootstrap REST endpoints;
2. Orchestrating WebSocket routes via TopicBus and SubscriptionRegistry;
3. Isolating high-frequency runtime data in the transport and service layers,
   preventing direct writes to Reflex State.

WebSocket route implementations have been extracted into separate modules:
- `ws_chart.py` — Chart increment push
- `ws_quote.py` — Quote list push
- `ws_alert.py` — Alert event push
- `ws_helpers.py` — Shared subscription lifecycle utilities
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
    """Orchestrate history backfill, indicator initialization, cache writes, and topic push."""

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
        """Initialize service dependencies."""

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
        """Build a chart bootstrap snapshot."""

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
        indicator_snapshot = self.indicator_engine.initialize(
            indicator_key, runtime_bars
        )
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
        """Publish a chart increment update."""

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
        """Publish a quote list increment update."""

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
        """Publish an alert event."""

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
        """Return the current runtime snapshot."""

        return self.metrics.snapshot()

    def _publish(self, topic: str, payload: dict[str, Any]) -> int:
        """Publish to the topic bus and record metrics."""

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
    """Create a FastAPI app with REST and WebSocket routes mounted.

    WebSocket route implementations have been extracted to separate modules
    (ws_chart/ws_quote/ws_alert.py); this function only assembles the app
    instance, registers CORS, and mounts endpoints.

    Args:
        service: Market monitor service.
        topic_bus: Topic bus.
        registry: Subscription registry.

    Returns:
        Fully assembled FastAPI app.
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
        """Return a chart bootstrap snapshot."""
        return service.bootstrap_chart(
            region=region,
            code=code,
            period=period,
            bars=bars,
        ).to_dict()

    @app.get("/api/runtime/metrics")
    async def runtime_metrics() -> dict[str, Any]:
        """Return minimal runtime metrics for the MEMORY path."""
        return service.runtime_snapshot()

    @app.websocket("/ws/chart/{session_id}")
    async def chart_stream(websocket: WebSocket, session_id: str) -> None:
        """Establish a chart increment push connection."""
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
        """Establish a quote list push connection."""
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
        """Establish an alert event push connection."""
        await handle_alert_stream(
            websocket=websocket,
            session_id=session_id,
            connections=connections,
            registry=registry,
            topic_bus=topic_bus,
            service=service,
        )

    return app
