"""定义 Reflex 页面层的最小状态边界。

页面层只保留低频交互状态，例如当前标的、周期、指标开关和订阅意图；
高频逐笔、forming bar、实时指标数值等运行态数据必须通过 FastAPI
bootstrap 接口与实时推送通道获取，而不是直接存入 Reflex State。
"""

from __future__ import annotations

from urllib.parse import urlencode

import reflex as rx


class WatchPageState(rx.State):
    """描述看盘页面的低频交互状态。"""

    region: str = "HK"
    code: str = "00700"
    period: str = "1m"
    indicators: list[str] = ["ma5", "ma20", "macd", "rsi14", "boll"]
    watchlist: list[str] = ["HK.00700", "US.AAPL"]
    bootstrap_endpoint: str = "/api/chart/bootstrap"
    chart_socket_url: str = "/ws/chart/session-local"
    quote_socket_url: str = "/ws/quotes/session-local"
    alerts_socket_url: str = "/ws/alerts/session-local"
    chart_subscription_payload: str = '{"action":"subscribe","symbol":"HK.00700","period":"1m"}'
    quote_subscription_payload: str = '{"action":"subscribe","name":"watchlist"}'
    alert_subscription_payload: str = '{"action":"subscribe","name":"default"}'

    @rx.var
    def symbol(self) -> str:
        """返回标准化 symbol。"""

        return f"{self.region}.{self.code}"

    @rx.var
    def bootstrap_url(self) -> str:
        """返回当前页面用于 bootstrap 的请求地址。"""

        query = urlencode(
            {
                "region": self.region,
                "code": self.code,
                "period": self.period,
                "bars": 240,
            }
        )
        return f"{self.bootstrap_endpoint}?{query}"

    @rx.event
    def set_symbol(self, region: str, code: str) -> None:
        """切换当前标的并同步图表订阅意图。"""

        self.region = region
        self.code = code
        self._refresh_chart_subscription_payload()

    @rx.event
    def set_period(self, period: str) -> None:
        """切换图表周期并同步订阅意图。"""

        self.period = period
        self._refresh_chart_subscription_payload()

    @rx.event
    def toggle_indicator(self, indicator: str) -> None:
        """切换指标开关。"""

        if indicator in self.indicators:
            self.indicators = [item for item in self.indicators if item != indicator]
            return
        self.indicators = [*self.indicators, indicator]

    @rx.event
    def set_watchlist(self, symbols: list[str]) -> None:
        """更新页面层自选列表。"""

        self.watchlist = symbols

    def _refresh_chart_subscription_payload(self) -> None:
        """刷新图表订阅消息，确保页面层只保存订阅意图。"""

        self.chart_subscription_payload = (
            f'{{"action":"subscribe","symbol":"{self.symbol}","period":"{self.period}"}}'
        )
