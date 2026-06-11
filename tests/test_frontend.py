"""验证 Reflex 看盘前端的状态边界、图表契约与页面结构。

本文件重点验证：
1. 页面状态只保留低频上下文，不回灌高频 bars 或逐笔流；
2. 图表 bootstrap 与增量更新契约稳定可序列化；
3. 页面组件树已接入浏览器图表容器和上下文切换控件。
"""

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


class WatchPageStateTests(unittest.TestCase):
    """验证看盘页面状态边界。"""

    def test_state_keeps_low_frequency_page_fields_only(self) -> None:
        """页面状态应只包含低频配置字段。"""

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
        self.assertIn("indicator_selection_json", WatchPageState.vars)

    def test_state_supports_context_switch_fields(self) -> None:
        """页面状态应提供切换图表上下文所需字段。"""

        fields = WatchPageState.get_fields()
        self.assertEqual(fields["api_base_url"].default, "http://127.0.0.1:8000")
        self.assertIn("HK.00700", fields["watchlist"].default_factory())
        self.assertIn("1m", fields["available_periods"].default_factory())
        self.assertIn("ma5", fields["indicator_candidates"].default_factory())


class ChartContractTests(unittest.TestCase):
    """验证图表输入契约。"""

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
        """指标选择 JSON 应维持前端开关顺序。"""

        rendered = indicators_json_literal(["ma5", "macd"])
        self.assertEqual(rendered, '{"enabled":["ma5","macd"]}')


class WatchPageRenderingTests(unittest.TestCase):
    """验证页面组件树已接入图表前端。"""

    def test_index_contains_chart_runtime_and_controls(self) -> None:
        """页面应包含图表容器、ECharts 运行脚本与切换控件。"""

        rendered = str(index())
        self.assertIn("watch-chart-root", rendered)
        self.assertIn("ECharts", rendered)
        self.assertIn("data-bootstrap-url", rendered)
        self.assertIn("indicator-status", rendered)
        self.assertIn("RadixThemesSelect.Root", rendered)
        self.assertIn("RadixThemesCheckbox", rendered)


if __name__ == "__main__":
    unittest.main()
