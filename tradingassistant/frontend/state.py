"""State and event wiring for the native terminal workspace."""

from __future__ import annotations

import reflex as rx

from . import charting


class WatchPageState(rx.State):
    """Store user-facing terminal controls and derive all mock workspace views."""

    ticker_input: str = ""
    watchlist: list[str] = charting.DEFAULT_WATCHLIST.copy()
    active_code: str = charting.DEFAULT_WATCHLIST[0]
    active_scale: str = charting.SCALE_OPTIONS[4]
    active_route: str = charting.ROUTE_OPTIONS[0][0]
    active_overlays: list[str] = ["MA", "BOLL", "VWAP"]
    depth_mode: str = charting.DEPTH_MODE_OPTIONS[0][0]
    rail_tab: str = charting.RAIL_TABS[0][0]
    movers_tab: str = charting.MOVERS_TABS[0][0]
    sort_mode: str = "code"

    @rx.var
    def active_model(self) -> dict:
        return charting.build_market_model(self.active_code, self.active_scale)

    @rx.var
    def macro_strip(self) -> list[dict[str, str]]:
        return charting.MACRO_STRIP

    @rx.var
    def quote_strip(self) -> list[dict[str, str]]:
        return charting.build_quote_strip(self.active_model)

    @rx.var
    def watchlist_rows(self) -> list[dict[str, str | bool]]:
        return charting.build_watchlist_rows(
            self.watchlist,
            self.active_code,
            self.active_scale,
            self.sort_mode,
        )

    @rx.var
    def movers_rows(self) -> list[dict[str, str]]:
        return charting.build_movers_rows(self.movers_tab, self.active_scale)

    @rx.var
    def snapshot_cells(self) -> list[dict[str, str]]:
        return charting.build_snapshot_cells(self.active_model)

    @rx.var
    def instrument_metrics(self) -> list[dict[str, str]]:
        return charting.build_instrument_metrics(self.active_model)

    @rx.var
    def chart_legend(self) -> list[dict[str, str]]:
        return charting.build_chart_legend(self.active_model, self.active_overlays)

    @rx.var
    def primary_chart_svg(self) -> str:
        return charting.build_primary_chart_svg(
            self.active_model,
            self.active_overlays,
            self.active_route,
        )

    @rx.var
    def study_cards(self) -> list[dict[str, str]]:
        return charting.build_route_studies(self.active_model, self.active_route)

    @rx.var
    def depth_rows(self) -> list[dict[str, str]]:
        return charting.build_depth_rows(self.active_model, self.depth_mode)

    @rx.var
    def order_book_rows(self) -> list[dict[str, str]]:
        return charting.build_order_book_rows(self.active_model)

    @rx.var
    def analysis_cards(self) -> list[dict[str, str]]:
        return charting.build_analysis_cards(
            self.active_model,
            self.active_route,
            self.active_scale,
            self.active_overlays,
            self.depth_mode,
        )

    @rx.var
    def tape_rows(self) -> list[dict[str, str]]:
        return charting.build_tape_rows(self.active_model)

    @rx.var
    def signal_rows(self) -> list[dict[str, str]]:
        return charting.build_signal_rows()

    @rx.var
    def news_rows(self) -> list[dict[str, str]]:
        return charting.build_news_rows()

    @rx.var
    def sort_button_label(self) -> str:
        return "By Code" if self.sort_mode == "code" else "By Name"

    @rx.var
    def instrument_name(self) -> str:
        return self.active_model["meta"]["name"]

    @rx.var
    def instrument_meta(self) -> str:
        model = self.active_model
        return f"{model['meta']['code']} / {model['meta']['venue']} / {model['meta']['session']}"

    @rx.var
    def last_price_text(self) -> str:
        return charting.format_number(self.active_model["last"])

    @rx.var
    def price_change_text(self) -> str:
        model = self.active_model
        return f"{charting.format_signed(model['change_value'])} / {charting.format_signed(model['change_pct'], 2, '%')}"

    @rx.var
    def price_change_color(self) -> str:
        return self.active_model["change_color"]

    @rx.var
    def chart_title(self) -> str:
        return f"{self.active_model['meta']['code']} / {self.active_route.upper()} / {self.active_scale}"

    @rx.var
    def route_hint(self) -> str:
        return f"{self.active_route.upper()} ROUTE / {self.active_scale}"

    @rx.var
    def study_title(self) -> str:
        return f"{self.active_route.upper()} ROUTE STUDIES"

    @rx.var
    def study_summary(self) -> str:
        return "3 linked indicator panes"

    @rx.var
    def chart_footer_labels(self) -> list[str]:
        return [f"{self.active_scale} {index}" for index in range(1, 7)]

    @rx.var
    def order_book_meta(self) -> str:
        return f"{self.depth_mode.upper()} VIEW / 10 levels"

    @rx.event
    def set_ticker_input(self, value: str) -> None:
        self.ticker_input = value

    @rx.event
    def add_watch_symbol(self) -> None:
        code = charting.normalize_code(self.ticker_input)
        if not code:
            return
        if code not in self.watchlist:
            self.watchlist = [code, *self.watchlist]
        self.active_code = code
        self.ticker_input = ""

    @rx.event
    def select_watch_symbol(self, code: str) -> None:
        self.active_code = code

    @rx.event
    def set_scale(self, scale: str) -> None:
        self.active_scale = scale

    @rx.event
    def set_route(self, route: str) -> None:
        self.active_route = route

    @rx.event
    def toggle_overlay(self, overlay: str) -> None:
        if overlay in self.active_overlays:
            self.active_overlays = [item for item in self.active_overlays if item != overlay]
            return
        self.active_overlays = [*self.active_overlays, overlay]

    @rx.event
    def set_depth_mode(self, mode: str) -> None:
        self.depth_mode = mode

    @rx.event
    def set_rail_tab(self, tab: str) -> None:
        self.rail_tab = tab

    @rx.event
    def set_movers_tab(self, tab: str) -> None:
        self.movers_tab = tab

    @rx.event
    def toggle_sort_mode(self) -> None:
        self.sort_mode = "name" if self.sort_mode == "code" else "code"
