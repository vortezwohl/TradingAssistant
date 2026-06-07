"""定义最小 Reflex 看盘页面骨架。

当前页面主要用于明确前端状态边界与对接路径：
1. 页面通过 bootstrap URL 拉取首屏图表数据；
2. 页面只保存 websocket 订阅意图，而不持有高频行情实体；
3. 指标开关、周期切换与自选列表属于低频页面状态，保留在 Reflex State。
"""

from __future__ import annotations

import reflex as rx

from .state import WatchPageState


def index() -> rx.Component:
    """构建最小看盘页面。"""

    return rx.container(
        rx.heading("TradingAssistant", size="7"),
        rx.text("MEMORY-first market monitor page"),
        rx.hstack(
            rx.badge(WatchPageState.region),
            rx.badge(WatchPageState.code),
            rx.badge(WatchPageState.period),
        ),
        rx.text("Bootstrap URL: ", WatchPageState.bootstrap_url),
        rx.text("Chart socket: ", WatchPageState.chart_socket_url),
        rx.text("Chart subscribe: ", WatchPageState.chart_subscription_payload),
        rx.text("Quote socket: ", WatchPageState.quote_socket_url),
        rx.text("Quote subscribe: ", WatchPageState.quote_subscription_payload),
        rx.text("Alert socket: ", WatchPageState.alerts_socket_url),
        rx.text("Alert subscribe: ", WatchPageState.alert_subscription_payload),
        rx.text(
            "Enabled indicators: ",
            rx.foreach(
                WatchPageState.indicators,
                lambda indicator: rx.badge(indicator),
            ),
        ),
        rx.text(
            "Watchlist: ",
            rx.foreach(
                WatchPageState.watchlist,
                lambda item: rx.badge(item),
            ),
        ),
        spacing="4",
        padding="2rem",
    )


app = rx.App()
app.add_page(index, route="/")
