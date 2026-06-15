
"""?? Reflex ??????????????"""

from __future__ import annotations

import reflex as rx

from . import charting
from .state import WatchPageState
from .theme import (
    TRADING_COLORS,
    column_style,
    compact_label_style,
    hover_panel_style,
    input_style,
    mono_value_style,
    panel_head_style,
    panel_style,
    scroll_region_style,
    shell_style,
    terminal_bar_block_style,
    terminal_bar_style,
    terminal_button_style,
    truncated_text_style,
    workspace_style,
)


def _tone_color_expr(tone: rx.Var[str] | str) -> rx.Var[str] | str:
    return rx.match(
        tone,
        ("up", TRADING_COLORS["green"]),
        ("down", TRADING_COLORS["red"]),
        ("amber", TRADING_COLORS["amber"]),
        ("blue", TRADING_COLORS["blue"]),
        ("cyan", TRADING_COLORS["cyan"]),
        ("yellow", TRADING_COLORS["yellow"]),
        ("soft", TRADING_COLORS["text_soft"]),
        TRADING_COLORS["text"],
    )


def _top_bar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("TradingAssistant / Terminal", style={**compact_label_style(), "color": TRADING_COLORS["amber"], "font_size": "12px", "font_weight": "700"}),
                    rx.text("Wall Street Market Workspace", style={**compact_label_style(), "font_size": "10px"}),
                    spacing="1",
                    align="start",
                ),
                rx.box("LIVE", style={"padding": "3px 6px", "border": "1px solid #22543a", "color": TRADING_COLORS["green"], "font_family": '"Consolas", "SFMono-Regular", "Courier New", monospace', "font_size": "10px", "font_weight": "700", "letter_spacing": "0.06em"}),
                spacing="3",
                align="center",
            ),
            style=terminal_bar_block_style(),
        ),
        rx.box(
            rx.hstack(
                rx.foreach(
                    WatchPageState.macro_strip,
                    lambda item: rx.hstack(
                        rx.text(item["label"], style=compact_label_style()),
                        rx.text(item["value"], style={**mono_value_style(color=_tone_color_expr(item["tone"])), "font_size": "12px"}),
                        spacing="2",
                        align="baseline",
                    ),
                ),
                spacing="4",
                align="center",
                width="100%",
                overflow="hidden",
            ),
            style=terminal_bar_block_style(),
        ),
        rx.box(
            rx.hstack(
                rx.foreach(
                    WatchPageState.quote_strip,
                    lambda item: rx.hstack(
                        rx.text(item["label"], style=compact_label_style()),
                        rx.text(item["value"], style={**mono_value_style(color=_tone_color_expr(item["tone"])), "font_size": "12px"}),
                        spacing="2",
                        align="baseline",
                    ),
                ),
                spacing="4",
                align="center",
                justify="end",
                width="100%",
                overflow="hidden",
            ),
            style=terminal_bar_block_style(border_right=False, justify_end=True),
        ),
        style=terminal_bar_style(),
    )


def _watchlist_row(row: dict[str, rx.Var[str] | str | bool]) -> rx.Component:
    return rx.button(
        rx.grid(
            rx.vstack(
                rx.text(row["code"], style={**mono_value_style(size="12px"), "width": "100%"}),
                rx.text(row["meta"], style=truncated_text_style(size="10px")),
                spacing="0",
                align="start",
                justify="center",
                width="100%",
                min_width="0",
                height="100%",
            ),
            rx.text(row["last"], style={**mono_value_style(size="12px"), "text_align": "right", "width": "100%", "overflow": "hidden", "text_overflow": "ellipsis"}),
            rx.text(row["change"], style={**mono_value_style(color=_tone_color_expr(row["tone"]), size="12px"), "text_align": "right", "width": "100%", "overflow": "hidden", "text_overflow": "ellipsis"}),
            columns="minmax(0, 1fr) 78px 70px",
            gap="8px",
            align="center",
            width="100%",
            min_width="0",
            min_height="40px",
            box_sizing="border-box",
        ),
        on_click=lambda: WatchPageState.select_watch_symbol(row["code"]),
        style={
            "width": "100%",
            "min_width": "0",
            "padding": "7px 10px 7px 12px",
            "border": "0",
            "border_bottom": f"1px solid {TRADING_COLORS['line']}",
            "box_shadow": rx.cond(row["active"], f"inset 2px 0 0 {TRADING_COLORS['amber']}", "inset 0 0 0 transparent"),
            "background": rx.cond(row["active"], "#141c25", "#0b1118"),
            "cursor": "pointer",
            "text_align": "left",
            "border_radius": "0",
            "overflow": "hidden",
            "min_height": "54px",
            "display": "flex",
            "align_items": "center",
            "box_sizing": "border-box",
        },
    )


def _hover_capture_grid() -> rx.Component:
    return rx.grid(
        rx.foreach(
            list(range(charting.CHART_POINT_COUNT)),
            lambda index: rx.box(
                on_mouse_enter=WatchPageState.set_hover_index(index),
                width="100%",
                height="100%",
                display="block",
                min_width="0",
                cursor="crosshair",
            ),
        ),
        grid_template_columns=f"repeat({charting.CHART_POINT_COUNT}, minmax(0, 1fr))",
        grid_template_rows="1fr",
        width="100%",
        height="100%",
        pointer_events="auto",
        position="absolute",
        inset="0",
        z_index="5",
    )


def _chart_hover_panel() -> rx.Component:
    details = WatchPageState.chart_hover_details
    return rx.box(
        rx.hstack(
            rx.text(details["slot"], style={**compact_label_style(), "color": TRADING_COLORS["amber"]}),
            rx.spacer(),
            rx.text(details["change"], style={**mono_value_style(color=_tone_color_expr(details["tone"]), size="11px"), "text_align": "right"}),
            width="100%",
            align="center",
        ),
        rx.grid(
            rx.box(rx.text("Open", style=compact_label_style()), rx.text(details["open"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("High", style=compact_label_style()), rx.text(details["high"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("Low", style=compact_label_style()), rx.text(details["low"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("Close", style=compact_label_style()), rx.text(details["close"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            columns="2",
            gap="8px",
        ),
        rx.grid(
            rx.box(rx.text("Volume", style=compact_label_style()), rx.text(details["volume"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("Delta", style=compact_label_style()), rx.text(details["delta"], style={**mono_value_style(color=_tone_color_expr(details["tone"]), size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("VWAP Gap", style=compact_label_style()), rx.text(details["vwap_gap"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            rx.box(rx.text("Route", style=compact_label_style()), rx.text(details["route"], style={**mono_value_style(size="11px"), "margin_top": "3px"})),
            columns="2",
            gap="8px",
        ),
        rx.box(
            rx.text(details["route_description"], style={**truncated_text_style(size="10px"), "white_space": "normal", "line_height": "1.35"}),
            border_top=f"1px solid {TRADING_COLORS['line']}",
            padding_top="6px",
        ),
        rx.vstack(
            rx.foreach(
                WatchPageState.chart_hover_overlay_rows,
                lambda row: rx.hstack(
                    rx.text(row["label"], style=compact_label_style()),
                    rx.spacer(),
                    rx.text(row["value"], style={**mono_value_style(color=_tone_color_expr(row["tone"]), size="11px")}),
                    width="100%",
                ),
            ),
            spacing="1",
            width="100%",
        ),
        style={**hover_panel_style(), "left": WatchPageState.chart_hover_card_left, "transform": WatchPageState.chart_hover_card_transform},
    )


def _watchlist_panel() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text("Watchlist", style={**compact_label_style(), "font_size": "11px", "color": TRADING_COLORS["text_soft"], "font_weight": "700"}),
            rx.button(WatchPageState.sort_button_label, on_click=WatchPageState.toggle_sort_mode, style={**terminal_button_style(height="30px", padding="0 10px", tone="text_soft"), "color": TRADING_COLORS["text_soft"]}),
            style=panel_head_style(),
        ),
        rx.vstack(
            rx.form(
                rx.hstack(
                    rx.input(name="code", placeholder="Add code: US.NVDA", value=WatchPageState.ticker_input, on_change=WatchPageState.set_ticker_input, style=input_style(), width="100%"),
                    rx.button("Add", type="submit", style={**terminal_button_style(height="30px", padding="0 12px"), "border": f"1px solid {TRADING_COLORS['line_strong']}", "background": TRADING_COLORS['surface_panel_alt'], "color": TRADING_COLORS['amber']}),
                    spacing="2",
                    width="100%",
                ),
                on_submit=lambda _: WatchPageState.add_watch_symbol(),
                width="100%",
                padding="10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
            ),
            rx.box(rx.foreach(WatchPageState.watchlist_rows, _watchlist_row), style=scroll_region_style(), min_width="0", width="100%"),
            spacing="0",
            width="100%",
            height="100%",
        ),
        style=panel_style(),
    )


def _movers_panel() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text("Market Movers", style={**compact_label_style(), "font_size": "11px", "color": TRADING_COLORS["text_soft"], "font_weight": "700"}),
            rx.hstack(
                rx.foreach(charting.MOVERS_TABS, lambda item: rx.button(item[1], on_click=lambda: WatchPageState.set_movers_tab(item[0]), style={**terminal_button_style(tone="text_soft"), "border": rx.cond(WatchPageState.movers_tab == item[0], f"1px solid {TRADING_COLORS['line_strong']}", f"1px solid {TRADING_COLORS['line']}"), "background": rx.cond(WatchPageState.movers_tab == item[0], TRADING_COLORS['surface_panel_alt'], TRADING_COLORS['surface_panel']), "color": rx.cond(WatchPageState.movers_tab == item[0], TRADING_COLORS['amber'], TRADING_COLORS['text_soft'])})),
                spacing="1",
            ),
            style=panel_head_style(),
        ),
        rx.box(
            rx.foreach(
                WatchPageState.movers_rows,
                lambda row: rx.grid(
                    rx.vstack(
                        rx.text(row["code"], style={**mono_value_style(size="12px"), "width": "100%"}),
                        rx.text(row["name"], style=truncated_text_style(size="10px")),
                        spacing="0",
                        align="start",
                        justify="center",
                        width="100%",
                        min_width="0",
                        height="100%",
                    ),
                    rx.text(row["last"], style={**mono_value_style(size="12px"), "text_align": "right", "width": "100%", "overflow": "hidden", "text_overflow": "ellipsis"}),
                    rx.text(row["change"], style={**mono_value_style(color=_tone_color_expr(row["tone"]), size="12px"), "text_align": "right", "width": "100%", "overflow": "hidden", "text_overflow": "ellipsis"}),
                    columns="minmax(0, 1fr) 74px 76px",
                    gap="8px",
                    align="center",
                    padding="7px 10px 7px 12px",
                    border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    background="#0b1118",
                    min_width="0",
                    overflow="hidden",
                    min_height="54px",
                    box_sizing="border-box",
                ),
            ),
            style=scroll_region_style(),
        ),
        style=panel_style(),
    )


def _snapshot_panel() -> rx.Component:
    return rx.box(
        rx.box(rx.text("Desk Snapshot", style={**compact_label_style(), "font_size": "11px", "color": TRADING_COLORS["text_soft"], "font_weight": "700"}), rx.text("Cross Asset Pulse", style=compact_label_style()), style=panel_head_style()),
        rx.grid(
            rx.foreach(
                WatchPageState.snapshot_cells,
                lambda cell: rx.box(
                    rx.text(cell["label"], style=truncated_text_style(size="10px", color=TRADING_COLORS["text_dim"])),
                    rx.text(cell["value"], style={**mono_value_style(size="16px"), "margin_top": "6px", "width": "100%", "overflow": "hidden", "text_overflow": "ellipsis"}),
                    rx.text(cell["sub"], style={**truncated_text_style(size="10px", color=TRADING_COLORS["text_soft"]), "margin_top": "5px"}),
                    padding="10px",
                    border_right=f"1px solid {TRADING_COLORS['line']}",
                    border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    background="#0b1016",
                    min_width="0",
                    overflow="hidden",
                    display="flex",
                    flex_direction="column",
                    justify_content="center",
                    box_sizing="border-box",
                ),
            ),
            columns="2",
            rows="2",
            height="100%",
        ),
        style=panel_style(rows="36px minmax(0, 1fr)", border_bottom=False),
    )


def _left_column() -> rx.Component:
    return rx.box(_watchlist_panel(), _movers_panel(), _snapshot_panel(), style=column_style(rows="minmax(0, 1.12fr) minmax(0, 0.9fr) 214px", background=TRADING_COLORS["surface_alt"]))


def _instrument_strip() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.vstack(rx.heading(WatchPageState.instrument_name, size="6", style={"font_size": "25px", "line_height": "1", "letter_spacing": "0.03em"}), rx.text(WatchPageState.instrument_meta, style={**compact_label_style(), "font_size": "11px", "margin_top": "7px", "color": TRADING_COLORS["text_soft"]}), spacing="1", align="start", min_width="0"),
                rx.hstack(rx.text(WatchPageState.last_price_text, style={**mono_value_style(color=WatchPageState.price_change_color, size="30px"), "letter_spacing": "0.02em"}), rx.text(WatchPageState.price_change_text, style={**mono_value_style(color=WatchPageState.price_change_color, size="14px")}), spacing="3", align="baseline"),
                spacing="4",
                align="end",
                min_width="0",
            ),
            rx.grid(rx.foreach(WatchPageState.instrument_metrics, lambda metric: rx.box(rx.text(metric["label"], style=compact_label_style()), rx.text(metric["value"], style={**mono_value_style(size="13px"), "margin_top": "6px"}), padding="7px 10px", border_left=f"1px solid {TRADING_COLORS['line']}")), columns="6", width="520px"),
            width="100%",
            justify="between",
            align="end",
            spacing="3",
        ),
        padding="10px 14px",
        border_bottom=f"1px solid {TRADING_COLORS['line']}",
        background="#090d12",
    )


def _control_row(items: list[tuple[str, str]], active_value: rx.Var[str], on_click) -> rx.Component:
    return rx.hstack(rx.foreach(items, lambda item: rx.button(item[1], on_click=lambda: on_click(item[0]), style={**terminal_button_style(tone="text_soft"), "border": rx.cond(active_value == item[0], f"1px solid {TRADING_COLORS['line_strong']}", f"1px solid {TRADING_COLORS['line']}"), "background": rx.cond(active_value == item[0], TRADING_COLORS['surface_panel_alt'], TRADING_COLORS['surface_panel']), "color": rx.cond(active_value == item[0], TRADING_COLORS['amber'], TRADING_COLORS['text_soft'])})), spacing="1", align="center", overflow_x="auto", width="100%")


def _overlay_row() -> rx.Component:
    return rx.hstack(rx.foreach([(item, item) for item in charting.OVERLAY_OPTIONS], lambda item: rx.button(item[1], on_click=lambda: WatchPageState.toggle_overlay(item[0]), style={**terminal_button_style(tone="text_soft"), "border": rx.cond(WatchPageState.active_overlays.contains(item[0]), f"1px solid {TRADING_COLORS['line_strong']}", f"1px solid {TRADING_COLORS['line']}"), "background": rx.cond(WatchPageState.active_overlays.contains(item[0]), TRADING_COLORS['surface_panel_alt'], TRADING_COLORS['surface_panel']), "color": rx.cond(WatchPageState.active_overlays.contains(item[0]), TRADING_COLORS['amber'], TRADING_COLORS['text_soft'])})), spacing="1", align="center", overflow_x="auto", width="100%")


def _chart_stage() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.text(WatchPageState.chart_title, style={**compact_label_style(), "font_size": "10px", "color": TRADING_COLORS["text_soft"]}),
                rx.text(WatchPageState.chart_status_label, style={**compact_label_style(), "color": TRADING_COLORS["amber"]}),
                rx.spacer(),
                rx.hstack(
                    rx.foreach(
                        WatchPageState.chart_legend,
                        lambda item: rx.text(f"{item['label']} {item['value']}", style={**mono_value_style(color=_tone_color_expr(item["tone"]), size="11px"), "white_space": "nowrap"}),
                    ),
                    spacing="3",
                    overflow_x="auto",
                    max_width="68%",
                ),
                width="100%",
                align="center",
            ),
            padding="0 12px",
            height="34px",
            border_bottom=f"1px solid {TRADING_COLORS['line']}",
            background="#070b10",
        ),
        rx.box(
            rx.box(rx.html(WatchPageState.primary_chart_svg), width="100%", height="100%", position="absolute", inset="0", z_index="1"),
            rx.box(position="absolute", top="0", bottom="0", left=WatchPageState.chart_hover_line_left, width="1px", background=rx.cond(WatchPageState.hover_active, TRADING_COLORS["amber"], "transparent"), opacity="0.7", z_index="3", transform="translateX(-0.5px)", pointer_events="none"),
            rx.cond(WatchPageState.hover_active, _chart_hover_panel(), rx.fragment()),
            rx.box(_hover_capture_grid(), position="absolute", inset="0", z_index="5", on_mouse_leave=WatchPageState.clear_hover_index),
            width="100%",
            height="100%",
            position="relative",
            overflow="hidden",
            background="linear-gradient(rgba(28, 38, 50, 0.7) 1px, transparent 1px), linear-gradient(90deg, rgba(28, 38, 50, 0.7) 1px, transparent 1px), #06090d",
            background_size="100% 20%, 8.333% 100%, auto",
        ),
        rx.grid(rx.foreach(WatchPageState.chart_footer_labels, lambda label: rx.box(label, display="flex", align_items="center", justify_content="center")), columns="6", padding="0 16px", height="28px", border_top=f"1px solid {TRADING_COLORS['line']}", background="#090d12", color=TRADING_COLORS["text_dim"], font_family='"Consolas", "SFMono-Regular", "Courier New", monospace', font_size="11px"),
        style=panel_style(rows="34px minmax(0, 1fr) 28px", background="#070b10"),
    )


def _study_strip() -> rx.Component:
    return rx.box(
        rx.hstack(rx.text(WatchPageState.study_title, style=compact_label_style()), rx.spacer(), rx.text(WatchPageState.study_summary, style=compact_label_style()), width="100%", padding="0 12px", height="32px", border_bottom=f"1px solid {TRADING_COLORS['line']}"),
        rx.grid(
            rx.foreach(
                WatchPageState.study_cards,
                lambda card: rx.box(
                    rx.hstack(
                        rx.text(card["name"], style={**compact_label_style(), "font_size": "11px", "color": TRADING_COLORS["text_soft"]}),
                        rx.spacer(),
                        rx.vstack(
                            rx.text(card["display_value"], style={**mono_value_style(color=_tone_color_expr(card["tone"]), size="12px")}),
                            rx.text(card["display_label"], style=compact_label_style()),
                            spacing="0",
                            align="end",
                        ),
                        width="100%",
                        padding="0 10px",
                        height="34px",
                        border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    ),
                    rx.box(
                        rx.html(card["svg"]),
                        rx.box(position="absolute", top="0", bottom="0", left=WatchPageState.chart_hover_line_left, width="1px", background=rx.cond(WatchPageState.hover_active, TRADING_COLORS["amber"], "transparent"), opacity="0.65", z_index="2", transform="translateX(-0.5px)", pointer_events="none"),
                        width="100%",
                        height="100%",
                        position="relative",
                        background="linear-gradient(rgba(28, 38, 50, 0.55) 1px, transparent 1px), linear-gradient(90deg, rgba(28, 38, 50, 0.55) 1px, transparent 1px)",
                        background_size="100% 25%, 20% 100%",
                        overflow="hidden",
                    ),
                    rx.grid(
                        rx.box(card["foot_left"], padding="0 10px", display="flex", align_items="center", border_right=f"1px solid {TRADING_COLORS['line']}", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.06em", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                        rx.box(card["foot_right"], padding="0 10px", display="flex", align_items="center", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.06em", overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                        columns="2",
                        height="44px",
                        border_top=f"1px solid {TRADING_COLORS['line']}",
                    ),
                    style=panel_style(rows="34px minmax(0, 1fr) 44px", background=TRADING_COLORS["surface_panel_alt"], border_bottom=False),
                ),
            ),
            columns="3",
            height="100%",
        ),
        style=panel_style(rows="32px minmax(0, 1fr)", background="#091017", border_bottom=False),
    )


def _center_column() -> rx.Component:
    return rx.box(
        _instrument_strip(),
        rx.box(
            _control_row(
                [(item, item) for item in charting.SCALE_OPTIONS],
                WatchPageState.active_scale,
                WatchPageState.set_scale,
            ),
            rx.spacer(),
            _overlay_row(),
            display="flex",
            align_items="center",
            gap="12px",
            padding="0 12px",
            height="40px",
            border_bottom=f"1px solid {TRADING_COLORS['line']}",
            background=TRADING_COLORS["surface_alt"],
        ),
        rx.box(
            _control_row(
                list(charting.ROUTE_OPTIONS),
                WatchPageState.active_route,
                WatchPageState.set_route,
            ),
            rx.spacer(),
            rx.text(WatchPageState.route_hint, style=compact_label_style()),
            display="flex",
            align_items="center",
            gap="12px",
            padding="0 12px",
            height="40px",
            border_bottom=f"1px solid {TRADING_COLORS['line']}",
            background="#0b1016",
        ),
        _chart_stage(),
        _study_strip(),
        style=column_style(
            rows="92px 40px 40px minmax(0, 1fr) 250px",
            background="#060a0e",
        ),
    )


def _depth_panel() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(
                "Market Depth",
                style={
                    **compact_label_style(),
                    "font_size": "11px",
                    "color": TRADING_COLORS["text_soft"],
                    "font_weight": "700",
                },
            ),
            rx.hstack(
                rx.foreach(
                    charting.DEPTH_MODE_OPTIONS,
                    lambda item: rx.button(
                        item[1],
                        on_click=lambda: WatchPageState.set_depth_mode(item[0]),
                        style={**terminal_button_style(tone="text_soft"), "border": rx.cond(WatchPageState.depth_mode == item[0], f"1px solid {TRADING_COLORS['line_strong']}", f"1px solid {TRADING_COLORS['line']}"), "background": rx.cond(WatchPageState.depth_mode == item[0], TRADING_COLORS['surface_panel_alt'], TRADING_COLORS['surface_panel']), "color": rx.cond(WatchPageState.depth_mode == item[0], TRADING_COLORS['amber'], TRADING_COLORS['text_soft'])},
                    ),
                ),
                spacing="1",
            ),
            style=panel_head_style(),
        ),
        rx.box(
            rx.grid(
                rx.box(
                    "Bid Size",
                    padding="0 10px",
                    border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    background="#081018",
                    color=TRADING_COLORS["text_dim"],
                    font_size="10px",
                    text_transform="uppercase",
                    letter_spacing="0.08em",
                    display="flex",
                    align_items="center",
                ),
                rx.box(
                    "Price",
                    padding="0 10px",
                    border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    background="#081018",
                    color=TRADING_COLORS["text_dim"],
                    font_size="10px",
                    text_transform="uppercase",
                    letter_spacing="0.08em",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.box(
                    "Ask Size",
                    padding="0 10px",
                    border_bottom=f"1px solid {TRADING_COLORS['line']}",
                    background="#081018",
                    color=TRADING_COLORS["text_dim"],
                    font_size="10px",
                    text_transform="uppercase",
                    letter_spacing="0.08em",
                    display="flex",
                    align_items="center",
                ),
                columns="1fr 62px 1fr",
                width="100%",
            ),
            rx.box(
                rx.foreach(
                    WatchPageState.depth_rows,
                    lambda row: rx.grid(
                        rx.box(
                            rx.box(
                                position="absolute",
                                top="3px",
                                bottom="3px",
                                right="0",
                                width=row["bid_width"],
                                background=f"linear-gradient(90deg, transparent, {TRADING_COLORS['green']})",
                                opacity="0.18",
                                clip_path="polygon(100% 0, 100% 100%, 0 100%)",
                            ),
                            rx.text(
                                row["bid_text"],
                                style={
                                    **mono_value_style(
                                        color=TRADING_COLORS["green"],
                                        size="11px",
                                    ),
                                    "position": "relative",
                                    "z_index": "1",
                                    "width": "100%",
                                    "text_align": "right",
                                },
                            ),
                            position="relative",
                            padding="0 10px",
                            border_bottom=f"1px solid {TRADING_COLORS['line']}",
                            height="24px",
                            display="flex",
                            align_items="center",
                            overflow="hidden",
                        ),
                        rx.box(
                            row["price"],
                            display="flex",
                            align_items="center",
                            justify_content="center",
                            padding="0 10px",
                            border_bottom=f"1px solid {TRADING_COLORS['line']}",
                            background="#081018",
                            color=TRADING_COLORS["text_soft"],
                            font_family='"Consolas", "SFMono-Regular", "Courier New", monospace',
                            font_size="11px",
                            height="24px",
                        ),
                        rx.box(
                            rx.box(
                                position="absolute",
                                top="3px",
                                bottom="3px",
                                left="0",
                                width=row["ask_width"],
                                background=f"linear-gradient(90deg, {TRADING_COLORS['red']}, transparent)",
                                opacity="0.18",
                                clip_path="polygon(0 0, 100% 0, 0 100%)",
                            ),
                            rx.text(
                                row["ask_text"],
                                style={
                                    **mono_value_style(
                                        color=TRADING_COLORS["red"],
                                        size="11px",
                                    ),
                                    "position": "relative",
                                    "z_index": "1",
                                    "width": "100%",
                                    "text_align": "left",
                                },
                            ),
                            position="relative",
                            padding="0 10px",
                            border_bottom=f"1px solid {TRADING_COLORS['line']}",
                            height="24px",
                            display="flex",
                            align_items="center",
                            overflow="hidden",
                        ),
                        columns="1fr 62px 1fr",
                        width="100%",
                    ),
                ),
                style=scroll_region_style(),
            ),
            display="grid",
            grid_template_rows="24px minmax(0, 1fr)",
            min_height="0",
        ),
        style=panel_style(
            rows="36px minmax(0, 1fr)",
            background=TRADING_COLORS["surface"],
        ),
    )


def _order_book_panel() -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(
                "Order Book",
                style={
                    **compact_label_style(),
                    "font_size": "11px",
                    "color": TRADING_COLORS["text_soft"],
                    "font_weight": "700",
                },
            ),
            rx.text(WatchPageState.order_book_meta, style=compact_label_style()),
            style=panel_head_style(),
        ),
        rx.box(
            rx.grid(
                rx.box("Ask Px", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.08em", text_align="right"),
                rx.box("Ask Sz", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.08em", text_align="right"),
                rx.box("Spread", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.08em", text_align="center"),
                rx.box("Bid Sz", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.08em", text_align="right"),
                rx.box("Bid Px", color=TRADING_COLORS["text_dim"], font_size="10px", text_transform="uppercase", letter_spacing="0.08em", text_align="right"),
                columns="76px 72px 1fr 72px 76px",
                gap="8px",
                align="center",
                padding="6px 10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
                background="#081018",
                font_family='"Consolas", "SFMono-Regular", "Courier New", monospace',
            ),
            rx.box(
                rx.foreach(
                    WatchPageState.order_book_rows,
                    lambda row: rx.grid(
                        rx.text(row["ask_price"], style={**mono_value_style(color=TRADING_COLORS["red"], size="11px"), "text_align": "right"}),
                        rx.text(row["ask_size"], style={**mono_value_style(color=TRADING_COLORS["red"], size="11px"), "text_align": "right"}),
                        rx.text(row["spread"], style={**mono_value_style(color=TRADING_COLORS["text_soft"], size="11px"), "text_align": "center"}),
                        rx.text(row["bid_size"], style={**mono_value_style(color=TRADING_COLORS["green"], size="11px"), "text_align": "right"}),
                        rx.text(row["bid_price"], style={**mono_value_style(color=TRADING_COLORS["green"], size="11px"), "text_align": "right"}),
                        columns="76px 72px 1fr 72px 76px",
                        gap="8px",
                        align="center",
                        padding="6px 10px",
                        border_bottom=f"1px solid {TRADING_COLORS['line']}",
                        font_family='"Consolas", "SFMono-Regular", "Courier New", monospace',
                    ),
                ),
                style=scroll_region_style(),
            ),
            display="grid",
            grid_template_rows="36px minmax(0, 1fr)",
            min_height="0",
        ),
        style=panel_style(
            rows="36px minmax(0, 1fr)",
            background=TRADING_COLORS["surface"],
        ),
    )


def _analysis_tab_panel() -> rx.Component:
    return rx.box(
        rx.foreach(
            WatchPageState.analysis_cards,
            lambda card: rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.text(card["title"], style={**compact_label_style(), "font_size": "12px", "color": TRADING_COLORS["text"], "font_weight": "700"}),
                        rx.text(card["subtitle"], style={**compact_label_style(), "font_size": "10px"}),
                        spacing="1",
                        align="start",
                        min_width="0",
                    ),
                    rx.spacer(),
                    rx.box(card["stamp"], padding="2px 6px", border=f"1px solid {TRADING_COLORS['line_strong']}", color=TRADING_COLORS["amber"], font_family='"Consolas", "SFMono-Regular", "Courier New", monospace', font_size="10px", font_weight="700", text_transform="uppercase", letter_spacing="0.06em"),
                    width="100%",
                    align="start",
                ),
                rx.text(card["body"], color=TRADING_COLORS["text_soft"], font_size="11px", line_height="1.55"),
                rx.grid(
                    rx.box(
                        rx.text(card["metric_1_label"], style={**compact_label_style(), "font_size": "9px"}),
                        rx.text(card["metric_1_value"], style={**mono_value_style(size="11px"), "margin_top": "4px"}),
                        padding="6px 8px",
                        border_right=f"1px solid {TRADING_COLORS['line']}",
                        background="#081018",
                    ),
                    rx.box(
                        rx.text(card["metric_2_label"], style={**compact_label_style(), "font_size": "9px"}),
                        rx.text(card["metric_2_value"], style={**mono_value_style(size="11px"), "margin_top": "4px"}),
                        padding="6px 8px",
                        border_right=f"1px solid {TRADING_COLORS['line']}",
                        background="#081018",
                    ),
                    rx.box(
                        rx.text(card["metric_3_label"], style={**compact_label_style(), "font_size": "9px"}),
                        rx.text(card["metric_3_value"], style={**mono_value_style(size="11px"), "margin_top": "4px"}),
                        padding="6px 8px",
                        background="#081018",
                    ),
                    columns="3",
                    border=f"1px solid {TRADING_COLORS['line']}",
                ),
                padding="10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
                background=TRADING_COLORS["surface_panel_alt"],
                display="grid",
                gap="10px",
            ),
        ),
        style=scroll_region_style(),
    )


def _tape_tab_panel() -> rx.Component:
    return rx.box(
        rx.foreach(
            WatchPageState.tape_rows,
            lambda row: rx.grid(
                rx.text(row["price"], style={**mono_value_style(color=_tone_color_expr(row["tone"]), size="11px")}),
                rx.text(row["size"], style={**mono_value_style(size="11px"), "text_align": "right"}),
                rx.text(row["time"], style={**mono_value_style(color=TRADING_COLORS["text_soft"], size="11px"), "text_align": "center"}),
                rx.text(row["side"], style={**mono_value_style(color=_tone_color_expr(row["tone"]), size="11px"), "text_align": "right"}),
                columns="62px 76px 1fr 54px",
                gap="8px",
                align="center",
                padding="6px 10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
                font_family='"Consolas", "SFMono-Regular", "Courier New", monospace',
            ),
        ),
        style=scroll_region_style(),
    )


def _signal_tab_panel() -> rx.Component:
    return rx.box(
        rx.foreach(
            WatchPageState.signal_rows,
            lambda row: rx.box(
                rx.text(row["title"], style={**compact_label_style(), "font_size": "12px", "color": TRADING_COLORS["text"], "font_weight": "700"}),
                rx.text(row["body"], style={**compact_label_style(), "font_size": "10px", "margin_top": "4px", "line_height": "1.45"}),
                padding="10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
                background="#0b1118",
            ),
        ),
        style=scroll_region_style(),
    )


def _news_tab_panel() -> rx.Component:
    return rx.box(
        rx.foreach(
            WatchPageState.news_rows,
            lambda row: rx.box(
                rx.text(row["title"], style={**compact_label_style(), "font_size": "12px", "color": TRADING_COLORS["text"], "font_weight": "700"}),
                rx.text(row["body"], style={**compact_label_style(), "font_size": "10px", "margin_top": "4px", "line_height": "1.45"}),
                padding="10px",
                border_bottom=f"1px solid {TRADING_COLORS['line']}",
                background="#0b1118",
            ),
        ),
        style=scroll_region_style(),
    )


def _rail_panel() -> rx.Component:
    return rx.cond(
        WatchPageState.rail_tab == "analysis",
        _analysis_tab_panel(),
        rx.cond(
            WatchPageState.rail_tab == "tape",
            _tape_tab_panel(),
            rx.cond(
                WatchPageState.rail_tab == "signals",
                _signal_tab_panel(),
                _news_tab_panel(),
            ),
        ),
    )


def _right_column() -> rx.Component:
    return rx.box(
        _depth_panel(),
        _order_book_panel(),
        rx.box(
            rx.box(
                rx.text("Terminal Rail", style={**compact_label_style(), "font_size": "11px", "color": TRADING_COLORS["text_soft"], "font_weight": "700"}),
                rx.hstack(
                    rx.foreach(
                        charting.RAIL_TABS,
                        lambda item: rx.button(item[1], on_click=lambda: WatchPageState.set_rail_tab(item[0]), style={**terminal_button_style(tone="text_soft"), "border": rx.cond(WatchPageState.rail_tab == item[0], f"1px solid {TRADING_COLORS['line_strong']}", f"1px solid {TRADING_COLORS['line']}"), "background": rx.cond(WatchPageState.rail_tab == item[0], TRADING_COLORS['surface_panel_alt'], TRADING_COLORS['surface_panel']), "color": rx.cond(WatchPageState.rail_tab == item[0], TRADING_COLORS['amber'], TRADING_COLORS['text_soft'])}),
                    ),
                    spacing="1",
                ),
                style=panel_head_style(),
            ),
            _rail_panel(),
            style=panel_style(rows="36px minmax(0, 1fr)", background=TRADING_COLORS["surface"], border_bottom=False),
        ),
        style=column_style(rows="318px minmax(0, 1fr) 232px", background=TRADING_COLORS["surface"], border_right=False),
    )


def index() -> rx.Component:
    """???????????????"""
    return rx.box(
        _top_bar(),
        rx.box(_left_column(), _center_column(), _right_column(), style=workspace_style()),
        style=shell_style(),
    )


app = rx.App()
app.add_page(index, route="/")
