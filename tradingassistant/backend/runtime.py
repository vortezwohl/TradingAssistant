"""Default runtime assembly entry point for local startup."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI

from tradingassistant.backend.charting.history import HistoryBackfillService
from tradingassistant.backend.charting.models import RuntimeBar
from tradingassistant.backend.diagnostics import RuntimeMetrics
from tradingassistant.backend.indicators.engine import IncrementalIndicatorEngine
from tradingassistant.backend.infrastructure.cache import MemoryCacheStore
from tradingassistant.backend.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.backend.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.backend.market_data.gateway import ITickMarketGateway
from tradingassistant.backend.transport.app import MarketMonitorService, create_app
from tradingassistant.settings import ITICK_TOKEN


class DemoHistoryGateway:
    """Provide local demo historical data."""

    def get_stock_history(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ) -> list[RuntimeBar]:
        """Return a stable set of demo K-line data."""
        del end
        base_time = datetime(2026, 6, 7, 9, 30, tzinfo=timezone.utc)
        return [
            RuntimeBar(
                symbol=f"{region.upper()}.{code}",
                period=period,
                bar_time=base_time + timedelta(minutes=index),
                open_price=500.0 + index,
                high_price=501.0 + index,
                low_price=499.0 + index,
                close_price=500.5 + index,
                volume=1000 + index,
                turnover=500000 + index * 100,
                provisional=False,
            )
            for index in range(limit)
        ]


@dataclass(slots=True)
class AppRuntime:
    """Encapsulate backend runtime dependencies."""

    app: FastAPI
    service: MarketMonitorService
    cache_store: MemoryCacheStore
    topic_bus: InMemoryTopicBus
    registry: InMemorySubscriptionRegistry
    metrics: RuntimeMetrics


def build_default_runtime() -> AppRuntime:
    """Build the default runtime object.

    Returns:
        Fully assembled runtime object.
    """
    cache_store = MemoryCacheStore()
    topic_bus = InMemoryTopicBus()
    registry = InMemorySubscriptionRegistry()
    metrics = RuntimeMetrics()
    indicator_engine = IncrementalIndicatorEngine()

    if ITICK_TOKEN:
        history_gateway = ITickMarketGateway(ITICK_TOKEN)
    else:
        history_gateway = DemoHistoryGateway()

    history_service = HistoryBackfillService(
        gateway=history_gateway,
        cache_store=cache_store,
    )
    service = MarketMonitorService(
        history_service=history_service,
        cache_store=cache_store,
        topic_bus=topic_bus,
        registry=registry,
        indicator_engine=indicator_engine,
        metrics=metrics,
    )
    app = create_app(
        service=service,
        topic_bus=topic_bus,
        registry=registry,
    )
    return AppRuntime(
        app=app,
        service=service,
        cache_store=cache_store,
        topic_bus=topic_bus,
        registry=registry,
        metrics=metrics,
    )


def create_default_app() -> FastAPI:
    """Return the default FastAPI application object."""
    return build_default_runtime().app
