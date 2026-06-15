"Utility functions for number formatting, code normalization, scaling, and chart helpers."

from __future__ import annotations

import hashlib
from typing import Any

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


def normalize_code(value: str) -> str:
    """Normalize a user-entered watchlist code."""

    return value.strip().upper().replace(" ", "")


def _seed_from_key(key: str) -> int:
    """Build a stable integer seed from a string key."""

    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _scale_amplitude(scale: str) -> float:
    """Return the price amplitude for the selected scale."""

    return {
        "30S": 0.55,
        "1M": 0.72,
        "5M": 1.05,
        "15M": 1.42,
        "1H": 2.08,
        "4H": 3.34,
        "1D": 4.82,
        "1W": 7.14,
        "1MO": 10.40,
        "1Y": 14.80,
    }.get(scale, 2.40)


def format_number(value: float, digits: int = 2) -> str:
    """Format a numeric terminal value."""

    return f"{value:,.{digits}f}"


def format_signed(value: float, digits: int = 2, suffix: str = "") -> str:
    """Format a signed numeric terminal value."""

    sign = "+" if value >= 0 else "-"
    return f"{sign}{abs(value):,.{digits}f}{suffix}"


def compact_volume(value: float) -> str:
    """Format large numeric values for compact table display."""

    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def tone_from_number(value: float) -> str:
    """Map numeric direction to a semantic tone key."""

    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "flat"


def _clamp_chart_index(index: int | None, length: int) -> int:
    """Clamp a hover index to the available chart series length."""

    if length <= 0:
        return 0
    if index is None:
        return length - 1
    return max(0, min(index, length - 1))


def _format_study_value(value: float) -> str:
    """Format route study values with a density suited for terminal readouts."""

    absolute = abs(value)
    if absolute >= 1_000_000:
        return compact_volume(value)
    if absolute >= 100:
        return format_number(value, 1)
    if absolute >= 10:
        return format_number(value, 2)
    return format_number(value, 3)


def build_tape_rows(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the recent prints rows for the Tape tab."""

    rows: list[dict[str, str]] = []
    for index in range(14):
        side = "BUY" if index % 3 else "SELL"
        price = active_model["last"] + ((index % 5) - 2) * 0.1
        size = 400 + index * 180
        rows.append(
            {
                "price": format_number(price),
                "size": compact_volume(size),
                "time": f"14:{28 + (index // 3):02d}:{(index * 7) % 60:02d}",
                "side": side,
                "tone": "up" if side == "BUY" else "down",
            }
        )
    return rows


def build_signal_rows() -> list[dict[str, str]]:
    """Build the Signals rail rows."""

    return [
        {
            "title": "Trend continuation",
            "body": "MA stack remains positively aligned and pullbacks keep holding near VWAP.",
        },
        {
            "title": "Liquidity pocket",
            "body": "Offer depth thins two ticks above last trade while the bid queue refills.",
        },
        {
            "title": "Momentum carry",
            "body": "MACD and RSI stay constructive on the active route settings.",
        },
        {
            "title": "Execution note",
            "body": "Mock child-order slices would still favor passive accumulation.",
        },
    ]


def build_news_rows() -> list[dict[str, str]]:
    """Build the News rail rows."""

    return [
        {
            "title": "Sector breadth remains concentrated in platform and chip names",
            "body": "Mock desk wrap / 14:29 / breadth broadens but leadership remains concentrated in liquid growth.",
        },
        {
            "title": "Macro desk flags stable rates backdrop for risk assets",
            "body": "Mock rates recap / 14:16 / front-end repricing slows and beta appetite improves.",
        },
        {
            "title": "Execution commentary sees healthy passive support below market",
            "body": "Mock market color / 13:58 / queue replenishment remains visible on the bid side.",
        },
        {
            "title": "Fundamental narrative stays secondary to positioning impulse",
            "body": "Mock strategy note / 13:41 / near-term price discovery remains flow-led.",
        },
    ]


def _line_path(
    values: list[float], minimum: float, maximum: float, width: float, height: float
) -> str:
    """Convert a series into an SVG line path."""

    if not values:
        return ""

    span = max(maximum - minimum, 0.0001)
    points: list[str] = []
    denominator = max(len(values) - 1, 1)
    for index, value in enumerate(values):
        x = (index / denominator) * width
        y = height - (((value - minimum) / span) * height)
        command = "M" if index == 0 else "L"
        points.append(f"{command} {x:.2f} {y:.2f}")
    return " ".join(points)


def _histogram_svg(values: list[float], width: float, height: float) -> str:
    """Build histogram SVG content for study panes."""

    if not values:
        return ""

    minimum = min(*values, 0.0)
    maximum = max(*values, 0.0)
    span = max(maximum - minimum, 0.0001)
    baseline = height - (((0.0 - minimum) / span) * height)
    bar_width = width / max(len(values), 1)
    bars: list[str] = [
        f"<line x1='0' y1='{baseline:.2f}' x2='{width:.2f}' y2='{baseline:.2f}' stroke='#22303d' stroke-width='1'></line>"
    ]
    for index, value in enumerate(values):
        x = index * bar_width + (bar_width * 0.18)
        y = height - (((value - minimum) / span) * height)
        rect_y = min(y, baseline)
        rect_height = max(abs(baseline - y), 1.2)
        fill = TONE_COLORS["up"] if value >= 0 else TONE_COLORS["down"]
        bars.append(
            "<rect "
            f"x='{x:.2f}' y='{rect_y:.2f}' width='{bar_width * 0.64:.2f}' "
            f"height='{rect_height:.2f}' fill='{fill}' opacity='0.82'></rect>"
        )
    return "".join(bars)
