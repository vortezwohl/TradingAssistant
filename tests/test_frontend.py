"""验证 Reflex 前端状态与页面结构。"""

from __future__ import annotations

import unittest

from tradingassistant.frontend.app import index
from tradingassistant.frontend.charting import (
    ChartBootstrapPayload,
    ChartIncrementalPayload,
    example_bootstrap_payload,
    example_incremental_payload,
    indicators_json_literal,
)
from tradingassistant.frontend.state import WatchPageState
from tradingassistant.settings import API_BASE_URL


class WatchPageStateTests(unittest.TestCase):
    """验证看盘页状态。"""

    def test_state_keeps_low_frequency_page_fields_only(self) -> None:
        """确认页面状态仅保留低频字段。"""

        field_names = set(WatchPageState.get_fields())
        self.assertIn("api_base_url", field_names)
        self.assertIn("region", field_names)
        self.assertIn("code", field_names)
        self.assertIn("period", field_names)
        self.assertIn("indicators", field_names)
        self.assertIn("watchlist", field_names)
        self.assertIn("chart_subscription_payload", field_names)
        self.assertNotIn("ticks", field_names)
        self.assertNotIn("bars", field_names)
        self.assertNotIn("raw_market_stream", field_names)

    def test_state_exposes_bootstrap_and_subscription_intents(self) -> None:
        """确认 bootstrap 和订阅意图对外暴露。"""

        fields = WatchPageState.get_fields()
        self.assertEqual(fields["bootstrap_endpoint"].default, "/api/chart/bootstrap")
        self.assertEqual(fields["chart_socket_url"].default, "/ws/chart/session-local")
        self.assertEqual(fields["quote_socket_url"].default, "/ws/quotes/session-local")
        self.assertEqual(fields["alerts_socket_url"].default, "/ws/alerts/session-local")
        self.assertIn("subscribe", fields["chart_subscription_payload"].default)
        self.assertIn("watchlist", fields["quote_subscription_payload"].default)
        self.assertIn("default", fields["alert_subscription_payload"].default)
        self.assertIn("bootstrap_url", WatchPageState.vars)
        self.assertIn("indicator_selection_json", WatchPageState.vars)

    def test_state_supports_context_switch_fields(self) -> None:
        """确认默认 API 地址来自统一配置源。"""

        fields = WatchPageState.get_fields()
        self.assertEqual(fields["api_base_url"].default, API_BASE_URL)
        self.assertIn("HK.00700", fields["watchlist"].default_factory())
        self.assertIn("1m", fields["available_periods"].default_factory())
        self.assertIn("ma5", fields["indicator_candidates"].default_factory())


class ChartContractTests(unittest.TestCase):
    """验证图表契约。"""

    def test_bootstrap_contract_roundtrip(self) -> None:
        """bootstrap 契约应可往返序列化。"""

        payload = example_bootstrap_payload()
        rebuilt = ChartBootstrapPayload.from_dict(payload.to_dict())
        self.assertEqual(rebuilt.topic, "chart:HK.00700:1m")
        self.assertEqual(rebuilt.symbol, "HK.00700")
        self.assertEqual(len(rebuilt.bars), 1)
        self.assertIn("values", rebuilt.indicators)

    def test_incremental_contract_roundtrip(self) -> None:
        """增量契约应保留 provisional 语义。"""

        payload = example_incremental_payload()
        rebuilt = ChartIncrementalPayload.from_dict(payload.to_dict())
        self.assertEqual(rebuilt.payload_type, "bar_update")
        self.assertTrue(rebuilt.provisional)
        self.assertEqual(rebuilt.bar["bar_time"], "2026-06-07T09:31:00+00:00")
        self.assertTrue(rebuilt.indicators["provisional"])

    def test_indicator_json_literal_keeps_enabled_order(self) -> None:
        """指标 JSON 应保持开关顺序。"""

        rendered = indicators_json_literal(["ma5", "macd"])
        self.assertEqual(rendered, '{"enabled":["ma5","macd"]}')


class WatchPageRenderingTests(unittest.TestCase):
    """验证页面组件树。"""

    def test_index_contains_chart_runtime_and_controls(self) -> None:
        """页面应包含图表运行时与控件。"""

        rendered = str(index())
        self.assertIn("watch-chart-root", rendered)
        self.assertIn("ECharts", rendered)
        self.assertIn("data-bootstrap-url", rendered)
        self.assertIn("command-bar", rendered)
        self.assertIn("chart-workspace", rendered)
        self.assertIn("summary-rail", rendered)
        self.assertIn("workspace-controls", rendered)
        self.assertIn("workspace-diagnostics", rendered)
        self.assertIn("indicator-status", rendered)
        self.assertIn("RadixThemesSelect.Root", rendered)
        self.assertIn("RadixThemesCheckbox", rendered)


if __name__ == "__main__":
    unittest.main()
