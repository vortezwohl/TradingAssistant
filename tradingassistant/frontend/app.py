"""定义 Reflex 看盘页的主布局与图表入口。

本页面负责：
1. 组织低频交互控件、图表容器与指标面板；
2. 把 bootstrap 地址、实时通道地址和上下文参数传给浏览器图表层；
3. 保持页面状态轻量，不直接持有高频行情或 K 线流。
"""

from __future__ import annotations

import reflex as rx

from .charting import chart_canvas, indicator_summary_card
from .state import WatchPageState


def _watchlist_selector() -> rx.Component:
    """构造标的切换控件。"""

    return rx.vstack(
        rx.text("标的", size="2", weight="bold"),
        rx.select(
            WatchPageState.watchlist,
            value=WatchPageState.symbol,
            on_change=WatchPageState.set_symbol,
            width="100%",
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _period_selector() -> rx.Component:
    """构造周期切换控件。"""

    return rx.vstack(
        rx.text("周期", size="2", weight="bold"),
        rx.select(
            WatchPageState.available_periods,
            value=WatchPageState.period,
            on_change=WatchPageState.set_period,
            width="100%",
        ),
        align="stretch",
        spacing="2",
        width="100%",
    )


def _indicator_selector(indicator: str) -> rx.Component:
    """构造单个指标复选项。"""

    return rx.checkbox(
        indicator.upper(),
        checked=WatchPageState.indicators.contains(indicator),
        on_change=lambda checked: WatchPageState.set_indicator_enabled(indicator, checked),
        size="2",
    )


def _indicator_panel() -> rx.Component:
    """构造指标开关面板。"""

    return rx.card(
        rx.vstack(
            rx.text("指标开关", size="2", weight="bold"),
            rx.foreach(
                WatchPageState.indicator_candidates,
                _indicator_selector,
            ),
            spacing="2",
            align="stretch",
        ),
        size="3",
        width="100%",
    )


def _endpoint_panel() -> rx.Component:
    """构造当前连接信息面板。"""

    return rx.card(
        rx.vstack(
            rx.text("连接信息", size="2", weight="bold"),
            rx.code(WatchPageState.api_base_url, width="100%"),
            rx.text("Bootstrap", size="2", color_scheme="gray"),
            rx.code(WatchPageState.bootstrap_url, width="100%"),
            rx.text("Chart WS", size="2", color_scheme="gray"),
            rx.code(WatchPageState.chart_socket_url, width="100%"),
            rx.text("订阅意图", size="2", color_scheme="gray"),
            rx.code(WatchPageState.chart_subscription_payload, width="100%"),
            spacing="2",
            align="stretch",
        ),
        size="3",
        width="100%",
    )


def _chart_workspace() -> rx.Component:
    """构造图表工作区。"""

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(WatchPageState.chart_title, size="6"),
                    rx.text(
                        "首屏使用 bootstrap，实时更新通过浏览器内 WebSocket 本地应用。",
                        color_scheme="gray",
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.badge("MEMORY-first", color_scheme="green"),
                    rx.badge(WatchPageState.symbol),
                    rx.badge(WatchPageState.period),
                    spacing="2",
                ),
                width="100%",
                align="start",
            ),
            rx.grid(
                rx.box(
                    chart_canvas(
                        container_id="watch-chart-root",
                        bootstrap_url=WatchPageState.bootstrap_url,
                        chart_socket_url=WatchPageState.chart_socket_url,
                        api_base_url=WatchPageState.api_base_url,
                        symbol=WatchPageState.symbol,
                        period=WatchPageState.period,
                        indicators_json=WatchPageState.indicator_selection_json,
                    ),
                    min_height="640px",
                    width="100%",
                ),
                indicator_summary_card(),
                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),
            spacing="4",
            align="stretch",
        ),
        size="4",
        width="100%",
    )


def index() -> rx.Component:
    """构建完整看盘页面。"""

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("TradingAssistant", size="8"),
                    rx.text(
                        "Reflex + FastAPI + iTick/OpenTrade 的实时看盘前端闭环。",
                        size="3",
                        color_scheme="gray",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge("Chart Frontend", color_scheme="blue", size="3"),
                width="100%",
                align="start",
            ),
            rx.grid(
                rx.vstack(
                    _watchlist_selector(),
                    _period_selector(),
                    _indicator_panel(),
                    _endpoint_panel(),
                    spacing="4",
                    align="stretch",
                    width="100%",
                ),
                _chart_workspace(),
                columns=rx.breakpoints(initial="1", xl="2"),
                spacing="6",
                width="100%",
            ),
            spacing="6",
            align="stretch",
            width="100%",
            max_width="1600px",
            margin="0 auto",
            padding="2.5rem 1.5rem 3rem",
        ),
        width="100%",
        min_height="100vh",
        background="linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%)",
    )


app = rx.App()
app.add_page(index, route="/")
