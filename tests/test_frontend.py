"""验证 Reflex 页面层状态边界。

本文件确保页面层只保留低频交互状态，不直接承载高频逐笔、forming bar
或原始行情流；同时验证 bootstrap 地址和订阅意图由页面层显式维护。
"""

from __future__ import annotations

import unittest

from tradingassistant.frontend.state import WatchPageState


class WatchPageStateTests(unittest.TestCase):
    """验证看盘页面状态边界。"""

    def test_state_keeps_low_frequency_page_fields_only(self) -> None:
        """页面状态应只包含低频配置字段。"""

        field_names = set(WatchPageState.get_fields())
        self.assertIn("region", field_names)
        self.assertIn("code", field_names)
        self.assertIn("period", field_names)
        self.assertIn("indicators", field_names)
        self.assertIn("chart_subscription_payload", field_names)
        self.assertIn("quote_subscription_payload", field_names)
        self.assertNotIn("ticks", field_names)
        self.assertNotIn("bars", field_names)
        self.assertNotIn("raw_market_stream", field_names)

    def test_state_exposes_bootstrap_and_subscription_intents(self) -> None:
        """页面层应暴露 bootstrap 地址与 websocket 订阅意图。"""

        fields = WatchPageState.get_fields()
        self.assertEqual(fields["bootstrap_endpoint"].default, "/api/chart/bootstrap")
        self.assertEqual(fields["chart_socket_url"].default, "/ws/chart/session-local")
        self.assertEqual(fields["quote_socket_url"].default, "/ws/quotes/session-local")
        self.assertEqual(fields["alerts_socket_url"].default, "/ws/alerts/session-local")
        self.assertIn("subscribe", fields["chart_subscription_payload"].default)
        self.assertIn("watchlist", fields["quote_subscription_payload"].default)
        self.assertIn("default", fields["alert_subscription_payload"].default)
        self.assertIn("bootstrap_url", WatchPageState.vars)


if __name__ == "__main__":
    unittest.main()
