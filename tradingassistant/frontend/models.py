"""??????????????????????????????????"""

from __future__ import annotations

import math
from typing import Any

from .studies import (
    _atr,
    _ema,
    _moving_average,
    _obv,
    _rolling_std,
    _rsi,
)
from .utils import (
    _scale_amplitude,
    _seed_from_key,
    compact_volume,
    format_number,
    format_signed,
    normalize_code,
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

    for index in range(CHART_POINT_COUNT):
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
    for price, volume in zip(typical_prices, volumes, strict=True):
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
    boll_upper = [mid + (std * 2) for mid, std in zip(boll_mid, std20, strict=True)]
    boll_lower = [mid - (std * 2) for mid, std in zip(boll_mid, std20, strict=True)]
    macd_line = [fast - slow for fast, slow in zip(ema12, ema26, strict=True)]
    macd_signal = _ema(macd_line, 9)
    macd_hist = [line - signal for line, signal in zip(macd_line, macd_signal, strict=True)]
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




def _build_overlay_legend_models(active_model: dict[str, Any], overlays: list[str]) -> list[dict[str, Any]]:
    """Return the active overlay series used by legends and hover cards."""

    analytics = active_model["analytics"]
    items: list[dict[str, Any]] = []
    if "MA" in overlays:
        items.extend([
            {"label": "MA5", "series": analytics["ma5"], "tone": "amber"},
            {"label": "MA20", "series": analytics["ma20"], "tone": "blue"},
            {"label": "MA60", "series": analytics["ma60"], "tone": "soft"},
        ])
    if "EMA" in overlays:
        items.extend([
            {"label": "EMA12", "series": analytics["ema12"], "tone": "up"},
            {"label": "EMA26", "series": analytics["ema26"], "tone": "down"},
        ])
    if "BOLL" in overlays:
        items.extend([
            {"label": "BOLL U", "series": analytics["boll_upper"], "tone": "cyan"},
            {"label": "BOLL L", "series": analytics["boll_lower"], "tone": "cyan"},
        ])
    if "VWAP" in overlays:
        items.append({"label": "VWAP", "series": analytics["vwap"], "tone": "yellow"})
    return items
