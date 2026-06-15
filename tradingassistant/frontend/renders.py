"""?????????SVG ??????????????????????????"""

from __future__ import annotations

import math
from typing import Any

from .models import _build_overlay_legend_models
from .utils import (
    _clamp_chart_index,
    _line_path,
    compact_volume,
    format_number,
    format_signed,
    tone_from_number,
)

SCALE_OPTIONS: tuple[str, ...] = (
    "30S",
    "1M",
    "5M",
    "15M",
    "1H",
    "4H",
    "1D",
    "1W",
    "1MO",
    "1Y",
)

OVERLAY_OPTIONS: tuple[str, ...] = ("MA", "EMA", "BOLL", "VWAP")

ROUTE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("main", "Main"),
    ("momentum", "Momentum"),
    ("trend", "Trend"),
    ("volatility", "Volatility"),
    ("orderflow", "Order Flow"),
    ("micro", "Microstructure"),
)

DEPTH_MODE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("ladder", "Ladder"),
    ("profile", "Profile"),
    ("imbalance", "Imbalance"),
)

RAIL_TABS: tuple[tuple[str, str], ...] = (
    ("analysis", "Analysis"),
    ("tape", "Tape"),
    ("signals", "Signals"),
    ("news", "News"),
)

MOVERS_TABS: tuple[tuple[str, str], ...] = (
    ("leaders", "Leaders"),
    ("laggards", "Laggards"),
)

CHART_POINT_COUNT = 72
PRIMARY_CHART_WIDTH = 1000.0
PRIMARY_CHART_HEIGHT = 420.0
STUDY_CHART_WIDTH = 320.0
STUDY_CHART_HEIGHT = 130.0

DEFAULT_WATCHLIST: list[str] = [
    "HK.00700",
    "US.NVDA",
    "US.AAPL",
    "US.MSFT",
    "US.AMZN",
    "US.TSLA",
]

UNIVERSE_CODES: list[str] = [
    "HK.00700",
    "US.NVDA",
    "US.AAPL",
    "US.MSFT",
    "US.AMZN",
    "US.TSLA",
    "US.META",
    "US.AVGO",
    "US.GOOGL",
    "US.AMD",
    "US.PLTR",
    "US.CRM",
]

MACRO_STRIP: list[dict[str, str]] = [
    {"label": "UST10Y", "value": "4.21", "tone": "down"},
    {"label": "DXY", "value": "104.18", "tone": "amber"},
    {"label": "WTI", "value": "78.44", "tone": "up"},
    {"label": "Gold", "value": "2358.6", "tone": "amber"},
    {"label": "VIX", "value": "15.92", "tone": "soft"},
]

SYMBOL_PROFILES: dict[str, dict[str, str]] = {
    "HK.00700": {
        "name": "Tencent Holdings",
        "venue": "HKEX",
        "sector": "Internet Platform",
        "session": "Asia Session / Cash",
        "currency": "HKD",
    },
    "US.NVDA": {
        "name": "NVIDIA Corp",
        "venue": "NASDAQ",
        "sector": "Semiconductors",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.AAPL": {
        "name": "Apple Inc",
        "venue": "NASDAQ",
        "sector": "Consumer Technology",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.MSFT": {
        "name": "Microsoft Corp",
        "venue": "NASDAQ",
        "sector": "Software",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.AMZN": {
        "name": "Amazon.com Inc",
        "venue": "NASDAQ",
        "sector": "E-Commerce",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.TSLA": {
        "name": "Tesla Inc",
        "venue": "NASDAQ",
        "sector": "EV / Auto",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.META": {
        "name": "Meta Platforms",
        "venue": "NASDAQ",
        "sector": "Internet Ads",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.AVGO": {
        "name": "Broadcom Inc",
        "venue": "NASDAQ",
        "sector": "Semiconductors",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.GOOGL": {
        "name": "Alphabet Inc",
        "venue": "NASDAQ",
        "sector": "Internet Services",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.AMD": {
        "name": "Advanced Micro Devices",
        "venue": "NASDAQ",
        "sector": "Semiconductors",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.PLTR": {
        "name": "Palantir Technologies",
        "venue": "NYSE",
        "sector": "Data Analytics",
        "session": "US Session / Core",
        "currency": "USD",
    },
    "US.CRM": {
        "name": "Salesforce Inc",
        "venue": "NYSE",
        "sector": "Enterprise Software",
        "session": "US Session / Core",
        "currency": "USD",
    },
}

ROUTE_DESCRIPTIONS: dict[str, str] = {
    "main": "Price structure with overlays and participation context",
    "momentum": "MACD, RSI and impulse spread for timing reads",
    "trend": "Slope, spread and persistence across moving averages",
    "volatility": "ATR, range expansion and band-width state",
    "orderflow": "Delta, OBV and participation pressure proxies",
    "micro": "Micro swings, queue pressure and spread behavior",
}

TONE_COLORS = {
    "up": "#42d48f",
    "down": "#ff6f61",
    "amber": "#ffb347",
    "blue": "#6aa7ff",
    "soft": "#9da9b5",
    "flat": "#e2e8ef",
    "cyan": "#6fd4e6",
    "yellow": "#d7dd63",
}


def build_chart_legend(
    active_model: dict[str, Any],
    overlays: list[str],
    index: int | None = None,
) -> list[dict[str, str]]:
    """Build legend items for the main chart stage."""

    candles = active_model["candles"]
    active_index = _clamp_chart_index(index, len(candles))
    active_candle = candles[active_index]
    previous_close = (
        active_model["prev_close"]
        if active_index == 0
        else candles[active_index - 1]["close"]
    )
    legend: list[dict[str, str]] = [
        {
            "label": active_model["meta"]["code"],
            "value": format_number(active_candle["close"]),
            "tone": tone_from_number(active_candle["close"] - previous_close),
        }
    ]
    for item in _build_overlay_legend_models(active_model, overlays):
        series_index = _clamp_chart_index(active_index, len(item["series"]))
        legend.append(
            {
                "label": item["label"],
                "value": format_number(item["series"][series_index]),
                "tone": item["tone"],
            }
        )
    return legend


def build_chart_hover_overlay_rows(
    active_model: dict[str, Any],
    overlays: list[str],
    index: int | None,
) -> list[dict[str, str]]:
    """Build overlay readouts for the active chart index."""

    active_index = _clamp_chart_index(index, len(active_model["candles"]))
    rows: list[dict[str, str]] = []
    for item in _build_overlay_legend_models(active_model, overlays):
        series_index = _clamp_chart_index(active_index, len(item["series"]))
        rows.append(
            {
                "label": item["label"],
                "value": format_number(item["series"][series_index]),
                "tone": item["tone"],
            }
        )
    return rows


def build_chart_hover_details(
    active_model: dict[str, Any],
    overlays: list[str],
    route: str,
    index: int | None,
) -> dict[str, str]:
    """Build the primary chart hover card payload for one chart index."""

    candles = active_model["candles"]
    analytics = active_model["analytics"]
    active_index = _clamp_chart_index(index, len(candles))
    candle = candles[active_index]
    previous_close = (
        active_model["prev_close"]
        if active_index == 0
        else candles[active_index - 1]["close"]
    )
    price_change = candle["close"] - previous_close
    price_change_pct = (price_change / previous_close) * 100 if previous_close else 0.0
    vwap_gap = (
        (candle["close"] - analytics["vwap"][active_index])
        / analytics["vwap"][active_index]
    ) * 100
    overlay_count = str(len(_build_overlay_legend_models(active_model, overlays)))
    return {
        "slot": f"{active_model['scale']} BAR {active_index + 1:02d}/{len(candles):02d}",
        "price": format_number(candle["close"]),
        "change": format_signed(price_change_pct, 2, "%"),
        "open": format_number(candle["open"]),
        "high": format_number(candle["high"]),
        "low": format_number(candle["low"]),
        "close": format_number(candle["close"]),
        "volume": compact_volume(candle["volume"]),
        "turnover": compact_volume(candle["turnover"]),
        "delta": compact_volume(candle["delta"]),
        "vwap_gap": format_signed(vwap_gap, 2, "%"),
        "route": route.upper(),
        "route_description": ROUTE_DESCRIPTIONS[route],
        "overlay_count": overlay_count,
        "tone": tone_from_number(price_change),
    }


def build_primary_chart_svg(
    active_model: dict[str, Any], overlays: list[str], route: str
) -> str:
    """Build the primary chart SVG for the center chart stage."""

    width = PRIMARY_CHART_WIDTH
    height = PRIMARY_CHART_HEIGHT
    candles = active_model["candles"]
    analytics = active_model["analytics"]
    values = list(analytics["highs"]) + list(analytics["lows"])
    if "MA" in overlays:
        values.extend(analytics["ma5"] + analytics["ma20"] + analytics["ma60"])
    if "EMA" in overlays:
        values.extend(analytics["ema12"] + analytics["ema26"])
    if "BOLL" in overlays:
        values.extend(analytics["boll_upper"] + analytics["boll_lower"])
    if "VWAP" in overlays:
        values.extend(analytics["vwap"])

    minimum = min(values)
    maximum = max(values)
    span = max(maximum - minimum, 0.0001)
    candle_width = width / max(len(candles), 1)

    def to_y(number: float) -> float:
        return height - (((number - minimum) / span) * height)

    candle_marks: list[str] = []
    for index, candle in enumerate(candles):
        x = index * candle_width + (candle_width / 2)
        open_y = to_y(candle["open"])
        close_y = to_y(candle["close"])
        high_y = to_y(candle["high"])
        low_y = to_y(candle["low"])
        top = min(open_y, close_y)
        body_height = max(abs(close_y - open_y), 1.25)
        fill = (
            TONE_COLORS["up"]
            if candle["close"] >= candle["open"]
            else TONE_COLORS["down"]
        )
        candle_marks.append(
            f"<line x1='{x:.2f}' y1='{high_y:.2f}' x2='{x:.2f}' y2='{low_y:.2f}' stroke='{fill}' stroke-width='1.1'></line>"
        )
        candle_marks.append(
            "<rect "
            f"x='{x - candle_width * 0.27:.2f}' y='{top:.2f}' width='{candle_width * 0.54:.2f}' "
            f"height='{body_height:.2f}' fill='{fill}' opacity='0.92'></rect>"
        )

    overlays_svg: list[str] = []
    if "MA" in overlays:
        overlays_svg.extend(
            [
                f"<path d='{_line_path(analytics['ma5'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['amber']}' stroke-width='1.6'></path>",
                f"<path d='{_line_path(analytics['ma20'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['blue']}' stroke-width='1.4'></path>",
                f"<path d='{_line_path(analytics['ma60'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.2'></path>",
            ]
        )
    if "EMA" in overlays:
        overlays_svg.extend(
            [
                f"<path d='{_line_path(analytics['ema12'], minimum, maximum, width, height)}' fill='none' stroke='#9ad97b' stroke-width='1.2'></path>",
                f"<path d='{_line_path(analytics['ema26'], minimum, maximum, width, height)}' fill='none' stroke='#f08d49' stroke-width='1.2' stroke-dasharray='5 4'></path>",
            ]
        )
    if "BOLL" in overlays:
        overlays_svg.extend(
            [
                f"<path d='{_line_path(analytics['boll_upper'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.0' stroke-dasharray='4 3'></path>",
                f"<path d='{_line_path(analytics['boll_mid'], minimum, maximum, width, height)}' fill='none' stroke='#406c84' stroke-width='1.0'></path>",
                f"<path d='{_line_path(analytics['boll_lower'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.0' stroke-dasharray='4 3'></path>",
            ]
        )
    if "VWAP" in overlays:
        overlays_svg.append(
            f"<path d='{_line_path(analytics['vwap'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['yellow']}' stroke-width='1.1'></path>"
        )

    route_overlay = ""
    if route == "orderflow":
        max_volume = max(analytics["volumes"])
        bars: list[str] = []
        for index, volume in enumerate(analytics["volumes"]):
            bar_height = (volume / max_volume) * 82
            bar_width = width / len(analytics["volumes"])
            bars.append(
                "<rect "
                f"x='{index * bar_width + bar_width * 0.18:.2f}' y='{height - bar_height:.2f}' "
                f"width='{bar_width * 0.62:.2f}' height='{bar_height:.2f}' fill='{TONE_COLORS['blue']}' opacity='0.18'></rect>"
            )
        route_overlay = "".join(bars)
    elif route == "micro":
        bars = []
        for index, candle in enumerate(candles):
            bar_width = width / len(candles)
            y = max(height - 28 - abs(candle["delta"]) / 1800, 120)
            fill = TONE_COLORS["up"] if candle["delta"] >= 0 else TONE_COLORS["down"]
            bars.append(
                "<rect "
                f"x='{index * bar_width + bar_width * 0.2:.2f}' y='{y:.2f}' width='{bar_width * 0.48:.2f}' "
                f"height='20' fill='{fill}' opacity='0.28'></rect>"
            )
        route_overlay = "".join(bars)

    return f"<svg viewBox='0 0 {width:.0f} {height:.0f}' preserveAspectRatio='none' aria-label='Primary chart'>{route_overlay}{''.join(candle_marks)}{''.join(overlays_svg)}</svg>"

    def to_y(number: float) -> float:
        return height - (((number - minimum) / span) * height)


def build_depth_rows(
    active_model: dict[str, Any], depth_mode: str
) -> list[dict[str, str]]:
    """Build the right-rail market depth rows."""

    base = active_model["last"]
    rows: list[dict[str, str]] = []
    max_size = 16000
    for index in range(9, -1, -1):
        price = base + ((index - 4.5) * 0.2)
        bid_size = 2800 + round(abs(math.sin(index + base)) * 9800)
        ask_size = 2600 + round(abs(math.cos(index + base)) * 10200)
        bid_ratio = max(min(bid_size / max_size, 1.0), 0.1)
        ask_ratio = max(min(ask_size / max_size, 1.0), 0.1)
        if depth_mode == "profile":
            bid_text = f"{round(bid_ratio * 100):d}%"
            ask_text = f"{round(ask_ratio * 100):d}%"
        elif depth_mode == "imbalance":
            bid_text = format_signed((bid_size - ask_size) / 1000, 1, "K")
            ask_text = format_signed((ask_size - bid_size) / 1000, 1, "K")
        else:
            bid_text = compact_volume(bid_size)
            ask_text = compact_volume(ask_size)
        rows.append(
            {
                "price": format_number(price),
                "bid_text": bid_text,
                "ask_text": ask_text,
                "bid_width": f"{bid_ratio * 100:.1f}%",
                "ask_width": f"{ask_ratio * 100:.1f}%",
            }
        )
    return rows


def build_order_book_rows(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the right-rail order book rows."""

    base = active_model["last"]
    rows: list[dict[str, str]] = []
    for index in range(10):
        ask_price = base + ((10 - index) * 0.1)
        bid_price = base - ((index + 1) * 0.1)
        ask_size = 3200 + index * 740
        bid_size = 3400 + (9 - index) * 820
        rows.append(
            {
                "ask_price": format_number(ask_price),
                "ask_size": compact_volume(ask_size),
                "spread": format_number(ask_price - bid_price),
                "bid_size": compact_volume(bid_size),
                "bid_price": format_number(bid_price),
            }
        )
    return rows
