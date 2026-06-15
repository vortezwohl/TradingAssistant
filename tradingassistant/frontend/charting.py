
"""Mock market models and SVG render helpers for the native terminal workspace."""

from __future__ import annotations

import hashlib
import math
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


def get_symbol_profile(code: str) -> dict[str, str]:
    """Return a static profile for the selected code."""

    normalized = normalize_code(code)
    if normalized in SYMBOL_PROFILES:
        return {"code": normalized, **SYMBOL_PROFILES[normalized]}

    if "." in normalized:
        region, ticker = normalized.split(".", maxsplit=1)
    else:
        region, ticker = "US", normalized or "CUSTOM"
        normalized = f"{region}.{ticker}"

    return {
        "code": normalized,
        "name": f"{ticker} Market Line",
        "venue": "User List",
        "sector": "Custom Basket",
        "session": f"{region} Session / Cash",
        "currency": "USD" if region == "US" else "HKD",
    }


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
    for gain, loss in zip(avg_gain, avg_loss):
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
        true_ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
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


def build_market_model(code: str, scale: str) -> dict[str, Any]:
    """Build the full mock model for the active symbol and scale."""

    profile = get_symbol_profile(code)
    normalized_code = profile["code"]
    seed = _seed_from_key(f"{normalized_code}:{scale}")
    amplitude = _scale_amplitude(scale)
    base_price = 38 + ((seed % 9000) / 55)
    prev_close = base_price * (0.985 + (((seed >> 2) % 9) * 0.0035))
    candles: list[dict[str, float]] = []
    running = prev_close

    for index in range(72):
        wave_primary = math.sin((index + (seed % 17)) / 5.2) * amplitude
        wave_secondary = math.cos((index + (seed % 29)) / 8.7) * amplitude * 0.58
        drift = ((index - 36) / 36) * amplitude * ((((seed >> 5) % 7) - 3) / 3)
        open_price = running + math.sin((index + (seed % 11)) / 3.4) * amplitude * 0.14
        close_price = running + (wave_primary * 0.21) + (wave_secondary * 0.14) + (drift * 0.17)
        high_price = max(open_price, close_price) + abs(math.cos(index / 4.1 + seed % 5)) * amplitude * 0.34 + 0.04
        low_price = min(open_price, close_price) - abs(math.sin(index / 3.6 + seed % 7)) * amplitude * 0.31 - 0.04
        volume = float(int(1400 + abs(math.sin(index / 2.8 + (seed % 13))) * 8800 + index * 18 + (seed % 700)))
        delta = float(int((close_price - open_price) * volume * 0.7))
        turnover = volume * ((open_price + close_price + high_price + low_price) / 4)
        candles.append(
            {
                "open": round(open_price, 4),
                "high": round(high_price, 4),
                "low": round(low_price, 4),
                "close": round(close_price, 4),
                "volume": volume,
                "delta": delta,
                "turnover": turnover,
            }
        )
        running = close_price

    closes = [item["close"] for item in candles]
    highs = [item["high"] for item in candles]
    lows = [item["low"] for item in candles]
    volumes = [item["volume"] for item in candles]
    turnovers = [item["turnover"] for item in candles]
    typical_prices = [
        (item["high"] + item["low"] + item["close"]) / 3
        for item in candles
    ]

    cumulative_turnover = 0.0
    cumulative_volume = 0.0
    vwap: list[float] = []
    for price, volume in zip(typical_prices, volumes):
        cumulative_turnover += price * volume
        cumulative_volume += volume
        vwap.append(cumulative_turnover / max(cumulative_volume, 1.0))

    ma5 = _moving_average(closes, 5)
    ma20 = _moving_average(closes, 20)
    ma60 = _moving_average(closes, 60)
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    boll_mid = ma20
    std20 = _rolling_std(closes, 20)
    boll_upper = [mid + (std * 2) for mid, std in zip(boll_mid, std20)]
    boll_lower = [mid - (std * 2) for mid, std in zip(boll_mid, std20)]
    macd_line = [fast - slow for fast, slow in zip(ema12, ema26)]
    macd_signal = _ema(macd_line, 9)
    macd_hist = [line - signal for line, signal in zip(macd_line, macd_signal)]
    rsi14 = _rsi(closes, 14)
    atr14 = _atr(candles, 14)
    obv = _obv(candles)

    last_price = closes[-1]
    change_value = last_price - prev_close
    change_pct = (change_value / prev_close) * 100
    tone = tone_from_number(change_pct)

    return {
        "meta": profile,
        "scale": scale,
        "candles": candles,
        "prev_close": prev_close,
        "last": last_price,
        "change_value": change_value,
        "change_pct": change_pct,
        "high": max(highs),
        "low": min(lows),
        "volume": sum(volumes),
        "turnover": sum(turnovers),
        "tone": tone,
        "change_color": TONE_COLORS[tone],
        "analytics": {
            "closes": closes,
            "highs": highs,
            "lows": lows,
            "volumes": volumes,
            "ma5": ma5,
            "ma20": ma20,
            "ma60": ma60,
            "ema12": ema12,
            "ema26": ema26,
            "boll_mid": boll_mid,
            "boll_upper": boll_upper,
            "boll_lower": boll_lower,
            "vwap": vwap,
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "rsi14": rsi14,
            "atr14": atr14,
            "obv": obv,
        },
    }


def build_quote_strip(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the compact quote strip for the top bar."""

    analytics = active_model["analytics"]
    return [
        {"label": active_model["meta"]["code"], "value": format_number(active_model["last"]), "tone": active_model["tone"]},
        {"label": "VWAP", "value": format_number(analytics["vwap"][-1]), "tone": "blue"},
        {"label": "ATR", "value": format_number(analytics["atr14"][-1]), "tone": "amber"},
        {"label": "Spread", "value": format_number(max(0.01, abs(active_model["change_pct"]) * 0.03), 2), "tone": "soft"},
    ]


def build_watchlist_rows(codes: list[str], active_code: str, scale: str, sort_mode: str) -> list[dict[str, str | bool]]:
    """Build the watchlist table rows."""

    rows: list[dict[str, str | bool]] = []
    for code in codes:
        model = build_market_model(code, scale)
        rows.append(
            {
                "code": model["meta"]["code"],
                "name": model["meta"]["name"],
                "meta": f"{model['meta']['venue']} / {model['meta']['sector']}",
                "last": format_number(model["last"]),
                "change": format_signed(model["change_pct"], 2, "%"),
                "volume": compact_volume(model["volume"]),
                "tone": model["tone"],
                "active": model["meta"]["code"] == active_code,
            }
        )

    rows.sort(key=lambda item: str(item["name"] if sort_mode == "name" else item["code"]))
    return rows


def build_movers_rows(tab: str, scale: str) -> list[dict[str, str]]:
    """Build the leaders or laggards table rows."""

    rows: list[dict[str, Any]] = []
    for code in UNIVERSE_CODES:
        model = build_market_model(code, scale)
        rows.append(
            {
                "code": model["meta"]["code"],
                "name": model["meta"]["name"],
                "last": format_number(model["last"]),
                "change": format_signed(model["change_pct"], 2, "%"),
                "change_value": model["change_pct"],
                "tone": model["tone"],
            }
        )

    rows.sort(key=lambda item: item["change_value"], reverse=(tab == "leaders"))
    return [
        {
            "code": row["code"],
            "name": row["name"],
            "last": row["last"],
            "change": row["change"],
            "tone": row["tone"],
        }
        for row in rows[:8]
    ]


def build_snapshot_cells(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the desk snapshot cells."""

    return [
        {"label": "Net Bias", "value": "Risk On" if active_model["change_pct"] >= 0 else "Defensive", "sub": "Scheduled desk posture"},
        {"label": "Flow Score", "value": f"{62 + int(abs(active_model['change_pct']) * 4):d}", "sub": "Bid/ask participation"},
        {"label": "Vol Pulse", "value": format_number(active_model["analytics"]["atr14"][-1]), "sub": "Range expansion"},
        {"label": "VWAP Gap", "value": format_signed(((active_model["last"] - active_model["analytics"]["vwap"][-1]) / active_model["analytics"]["vwap"][-1]) * 100, 2, "%"), "sub": "Price versus fair flow"},
    ]


def build_instrument_metrics(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the compact instrument metrics strip."""

    analytics = active_model["analytics"]
    return [
        {"label": "Day High", "value": format_number(active_model["high"])},
        {"label": "Day Low", "value": format_number(active_model["low"])},
        {"label": "Volume", "value": compact_volume(active_model["volume"])},
        {"label": "Turnover", "value": compact_volume(active_model["turnover"])},
        {"label": "ATR", "value": format_number(analytics["atr14"][-1])},
        {"label": "Prev Close", "value": format_number(active_model["prev_close"])},
    ]

def _line_path(values: list[float], minimum: float, maximum: float, width: float, height: float) -> str:
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

    minimum = min(min(values), 0.0)
    maximum = max(max(values), 0.0)
    span = max(maximum - minimum, 0.0001)
    baseline = height - (((0.0 - minimum) / span) * height)
    bar_width = width / max(len(values), 1)
    bars: list[str] = [f"<line x1='0' y1='{baseline:.2f}' x2='{width:.2f}' y2='{baseline:.2f}' stroke='#22303d' stroke-width='1'></line>"]
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


def build_chart_legend(active_model: dict[str, Any], overlays: list[str]) -> list[dict[str, str]]:
    """Build legend items for the main chart stage."""

    analytics = active_model["analytics"]
    legend: list[dict[str, str]] = [
        {"label": active_model["meta"]["code"], "value": format_number(active_model["last"]), "tone": active_model["tone"]}
    ]
    if "MA" in overlays:
        legend.extend([
            {"label": "MA5", "value": format_number(analytics["ma5"][-1]), "tone": "amber"},
            {"label": "MA20", "value": format_number(analytics["ma20"][-1]), "tone": "blue"},
            {"label": "MA60", "value": format_number(analytics["ma60"][-1]), "tone": "soft"},
        ])
    if "EMA" in overlays:
        legend.extend([
            {"label": "EMA12", "value": format_number(analytics["ema12"][-1]), "tone": "up"},
            {"label": "EMA26", "value": format_number(analytics["ema26"][-1]), "tone": "down"},
        ])
    if "BOLL" in overlays:
        legend.extend([
            {"label": "BOLL U", "value": format_number(analytics["boll_upper"][-1]), "tone": "cyan"},
            {"label": "BOLL L", "value": format_number(analytics["boll_lower"][-1]), "tone": "cyan"},
        ])
    if "VWAP" in overlays:
        legend.append({"label": "VWAP", "value": format_number(analytics["vwap"][-1]), "tone": "yellow"})
    return legend


def build_primary_chart_svg(active_model: dict[str, Any], overlays: list[str], route: str) -> str:
    """Build the primary chart SVG for the center chart stage."""

    width = 1000.0
    height = 420.0
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
        fill = TONE_COLORS["up"] if candle["close"] >= candle["open"] else TONE_COLORS["down"]
        candle_marks.append(f"<line x1='{x:.2f}' y1='{high_y:.2f}' x2='{x:.2f}' y2='{low_y:.2f}' stroke='{fill}' stroke-width='1.1'></line>")
        candle_marks.append(
            "<rect "
            f"x='{x - candle_width * 0.27:.2f}' y='{top:.2f}' width='{candle_width * 0.54:.2f}' "
            f"height='{body_height:.2f}' fill='{fill}' opacity='0.92'></rect>"
        )

    overlays_svg: list[str] = []
    if "MA" in overlays:
        overlays_svg.extend([
            f"<path d='{_line_path(analytics['ma5'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['amber']}' stroke-width='1.6'></path>",
            f"<path d='{_line_path(analytics['ma20'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['blue']}' stroke-width='1.4'></path>",
            f"<path d='{_line_path(analytics['ma60'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.2'></path>",
        ])
    if "EMA" in overlays:
        overlays_svg.extend([
            f"<path d='{_line_path(analytics['ema12'], minimum, maximum, width, height)}' fill='none' stroke='#9ad97b' stroke-width='1.2'></path>",
            f"<path d='{_line_path(analytics['ema26'], minimum, maximum, width, height)}' fill='none' stroke='#f08d49' stroke-width='1.2' stroke-dasharray='5 4'></path>",
        ])
    if "BOLL" in overlays:
        overlays_svg.extend([
            f"<path d='{_line_path(analytics['boll_upper'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.0' stroke-dasharray='4 3'></path>",
            f"<path d='{_line_path(analytics['boll_mid'], minimum, maximum, width, height)}' fill='none' stroke='#406c84' stroke-width='1.0'></path>",
            f"<path d='{_line_path(analytics['boll_lower'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['cyan']}' stroke-width='1.0' stroke-dasharray='4 3'></path>",
        ])
    if "VWAP" in overlays:
        overlays_svg.append(f"<path d='{_line_path(analytics['vwap'], minimum, maximum, width, height)}' fill='none' stroke='{TONE_COLORS['yellow']}' stroke-width='1.1'></path>")

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


def build_route_studies(active_model: dict[str, Any], route: str) -> list[dict[str, str]]:
    """Build the lower linked study panes for the active route."""

    analytics = active_model["analytics"]
    candles = active_model["candles"]
    if route == "momentum":
        studies = [
            ("MACD Histogram", "Impulse", ["Signal spread", "Zero line watch"], analytics["macd_hist"], "amber", True),
            ("RSI 14", "Momentum", ["Range state", "Failure swing"], analytics["rsi14"], "blue", False),
            ("Signal Delta", "Trigger", ["Line minus signal", "Timing pressure"], [line - signal for line, signal in zip(analytics["macd_line"], analytics["macd_signal"])], "green", False),
        ]
    elif route == "trend":
        studies = [
            ("MA20 - MA60", "Slope", ["Trend spread", "Medium-term bias"], [fast - slow for fast, slow in zip(analytics["ma20"], analytics["ma60"])], "amber", False),
            ("EMA12 - EMA26", "Pullback", ["Fast versus slow", "Continuation risk"], [fast - slow for fast, slow in zip(analytics["ema12"], analytics["ema26"])], "blue", False),
            ("MA5 - MA20", "Front End", ["Near-term spread", "Trend firmness"], [fast - slow for fast, slow in zip(analytics["ma5"], analytics["ma20"])], "green", False),
        ]
    elif route == "volatility":
        studies = [
            ("ATR 14", "Range", ["Expansion rate", "Stops calibration"], analytics["atr14"], "amber", False),
            ("Band Width", "Compression", ["Upper minus lower", "Breakout readiness"], [upper - lower for upper, lower in zip(analytics["boll_upper"], analytics["boll_lower"])], "blue", False),
            ("High - Low", "Session Swing", ["Raw range", "Bar stress"], [candle["high"] - candle["low"] for candle in candles], "green", False),
        ]
    elif route == "orderflow":
        studies = [
            ("Delta", "Flow", ["Aggressor tilt", "Participation bias"], [candle["delta"] for candle in candles], "amber", True),
            ("OBV", "Carry", ["Accumulation line", "Persistence"], analytics["obv"], "blue", False),
            ("Volume x1K", "Tempo", ["Execution pace", "Order flow speed"], [volume / 1000 for volume in analytics["volumes"]], "green", False),
        ]
    elif route == "micro":
        studies = [
            ("Micro Range", "Queue", ["High-low pulse", "Spread pressure"], [(candle["high"] - candle["low"]) * 100 for candle in candles], "amber", False),
            ("Queue Size Proxy", "Depth", ["Volume pulse", "Resting flow"], [volume / 2500 for volume in analytics["volumes"]], "blue", False),
            ("Delta x0.01", "Prints", ["Trade impulse", "Execution stress"], [candle["delta"] / 80 for candle in candles], "green", False),
        ]
    else:
        studies = [
            ("MA5 - MA20", "Structure", ["Trend stack", "Bias spread"], [fast - slow for fast, slow in zip(analytics["ma5"], analytics["ma20"])], "amber", False),
            ("Volume x1K", "Participation", ["Turnover pace", "Breadth proxy"], [volume / 1000 for volume in analytics["volumes"]], "blue", False),
            ("Price - VWAP", "Location", ["Relative price", "Fair value gap"], [close - fair for close, fair in zip(analytics["closes"], analytics["vwap"])], "green", False),
        ]

    tone_map = {"amber": TONE_COLORS["amber"], "blue": TONE_COLORS["blue"], "green": TONE_COLORS["up"]}
    cards: list[dict[str, str]] = []
    for name, tag, foot, series, tone, histogram in studies:
        minimum = min(series)
        maximum = max(series)
        width = 320.0
        height = 130.0
        if histogram:
            svg_body = _histogram_svg(series, width, height)
        else:
            svg_body = f"<line x1='0' y1='{height - 1:.2f}' x2='{width:.2f}' y2='{height - 1:.2f}' stroke='#22303d' stroke-width='1'></line><path d='{_line_path(series, minimum, maximum, width, height)}' fill='none' stroke='{tone_map[tone]}' stroke-width='1.8'></path>"
        cards.append({
            "name": name,
            "tag": tag,
            "tone": tone,
            "value": format_number(series[-1]),
            "foot_left": foot[0],
            "foot_right": foot[1],
            "svg": f"<svg viewBox='0 0 {width:.0f} {height:.0f}' preserveAspectRatio='none' aria-label='{name}'>{svg_body}</svg>",
        })
    return cards


def build_depth_rows(active_model: dict[str, Any], depth_mode: str) -> list[dict[str, str]]:
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
        rows.append({
            "price": format_number(price),
            "bid_text": bid_text,
            "ask_text": ask_text,
            "bid_width": f"{bid_ratio * 100:.1f}%",
            "ask_width": f"{ask_ratio * 100:.1f}%",
        })
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
        rows.append({
            "ask_price": format_number(ask_price),
            "ask_size": compact_volume(ask_size),
            "spread": format_number(ask_price - bid_price),
            "bid_size": compact_volume(bid_size),
            "bid_price": format_number(bid_price),
        })
    return rows


def build_analysis_cards(active_model: dict[str, Any], route: str, scale: str, overlays: list[str], depth_mode: str) -> list[dict[str, Any]]:
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
            "metric_1_value": format_signed(((active_model['last'] - active_model['analytics']['vwap'][-1]) / active_model['analytics']['vwap'][-1]) * 100, 2, "%"),
            "metric_2_label": "ATR",
            "metric_2_value": format_number(active_model['analytics']['atr14'][-1]),
            "metric_3_label": "Bias",
            "metric_3_value": direction.upper(),
        },
    ]


def build_tape_rows(active_model: dict[str, Any]) -> list[dict[str, str]]:
    """Build the recent prints rows for the Tape tab."""

    rows: list[dict[str, str]] = []
    for index in range(14):
        side = "BUY" if index % 3 else "SELL"
        price = active_model["last"] + ((index % 5) - 2) * 0.1
        size = 400 + index * 180
        rows.append({
            "price": format_number(price),
            "size": compact_volume(size),
            "time": f"14:{28 + (index // 3):02d}:{(index * 7) % 60:02d}",
            "side": side,
            "tone": "up" if side == "BUY" else "down",
        })
    return rows


def build_signal_rows() -> list[dict[str, str]]:
    """Build the Signals rail rows."""

    return [
        {"title": "Trend continuation", "body": "MA stack remains positively aligned and pullbacks keep holding near VWAP."},
        {"title": "Liquidity pocket", "body": "Offer depth thins two ticks above last trade while the bid queue refills."},
        {"title": "Momentum carry", "body": "MACD and RSI stay constructive on the active route settings."},
        {"title": "Execution note", "body": "Mock child-order slices would still favor passive accumulation."},
    ]


def build_news_rows() -> list[dict[str, str]]:
    """Build the News rail rows."""

    return [
        {"title": "Sector breadth remains concentrated in platform and chip names", "body": "Mock desk wrap / 14:29 / breadth broadens but leadership remains concentrated in liquid growth."},
        {"title": "Macro desk flags stable rates backdrop for risk assets", "body": "Mock rates recap / 14:16 / front-end repricing slows and beta appetite improves."},
        {"title": "Execution commentary sees healthy passive support below market", "body": "Mock market color / 13:58 / queue replenishment remains visible on the bid side."},
        {"title": "Fundamental narrative stays secondary to positioning impulse", "body": "Mock strategy note / 13:41 / near-term price discovery remains flow-led."},
    ]
