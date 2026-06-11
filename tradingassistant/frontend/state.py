"""定义 Reflex 看盘页的低频状态与交互事件。

本模块只负责维护页面上下文、控件选择和订阅意图：
1. 标的、周期、指标开关与后端地址留在 Reflex State；
2. 实时 K 线、forming bar 与指标流由浏览器图表组件本地消费；
3. 页面切换通过“重建 bootstrap + 重建订阅”驱动，而不是缓存高频流。
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

import reflex as rx


class WatchPageState(rx.State):
    """描述看盘页面的低频交互状态。"""

    api_base_url: str = "http://127.0.0.1:8000"
    region: str = "HK"
    code: str = "00700"
    period: str = "1m"
    indicators: list[str] = ["ma5", "ma20", "macd", "rsi14"]
    indicator_candidates: list[str] = ["ma5", "ma20", "macd", "rsi14", "boll"]
    available_periods: list[str] = ["1m", "5m", "15m", "30m", "60m"]
    watchlist: list[str] = ["HK.00700", "US.AAPL", "US.NVDA"]
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
    def chart_title(self) -> str:
        """返回页面主标题。"""

        return f"{self.symbol} {self.period} 实时看盘"

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

    @rx.var
    def indicator_selection_json(self) -> str:
        """返回图表组件消费的指标选择文本。"""

        return json.dumps(self.indicators, ensure_ascii=False, separators=(",", ":"))

    @rx.event
    def set_symbol(self, value: str) -> None:
        """根据 watchlist 选择切换当前标的。"""

        try:
            region, code = value.split(".", maxsplit=1)
        except ValueError:
            return
        self.region = region
        self.code = code
        self._refresh_chart_subscription_payload()

    @rx.event
    def set_period(self, period: str) -> None:
        """切换图表周期并同步订阅意图。"""

        self.period = period
        self._refresh_chart_subscription_payload()

    @rx.event
    def set_indicator_enabled(self, indicator: str, checked: bool) -> None:
        """以显式布尔值更新指标开关。"""

        if checked:
            if indicator not in self.indicators:
                self.indicators = [*self.indicators, indicator]
            return
        self.indicators = [item for item in self.indicators if item != indicator]

    @rx.event
    def toggle_indicator(self, indicator: str) -> None:
        """兼容旧测试入口，切换指标开关。"""

        self.set_indicator_enabled(indicator, indicator not in self.indicators)

    @rx.event
    def set_watchlist(self, symbols: list[str]) -> None:
        """更新页面层自选列表。"""

        self.watchlist = symbols

    @rx.event
    def set_api_base_url(self, value: str) -> None:
        """切换前端连接的 FastAPI 门面地址。"""

        self.api_base_url = value.rstrip("/")

    def _refresh_chart_subscription_payload(self) -> None:
        """刷新图表订阅消息，确保页面层只保存订阅意图。"""

        self.chart_subscription_payload = (
            f'{{"action":"subscribe","symbol":"{self.symbol}","period":"{self.period}"}}'
        )
