"""定义 Reflex 看盘页的交易工作区布局与浏览器图表入口。

本页面负责：
1. 以图表优先的方式组织首屏命令条、主图工作区与右侧摘要栏；
2. 把 bootstrap 地址、实时通道地址和上下文参数传给浏览器图表层；
3. 通过渐进披露保留低频设置与 diagnostics，不让它们挤占首屏注意力。
"""

from __future__ import annotations

import reflex as rx

from .charting import chart_canvas, indicator_summary_card
from .state import WatchPageState
from .theme import (
    TRADING_COLORS,
    command_select_style,
    diagnostics_panel_style,
    eyebrow_badge,
    hero_panel_style,
    muted_text_style,
    shell_box_style,
    subtle_code_style,
    top_bar_style,
    workspace_container_style,
)


def _selector_block(label: str, control: rx.Component, hint: str) -> rx.Component:
    """构造顶部命令条中的单个选择区块。"""

    return rx.vstack(
        rx.text(
            label,
            size="1",
            weight="bold",
            style={
                "color": TRADING_COLORS["text_muted"],
                "letter_spacing": "0.08em",
                "text_transform": "uppercase",
            },
        ),
        control,
        rx.text(hint, size="1", style=muted_text_style()),
        spacing="1",
        align="stretch",
        width="100%",
    )


def _watchlist_selector() -> rx.Component:
    """构造顶部标的切换控件。"""

    return _selector_block(
        "Symbol",
        rx.select(
            WatchPageState.watchlist,
            value=WatchPageState.symbol,
            on_change=WatchPageState.set_symbol,
            width="100%",
            style=command_select_style(),
        ),
        "主图上下文会随标的切换重建。",
    )


def _period_selector() -> rx.Component:
    """构造顶部周期切换控件。"""

    return _selector_block(
        "Period",
        rx.select(
            WatchPageState.available_periods,
            value=WatchPageState.period,
            on_change=WatchPageState.set_period,
            width="100%",
            style=command_select_style(),
        ),
        "优先保证图表可读性，再做周期切换。",
    )


def _indicator_selector(indicator: str) -> rx.Component:
    """构造低频指标复选项。"""

    return rx.checkbox(
        indicator.upper(),
        checked=WatchPageState.indicators.contains(indicator),
        on_change=lambda checked: WatchPageState.set_indicator_enabled(indicator, checked),
        size="2",
        spacing="2",
        style={
            "padding": "0.35rem 0.2rem",
            "color": TRADING_COLORS["text"],
        },
    )


def _command_bar() -> rx.Component:
    """构造首屏顶部命令条。"""

    return rx.box(
        rx.flex(
            rx.vstack(
                rx.hstack(
                    eyebrow_badge("BLOOMBERG-INSPIRED"),
                    eyebrow_badge(
                        "LIVE",
                        color=TRADING_COLORS["bull"],
                        background="rgba(49, 196, 141, 0.14)",
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                rx.heading(
                    "TradingAssistant",
                    size="8",
                    style={
                        "font_size": "clamp(2rem, 4vw, 3.3rem)",
                        "letter_spacing": "-0.05em",
                    },
                ),
                rx.text(
                    "Chart-first trading workspace for bootstrap and realtime flow.",
                    size="3",
                    style=muted_text_style(),
                ),
                align="start",
                spacing="2",
                width="100%",
                max_width="34rem",
            ),
            rx.spacer(),
            rx.vstack(
                rx.grid(
                    _watchlist_selector(),
                    _period_selector(),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                rx.hstack(
                    eyebrow_badge(
                        WatchPageState.symbol,
                        color=TRADING_COLORS["text"],
                        background="rgba(73, 167, 255, 0.14)",
                    ),
                    eyebrow_badge(
                        WatchPageState.period,
                        color=TRADING_COLORS["info"],
                        background="rgba(73, 167, 255, 0.1)",
                    ),
                    eyebrow_badge(
                        "MEMORY-FIRST",
                        color=TRADING_COLORS["accent"],
                    ),
                    spacing="2",
                    wrap="wrap",
                    width="100%",
                ),
                width=rx.breakpoints(initial="100%", xl="31rem"),
                spacing="3",
                align="stretch",
            ),
            direction=rx.breakpoints(initial="column", xl="row"),
            spacing="5",
            align=rx.breakpoints(initial="start", xl="center"),
            width="100%",
        ),
        data_role="command-bar",
        style=top_bar_style(),
    )


def _chart_workspace() -> rx.Component:
    """构造主图工作区。"""

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "实时图表工作区",
                        size="1",
                        weight="bold",
                        style={
                            "color": TRADING_COLORS["text_muted"],
                            "letter_spacing": "0.08em",
                            "text_transform": "uppercase",
                        },
                    ),
                    rx.heading(WatchPageState.chart_title, size="7"),
                    rx.text(
                        "首屏只保留价格结构、当前上下文与关键状态；低频设置与 diagnostics 下沉到后续分区。",
                        size="2",
                        style=muted_text_style(),
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.hstack(
                        eyebrow_badge(
                            "Bootstrap",
                            color=TRADING_COLORS["info"],
                            background="rgba(73, 167, 255, 0.1)",
                        ),
                        eyebrow_badge(
                            "Realtime WS",
                            color=TRADING_COLORS["bull"],
                            background="rgba(49, 196, 141, 0.12)",
                        ),
                        spacing="2",
                        wrap="wrap",
                        justify="end",
                    ),
                    rx.text(
                        "形成中与已确认语义会直接映射到右侧摘要栏。",
                        size="1",
                        style=muted_text_style(),
                    ),
                    spacing="1",
                    align=rx.breakpoints(initial="start", md="end"),
                ),
                width="100%",
                align="start",
                spacing="4",
                direction=rx.breakpoints(initial="column", md="row"),
            ),
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
                min_height=rx.breakpoints(initial="560px", xl="760px"),
                width="100%",
            ),
            spacing="4",
            align="stretch",
        ),
        data_role="chart-workspace",
        style=hero_panel_style(),
    )


def _indicator_configuration_panel() -> rx.Component:
    """构造下沉的指标与观察列表面板。"""

    return rx.el.details(
        rx.el.summary(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "低频配置",
                        size="1",
                        weight="bold",
                        style={
                            "color": TRADING_COLORS["text_muted"],
                            "letter_spacing": "0.08em",
                            "text_transform": "uppercase",
                        },
                    ),
                    rx.text("指标开关与观察列表", size="3", weight="bold"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.icon("panel_right_open", size=18, color=TRADING_COLORS["text_soft"]),
                width="100%",
                align="center",
                style={"cursor": "pointer", "list_style": "none"},
            ),
        ),
        rx.vstack(
            rx.text(
                "这些控件保留完整性，但默认不与主图争抢首屏注意力。",
                size="2",
                style=muted_text_style(),
            ),
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("当前自选", size="2", weight="bold"),
                        rx.flex(
                            rx.foreach(
                                WatchPageState.watchlist,
                                lambda symbol: eyebrow_badge(
                                    symbol,
                                    color=TRADING_COLORS["text"],
                                    background="rgba(73, 167, 255, 0.08)",
                                ),
                            ),
                            gap="2",
                            wrap="wrap",
                            width="100%",
                        ),
                        spacing="3",
                        align="stretch",
                    ),
                    width="100%",
                    style={
                        "background": "rgba(12, 18, 27, 0.68)",
                        "border": f"1px solid {TRADING_COLORS['border']}",
                    },
                ),
                rx.card(
                    rx.vstack(
                        rx.text("指标开关", size="2", weight="bold"),
                        rx.grid(
                            rx.foreach(
                                WatchPageState.indicator_candidates,
                                _indicator_selector,
                            ),
                            columns=rx.breakpoints(initial="1", sm="2"),
                            spacing="3",
                            width="100%",
                        ),
                        spacing="3",
                        align="stretch",
                    ),
                    width="100%",
                    style={
                        "background": "rgba(12, 18, 27, 0.68)",
                        "border": f"1px solid {TRADING_COLORS['border']}",
                    },
                ),
                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),
            padding_top="0.9rem",
            spacing="4",
            align="stretch",
        ),
        data_role="workspace-controls",
        style=diagnostics_panel_style(),
        open=True,
    )


def _diagnostics_panel() -> rx.Component:
    """构造下沉的 diagnostics 区。"""

    return rx.el.details(
        rx.el.summary(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Diagnostics",
                        size="1",
                        weight="bold",
                        style={
                            "color": TRADING_COLORS["text_muted"],
                            "letter_spacing": "0.08em",
                            "text_transform": "uppercase",
                        },
                    ),
                    rx.text("连接与订阅意图", size="3", weight="bold"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.icon("panel_right_open", size=18, color=TRADING_COLORS["text_soft"]),
                width="100%",
                align="center",
                style={"cursor": "pointer", "list_style": "none"},
            ),
        ),
        rx.vstack(
            rx.text(
                "保留联调所需的门面地址、WebSocket 地址与订阅载荷，但默认不常驻首屏。",
                size="2",
                style=muted_text_style(),
            ),
            rx.grid(
                rx.vstack(
                    rx.text("API Base", size="1", style=muted_text_style()),
                    rx.code(WatchPageState.api_base_url, style=subtle_code_style()),
                    rx.text("Bootstrap", size="1", style=muted_text_style()),
                    rx.code(WatchPageState.bootstrap_url, style=subtle_code_style()),
                    spacing="2",
                    align="stretch",
                ),
                rx.vstack(
                    rx.text("Chart WS", size="1", style=muted_text_style()),
                    rx.code(WatchPageState.chart_socket_url, style=subtle_code_style()),
                    rx.text("Quote WS", size="1", style=muted_text_style()),
                    rx.code(WatchPageState.quote_socket_url, style=subtle_code_style()),
                    rx.text("Alert WS", size="1", style=muted_text_style()),
                    rx.code(WatchPageState.alerts_socket_url, style=subtle_code_style()),
                    spacing="2",
                    align="stretch",
                ),
                columns=rx.breakpoints(initial="1", lg="2"),
                spacing="4",
                width="100%",
            ),
            rx.vstack(
                rx.text("订阅意图", size="1", style=muted_text_style()),
                rx.code(WatchPageState.chart_subscription_payload, style=subtle_code_style()),
                rx.code(WatchPageState.quote_subscription_payload, style=subtle_code_style()),
                rx.code(WatchPageState.alert_subscription_payload, style=subtle_code_style()),
                spacing="2",
                align="stretch",
                width="100%",
            ),
            padding_top="0.9rem",
            spacing="4",
            align="stretch",
        ),
        data_role="workspace-diagnostics",
        style=diagnostics_panel_style(),
    )


def index() -> rx.Component:
    """构建图表优先的完整看盘页面。"""

    return rx.box(
        rx.vstack(
            _command_bar(),
            rx.grid(
                _chart_workspace(),
                indicator_summary_card(),
                columns=rx.breakpoints(initial="1", xl="minmax(0,1fr) 22rem"),
                spacing="5",
                width="100%",
                align="stretch",
            ),
            rx.grid(
                _indicator_configuration_panel(),
                _diagnostics_panel(),
                columns=rx.breakpoints(initial="1", xl="2"),
                spacing="5",
                width="100%",
            ),
            spacing="5",
            align="stretch",
            style=workspace_container_style(),
        ),
        style=shell_box_style(),
    )


app = rx.App()
app.add_page(index, route="/")