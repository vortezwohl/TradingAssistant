"""提供本地可启动的默认运行时装配入口。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI

from tradingassistant.charting.history import HistoryBackfillService
from tradingassistant.charting.models import RuntimeBar
from tradingassistant.diagnostics import RuntimeMetrics
from tradingassistant.indicators.engine import IncrementalIndicatorEngine
from tradingassistant.infrastructure.cache import MemoryCacheStore
from tradingassistant.infrastructure.subscription_registry import (
    InMemorySubscriptionRegistry,
)
from tradingassistant.infrastructure.topic_bus import InMemoryTopicBus
from tradingassistant.market_data.gateway import ITickMarketGateway
from tradingassistant.settings import ITICK_TOKEN
from tradingassistant.transport.app import MarketMonitorService, create_app


class DemoHistoryGateway:
    """提供本地演示历史数据。"""

    def get_stock_history(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ) -> list[RuntimeBar]:
        """返回一组稳定的演示 K 线数据。"""

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
    """封装后端运行时依赖。"""

    app: FastAPI
    service: MarketMonitorService
    cache_store: MemoryCacheStore
    topic_bus: InMemoryTopicBus
    registry: InMemorySubscriptionRegistry
    metrics: RuntimeMetrics


def build_default_runtime() -> AppRuntime:
    """构造默认运行时对象。

    Returns:
        已完成装配的运行时对象。
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
    """返回默认 FastAPI 应用对象。"""

    return build_default_runtime().app
