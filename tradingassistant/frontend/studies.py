"Technical studies for route analysis: MA, EMA, RSI, ATR, OBV, MACD and analysis card builders."

from __future__ import annotations

import math
from typing import Any

from .utils import (
    _clamp_chart_index,
    _format_study_value,
    _histogram_svg,
    _line_path,
    format_number,
    format_signed,
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


def _moving_average(values: list[float], window: int) -> list[float]:
    """Return a simple moving average sequence."""

    result: list[float] = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        sample = values[start : index + 1]
        result.append(sum(sample) / len(sample))
    return result


def _ema(values: list[float], window: int) -> list[float]:
    """Return an exponential moving average sequence."""

    result: list[float] = []
    multiplier = 2 / (window + 1)
    for index, value in enumerate(values):
        if index == 0:
            result.append(value)
            continue
        result.append(((value - result[-1]) * multiplier) + result[-1])
    return result


def _rolling_std(values: list[float], window: int) -> list[float]:
    """Return a rolling standard deviation sequence."""

    result: list[float] = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        sample = values[start : index + 1]
        mean = sum(sample) / len(sample)
        variance = sum((item - mean) ** 2 for item in sample) / len(sample)
        result.append(math.sqrt(variance))
    return result


def _rsi(values: list[float], window: int = 14) -> list[float]:
    """Return an RSI sequence."""

    if not values:
        return []

    gains = [0.0]
    losses = [0.0]
    for index in range(1, len(values)):
        change = values[index] - values[index - 1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))

    avg_gain = _moving_average(gains, window)
    avg_loss = _moving_average(losses, window)
    result: list[float] = []
    for gain, loss in zip(avg_gain, avg_loss, strict=True):
        if loss == 0:
            result.append(100.0)
            continue
        strength = gain / loss
        result.append(100 - (100 / (1 + strength)))
    return result


def _atr(candles: list[dict[str, float]], window: int = 14) -> list[float]:
    """Return an ATR sequence."""

    true_ranges: list[float] = []
    previous_close = candles[0]["close"]
    for candle in candles:
        high = candle["high"]
        low = candle["low"]
        true_ranges.append(
            max(high - low, abs(high - previous_close), abs(low - previous_close))
        )
        previous_close = candle["close"]
    return _moving_average(true_ranges, window)


def _obv(candles: list[dict[str, float]]) -> list[float]:
    """Return an OBV sequence."""

    if not candles:
        return []

    result = [candles[0]["volume"]]
    for index in range(1, len(candles)):
        current = candles[index]
        previous = candles[index - 1]
        if current["close"] >= previous["close"]:
            result.append(result[-1] + current["volume"])
        else:
            result.append(result[-1] - current["volume"])
    return result


def _build_route_study_models(
    active_model: dict[str, Any], route: str
) -> list[dict[str, Any]]:
    """Build route study definitions with explicit series metadata."""

    analytics = active_model["analytics"]
    candles = active_model["candles"]
    if route == "momentum":
        return [
            {
                "name": "MACD Histogram",
                "tag": "Impulse",
                "foot": ["Signal spread", "Zero line watch"],
                "series": analytics["macd_hist"],
                "tone": "amber",
                "histogram": True,
            },
            {
                "name": "RSI 14",
                "tag": "Momentum",
                "foot": ["Range state", "Failure swing"],
                "series": analytics["rsi14"],
                "tone": "blue",
                "histogram": False,
            },
            {
                "name": "Signal Delta",
                "tag": "Trigger",
                "foot": ["Line minus signal", "Timing pressure"],
                "series": [
                    line - signal
                    for line, signal in zip(
                        analytics["macd_line"], analytics["macd_signal"], strict=True
                    )
                ],
                "tone": "green",
                "histogram": False,
            },
        ]
    if route == "trend":
        return [
            {
                "name": "MA20 - MA60",
                "tag": "Slope",
                "foot": ["Trend spread", "Medium-term bias"],
                "series": [
                    fast - slow
                    for fast, slow in zip(
                        analytics["ma20"], analytics["ma60"], strict=True
                    )
                ],
                "tone": "amber",
                "histogram": False,
            },
            {
                "name": "EMA12 - EMA26",
                "tag": "Pullback",
                "foot": ["Fast versus slow", "Continuation risk"],
                "series": [
                    fast - slow
                    for fast, slow in zip(
                        analytics["ema12"], analytics["ema26"], strict=True
                    )
                ],
                "tone": "blue",
                "histogram": False,
            },
            {
                "name": "MA5 - MA20",
                "tag": "Front End",
                "foot": ["Near-term spread", "Trend firmness"],
                "series": [
                    fast - slow
                    for fast, slow in zip(
                        analytics["ma5"], analytics["ma20"], strict=True
                    )
                ],
                "tone": "green",
                "histogram": False,
            },
        ]
    if route == "volatility":
        return [
            {
                "name": "ATR 14",
                "tag": "Range",
                "foot": ["Expansion rate", "Stops calibration"],
                "series": analytics["atr14"],
                "tone": "amber",
                "histogram": False,
            },
            {
                "name": "Band Width",
                "tag": "Compression",
                "foot": ["Upper minus lower", "Breakout readiness"],
                "series": [
                    upper - lower
                    for upper, lower in zip(
                        analytics["boll_upper"], analytics["boll_lower"], strict=True
                    )
                ],
                "tone": "blue",
                "histogram": False,
            },
            {
                "name": "High - Low",
                "tag": "Session Swing",
                "foot": ["Raw range", "Bar stress"],
                "series": [candle["high"] - candle["low"] for candle in candles],
                "tone": "green",
                "histogram": False,
            },
        ]
    if route == "orderflow":
        return [
            {
                "name": "Delta",
                "tag": "Flow",
                "foot": ["Aggressor tilt", "Participation bias"],
                "series": [candle["delta"] for candle in candles],
                "tone": "amber",
                "histogram": True,
            },
            {
                "name": "OBV",
                "tag": "Carry",
                "foot": ["Accumulation line", "Persistence"],
                "series": analytics["obv"],
                "tone": "blue",
                "histogram": False,
            },
            {
                "name": "Volume x1K",
                "tag": "Tempo",
                "foot": ["Execution pace", "Order flow speed"],
                "series": [volume / 1000 for volume in analytics["volumes"]],
                "tone": "green",
                "histogram": False,
            },
        ]
    if route == "micro":
        return [
            {
                "name": "Micro Range",
                "tag": "Queue",
                "foot": ["High-low pulse", "Spread pressure"],
                "series": [
                    (candle["high"] - candle["low"]) * 100 for candle in candles
                ],
                "tone": "amber",
                "histogram": False,
            },
            {
                "name": "Queue Size Proxy",
                "tag": "Depth",
                "foot": ["Volume pulse", "Resting flow"],
                "series": [volume / 2500 for volume in analytics["volumes"]],
                "tone": "blue",
                "histogram": False,
            },
            {
                "name": "Delta x0.01",
                "tag": "Prints",
                "foot": ["Trade impulse", "Execution stress"],
                "series": [candle["delta"] / 80 for candle in candles],
                "tone": "green",
                "histogram": False,
            },
        ]
    return [
        {
            "name": "MA5 - MA20",
            "tag": "Structure",
            "foot": ["Trend stack", "Bias spread"],
            "series": [
                fast - slow
                for fast, slow in zip(analytics["ma5"], analytics["ma20"], strict=True)
            ],
            "tone": "amber",
            "histogram": False,
        },
        {
            "name": "Volume x1K",
            "tag": "Participation",
            "foot": ["Turnover pace", "Breadth proxy"],
            "series": [volume / 1000 for volume in analytics["volumes"]],
            "tone": "blue",
            "histogram": False,
        },
        {
            "name": "Price - VWAP",
            "tag": "Location",
            "foot": ["Relative price", "Fair value gap"],
            "series": [
                close - fair
                for close, fair in zip(
                    analytics["closes"], analytics["vwap"], strict=True
                )
            ],
            "tone": "green",
            "histogram": False,
        },
    ]


def build_route_studies(
    active_model: dict[str, Any],
    route: str,
    active_index: int | None = None,
    hover_active: bool = False,
) -> list[dict[str, str]]:
    """Build the lower linked study panes for the active route."""

    tone_map = {
        "amber": TONE_COLORS["amber"],
        "blue": TONE_COLORS["blue"],
        "green": TONE_COLORS["up"],
    }
    cards: list[dict[str, str]] = []
    for study in _build_route_study_models(active_model, route):
        series = study["series"]
        series_index = _clamp_chart_index(active_index, len(series))
        minimum = min(series)
        maximum = max(series)
        width = STUDY_CHART_WIDTH
        height = STUDY_CHART_HEIGHT
        if study["histogram"]:
            svg_body = _histogram_svg(series, width, height)
        else:
            svg_body = f"<line x1='0' y1='{height - 1:.2f}' x2='{width:.2f}' y2='{height - 1:.2f}' stroke='#22303d' stroke-width='1'></line><path d='{_line_path(series, minimum, maximum, width, height)}' fill='none' stroke='{tone_map[study['tone']]}' stroke-width='1.8'></path>"
        latest_value = _format_study_value(series[-1])
        hover_value = _format_study_value(series[series_index])
        cards.append(
            {
                "name": study["name"],
                "tag": study["tag"],
                "tone": study["tone"],
                "value": latest_value,
                "hover_value": hover_value,
                "display_value": hover_value if hover_active else latest_value,
                "hover_label": f"{active_model['scale']} BAR {series_index + 1:02d}/{len(series):02d}",
                "display_label": f"{active_model['scale']} BAR {series_index + 1:02d}/{len(series):02d}"
                if hover_active
                else "Latest",
                "foot_left": study["foot"][0],
                "foot_right": study["foot"][1],
                "svg": f"<svg viewBox='0 0 {width:.0f} {height:.0f}' preserveAspectRatio='none' aria-label='{study['name']}'>{svg_body}</svg>",
            }
        )
    return cards


def build_analysis_cards(
    active_model: dict[str, Any],
    route: str,
    scale: str,
    overlays: list[str],
    depth_mode: str,
) -> list[dict[str, Any]]:
    """Build the scheduled AI analysis cards."""

    constructive = active_model["change_pct"] >= 0
    direction = "Constructive" if constructive else "Defensive"
    confidence = "76%" if constructive else "61%"
    risk_bias = "Elevated" if abs(active_model["change_pct"]) > 1.8 else "Measured"
    if scale in {"30S", "1M"}:
        cadence = "Every 5 min"
    elif scale == "1D":
        cadence = "Every 30 min"
    else:
        cadence = "Every 2 hours"

    return [
        {
            "title": "AI Regime Read",
            "subtitle": f"{active_model['meta']['code']} / {route.upper()} / scheduled push",
            "stamp": "Latest",
            "body": f"{direction} tone remains intact as price trades {'above' if active_model['last'] >= active_model['analytics']['vwap'][-1] else 'near'} VWAP. Pullbacks should be treated as review points rather than as immediate reversals until participation fades materially.",
            "metric_1_label": "Confidence",
            "metric_1_value": confidence,
            "metric_2_label": "Refresh",
            "metric_2_value": cadence,
            "metric_3_label": "Risk",
            "metric_3_value": risk_bias,
        },
        {
            "title": "Flow And Structure",
            "subtitle": "Automated summary / order book + tape + indicators",
            "stamp": "Queued",
            "body": f"Resting depth remains {'firmer on the bid side' if constructive else 'more cautious on the offer side'}, while overlays stay {'well aligned' if len(overlays) >= 3 else 'partially aligned'} with the active route.",
            "metric_1_label": "Depth",
            "metric_1_value": depth_mode.upper(),
            "metric_2_label": "Overlays",
            "metric_2_value": f"{len(overlays)} live",
            "metric_3_label": "Next Push",
            "metric_3_value": "14:35",
        },
        {
            "title": "Risk Notes",
            "subtitle": "What the scheduled AI push would flag next",
            "stamp": "Watch",
            "body": f"Monitor for a break {'back under' if constructive else 'back above'} the short moving-average cluster, a spread expansion beyond recent norms, or a visible slowdown in participation. Any two together would downgrade the next scheduled analysis.",
            "metric_1_label": "VWAP Gap",
            "metric_1_value": format_signed(
                (
                    (active_model["last"] - active_model["analytics"]["vwap"][-1])
                    / active_model["analytics"]["vwap"][-1]
                )
                * 100,
                2,
                "%",
            ),
            "metric_2_label": "ATR",
            "metric_2_value": format_number(active_model["analytics"]["atr14"][-1]),
            "metric_3_label": "Bias",
            "metric_3_value": direction.upper(),
        },
    ]
