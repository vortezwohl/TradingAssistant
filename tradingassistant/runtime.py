"""提供本地可启动的默认运行时装配入口。

该模块的职责是把 MemoryCacheStore、TopicBus、SubscriptionRegistry、
历史回填服务、指标引擎和 FastAPI 门面装配成一个可运行的默认实例，
方便本地开发直接启动后端服务。

当前阶段默认使用内置的演示历史数据网关，以保证在没有 iTick 凭据时也能启动。
后续如果提供真实的 iTick token，可以沿着这里的工厂函数平滑替换为真实网关。
"""

from __future__ import annotations

import os
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
from tradingassistant.transport.app import MarketMonitorService, create_app


class DemoHistoryGateway:
    """提供本地开发可用的演示历史数据。"""

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
    """封装后端运行时中需要复用的核心对象。"""

    app: FastAPI
    service: MarketMonitorService
    cache_store: MemoryCacheStore
    topic_bus: InMemoryTopicBus
    registry: InMemorySubscriptionRegistry
    metrics: RuntimeMetrics


def build_default_runtime() -> AppRuntime:
    """构造默认可启动运行时。

    Returns:
        已完成依赖装配的运行时对象。
    """

    cache_store = MemoryCacheStore()
    topic_bus = InMemoryTopicBus()
    registry = InMemorySubscriptionRegistry()
    metrics = RuntimeMetrics()
    indicator_engine = IncrementalIndicatorEngine()

    itick_token = os.getenv("TRADINGASSISTANT_ITICK_TOKEN")
    if itick_token:
        history_gateway = ITickMarketGateway(itick_token)
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
    """返回默认可启动的 FastAPI 应用对象。"""

    return build_default_runtime().app
