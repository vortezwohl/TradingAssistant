"""Regression tests for the Reflex terminal workspace mock frontend."""

from __future__ import annotations

import unittest

from tradingassistant.frontend import charting
from tradingassistant.frontend.app import index
from tradingassistant.frontend.state import WatchPageState
from tradingassistant.frontend.theme import (
    hover_panel_style,
    scroll_region_style,
    shell_style,
    truncated_text_style,
    workspace_style,
)


class WatchPageStateTests(unittest.TestCase):
    """Validate terminal state defaults, vars, and event handlers."""

    def test_state_fields_match_terminal_controls(self) -> None:
        """The page state should expose the expected terminal defaults."""
        fields = WatchPageState.get_fields()
        self.assertEqual(fields["ticker_input"].default, "")
        self.assertEqual(fields["active_code"].default, "HK.00700")
        self.assertEqual(fields["active_scale"].default, "1H")
        self.assertEqual(fields["active_route"].default, "main")
        self.assertEqual(fields["depth_mode"].default, "ladder")
        self.assertEqual(fields["rail_tab"].default, "analysis")
        self.assertEqual(fields["movers_tab"].default, "leaders")
        self.assertEqual(fields["sort_mode"].default, "code")
        self.assertEqual(fields["hover_index"].default, -1)
        self.assertIn("US.NVDA", fields["watchlist"].default_factory())
        self.assertIn("MA", fields["active_overlays"].default_factory())
        self.assertIn("BOLL", fields["active_overlays"].default_factory())
        self.assertIn("VWAP", fields["active_overlays"].default_factory())

    def test_state_exposes_terminal_derived_vars(self) -> None:
        """The page state should expose all chart and hover derived vars."""
        vars_set = set(WatchPageState.vars)
        for name in [
            "active_model",
            "watchlist_rows",
            "movers_rows",
            "snapshot_cells",
            "instrument_metrics",
            "chart_legend",
            "primary_chart_svg",
            "study_cards",
            "depth_rows",
            "order_book_rows",
            "analysis_cards",
            "tape_rows",
            "signal_rows",
            "news_rows",
            "instrument_name",
            "chart_title",
            "order_book_meta",
            "hover_active",
            "active_chart_index",
            "chart_hover_line_left",
            "chart_hover_card_left",
            "chart_hover_card_transform",
            "chart_hover_details",
            "chart_hover_overlay_rows",
            "chart_status_label",
        ]:
            self.assertIn(name, vars_set)

    def test_state_exposes_terminal_event_handlers(self) -> None:
        """The page state should expose all terminal interaction handlers."""
        handlers = WatchPageState.event_handlers
        for name in [
            "set_ticker_input",
            "add_watch_symbol",
            "select_watch_symbol",
            "set_scale",
            "set_route",
            "toggle_overlay",
            "set_depth_mode",
            "set_rail_tab",
            "set_movers_tab",
            "toggle_sort_mode",
            "set_hover_index",
            "clear_hover_index",
        ]:
            self.assertIn(name, handlers)


class ThemeContractTests(unittest.TestCase):
    """Validate terminal shell and dense left-rail styling helpers."""

    def test_shell_and_workspace_disable_page_scroll(self) -> None:
        """The shell should keep global page scrolling disabled."""
        shell = shell_style()
        workspace = workspace_style()
        scroll_region = scroll_region_style()
        self.assertEqual(shell["height"], "100vh")
        self.assertEqual(shell["overflow"], "hidden")
        self.assertEqual(workspace["grid_template_columns"], "260px minmax(0, 1fr) 360px")
        self.assertEqual(workspace["height"], "calc(100vh - 48px)")
        self.assertEqual(workspace["overflow"], "hidden")
        self.assertEqual(scroll_region["overflow_y"], "auto")
        self.assertEqual(scroll_region["overflow_x"], "hidden")

    def test_dense_terminal_styles_preserve_truncation_contract(self) -> None:
        """Dense side-rail text and hover surfaces should use stable overflow rules."""
        shell = shell_style()
        truncated = truncated_text_style()
        hover_panel = hover_panel_style()
        self.assertEqual(truncated["overflow"], "hidden")
        self.assertEqual(truncated["text_overflow"], "ellipsis")
        self.assertEqual(truncated["white_space"], "nowrap")
        self.assertEqual(truncated["box_sizing"], "border-box")
        self.assertEqual(shell["box_sizing"], "border-box")
        self.assertEqual(hover_panel["pointer_events"], "none")
        self.assertEqual(hover_panel["overflow"], "hidden")
        self.assertEqual(hover_panel["box_sizing"], "border-box")


class ChartingContractTests(unittest.TestCase):
    """Validate mock chart builders and hover payload contracts."""

    def test_scale_and_route_options_cover_terminal_contract(self) -> None:
        """The terminal options should still expose the expected scales and routes."""
        self.assertEqual(
            charting.SCALE_OPTIONS,
            ("30S", "1M", "5M", "15M", "1H", "4H", "1D", "1W", "1MO", "1Y"),
        )
        self.assertEqual(
            charting.ROUTE_OPTIONS,
            (
                ("main", "Main"),
                ("momentum", "Momentum"),
                ("trend", "Trend"),
                ("volatility", "Volatility"),
                ("orderflow", "Order Flow"),
                ("micro", "Microstructure"),
            ),
        )
        self.assertEqual(charting.OVERLAY_OPTIONS, ("MA", "EMA", "BOLL", "VWAP"))
        self.assertEqual(charting.RAIL_TABS, (("analysis", "Analysis"), ("tape", "Tape"), ("signals", "Signals"), ("news", "News")))
        self.assertEqual(charting.CHART_POINT_COUNT, 72)

    def test_charting_helpers_cover_hover_contract_and_microstructure(self) -> None:
        """The chart builders should expose hover-ready metadata and route studies."""
        model = charting.build_market_model("US.NVDA", "1D")
        legend = charting.build_chart_legend(model, ["MA", "EMA", "BOLL", "VWAP"], 5)
        labels = [item["label"] for item in legend]
        self.assertIn("MA5", labels)
        self.assertIn("EMA12", labels)
        self.assertIn("BOLL U", labels)
        self.assertIn("VWAP", labels)

        hover_details = charting.build_chart_hover_details(model, ["MA", "VWAP"], "orderflow", 5)
        self.assertEqual(hover_details["route"], "ORDERFLOW")
        self.assertIn("slot", hover_details)
        self.assertIn("open", hover_details)
        self.assertIn("delta", hover_details)
        self.assertIn("route_description", hover_details)

        overlay_rows = charting.build_chart_hover_overlay_rows(model, ["MA", "VWAP"], 5)
        self.assertGreaterEqual(len(overlay_rows), 2)
        self.assertEqual(overlay_rows[0]["label"], "MA5")

        main_svg = charting.build_primary_chart_svg(model, ["MA", "EMA", "BOLL", "VWAP"], "orderflow")
        self.assertIn("<svg", main_svg)
        self.assertIn("path", main_svg)
        self.assertIn("rect", main_svg)

        for route, _ in charting.ROUTE_OPTIONS:
            studies = charting.build_route_studies(model, route, 5, True)
            self.assertEqual(len(studies), 3)
            for card in studies:
                self.assertIn("svg", card)
                self.assertIn("tag", card)
                self.assertIn("foot_left", card)
                self.assertIn("foot_right", card)
                self.assertIn("hover_value", card)
                self.assertIn("display_value", card)
                self.assertIn("display_label", card)

        depth_rows = charting.build_depth_rows(model, "ladder")
        self.assertEqual(len(depth_rows), 10)
        self.assertIn("bid_width", depth_rows[0])
        self.assertIn("ask_width", depth_rows[0])

        book_rows = charting.build_order_book_rows(model)
        self.assertEqual(len(book_rows), 10)
        self.assertIn("spread", book_rows[0])

        analysis_cards = charting.build_analysis_cards(model, "main", "30S", ["MA", "VWAP"], "ladder")
        self.assertEqual(len(analysis_cards), 3)
        self.assertIn("metric_1_label", analysis_cards[0])
        self.assertIn("metric_3_value", analysis_cards[0])


class TerminalRenderingTests(unittest.TestCase):
    """Validate the rendered Reflex page contains key hover and terminal tokens."""

    def test_index_contains_terminal_workspace_structure(self) -> None:
        """The page render should include the updated terminal workspace building blocks."""
        rendered = str(index())
        for token in [
            "TradingAssistant / Terminal",
            "Wall Street Market Workspace",
            "Watchlist",
            "Market Movers",
            "Desk Snapshot",
            "Market Depth",
            "Order Book",
            "Analysis",
            "Tape",
            "Signals",
            "News",
            "260px minmax(0, 1fr) 360px",
            "calc(100vh - 48px)",
            "polygon(100% 0, 100% 100%, 0 100%)",
            "polygon(0 0, 100% 0, 0 100%)",
            "repeat(72, minmax(0, 1fr))",
            "inset 2px 0 0",
            "set_hover_index",
        ]:
            self.assertIn(token, rendered)


if __name__ == "__main__":
    unittest.main()
