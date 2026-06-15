"""Indicator initialization, incremental updates, and consistency verification.

This module currently provides:
1. History-based initialization via OpenTrade;
2. Incremental update state model for initial indicators;
3. Provisional / finalized output markers;
4. Basic consistency comparison tools.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import isnan
from typing import Any

import pandas as pd
from opentrade.enrichment.indicators import enrich_history_frame

from tradingassistant.backend.charting.models import RuntimeBar


def safe_float(value: Any) -> float | None:
    """Safely convert a pandas/Python scalar to float.

    Args:
        value: Raw value.

    Returns:
        Float; returns `None` if empty or NaN.
    """
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if isnan(number):
        return None
    return number


def bars_to_frame(bars: list[RuntimeBar]) -> pd.DataFrame:
    """Convert runtime bar list to a DataFrame."""
    return pd.DataFrame(
        [
            {
                "date": bar.bar_time.isoformat(),
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "turnover": bar.turnover,
            }
            for bar in bars
        ]
    )


@dataclass(slots=True)
class IndicatorSnapshot:
    """Describe a single indicator output snapshot."""

    values: dict[str, float | None]
    provisional: bool

    def to_dict(self) -> dict[str, Any]:
        """Return serializable structure."""
        return {
            "values": self.values,
            "provisional": self.provisional,
        }


@dataclass(slots=True)
class RollingWindow:
    """Fixed-length sequence for window-based indicators."""

    size: int
    values: deque[float] = field(default_factory=deque)

    def append(self, value: float) -> None:
        """Append value while maintaining fixed window length."""
        self.values.append(value)
        while len(self.values) > self.size:
            self.values.popleft()

    def mean(self) -> float | None:
        """Return window mean."""
        if not self.values:
            return None
        return sum(self.values) / len(self.values)

    def std(self) -> float | None:
        """Return window standard deviation."""
        if not self.values:
            return None
        mean_value = self.mean()
        assert mean_value is not None
        variance = sum((value - mean_value) ** 2 for value in self.values) / len(
            self.values
        )
        return variance**0.5

    def as_list(self) -> list[float]:
        """Return a copy of window values as list."""
        return list(self.values)


@dataclass(slots=True)
class IndicatorState:
    """Maintain incremental indicator state for a single symbol/period."""

    bars: list[RuntimeBar] = field(default_factory=list)
    ema12: float | None = None
    ema26: float | None = None
    dea9: float | None = None
    avg_gain: float | None = None
    avg_loss: float | None = None
    ma5_window: RollingWindow = field(default_factory=lambda: RollingWindow(size=5))
    ma20_window: RollingWindow = field(default_factory=lambda: RollingWindow(size=20))
    boll_window: RollingWindow = field(default_factory=lambda: RollingWindow(size=20))
    latest_snapshot: IndicatorSnapshot | None = None


class IncrementalIndicatorEngine:
    """Indicator engine with history-based initialization and incremental updates."""

    def __init__(self) -> None:
        """Initialize indicator state mapping."""
        self._states: dict[str, IndicatorState] = {}

    def initialize(self, key: str, bars: list[RuntimeBar]) -> IndicatorSnapshot:
        """Initialize indicators from a history window.

        Args:
            key: Composite key of symbol + period.
            bars: Historical bar list.

        Returns:
            Initialized indicator snapshot.
        """
        frame = bars_to_frame(bars)
        enriched = enrich_history_frame(frame, "basic") if not frame.empty else frame
        state = IndicatorState(bars=list(bars))

        closes = [bar.close_price for bar in bars if bar.close_price is not None]
        for close_price in closes:
            state.ma5_window.append(close_price)
            state.ma20_window.append(close_price)
            state.boll_window.append(close_price)
        if not enriched.empty:
            latest = enriched.iloc[-1]
            state.ema12 = safe_float(latest.get("ema12"))
            state.ema26 = safe_float(latest.get("ema26"))
            state.dea9 = safe_float(latest.get("macd_dea"))
            state.latest_snapshot = IndicatorSnapshot(
                values={
                    "ma5": safe_float(latest.get("ma5")),
                    "ma20": safe_float(latest.get("ma20")),
                    "ema12": state.ema12,
                    "ema26": state.ema26,
                    "macd_dif": safe_float(latest.get("macd_dif")),
                    "macd_dea": state.dea9,
                    "macd_histogram": safe_float(latest.get("macd_histogram")),
                    "rsi14": safe_float(latest.get("rsi14")),
                    "boll_middle": safe_float(latest.get("boll_middle")),
                    "boll_upper": safe_float(latest.get("boll_upper")),
                    "boll_lower": safe_float(latest.get("boll_lower")),
                },
                provisional=False,
            )
        else:
            state.latest_snapshot = IndicatorSnapshot(
                values={
                    "ma5": state.ma5_window.mean(),
                    "ma20": state.ma20_window.mean(),
                    "ema12": None,
                    "ema26": None,
                    "macd_dif": None,
                    "macd_dea": None,
                    "macd_histogram": None,
                    "rsi14": None,
                    "boll_middle": state.boll_window.mean(),
                    "boll_upper": None,
                    "boll_lower": None,
                },
                provisional=False,
            )
        self._states[key] = state
        return state.latest_snapshot

    def update(
        self,
        key: str,
        new_bar: RuntimeBar,
        *,
        provisional: bool = True,
    ) -> IndicatorSnapshot:
        """Incrementally update indicators.

        Args:
            key: Composite key of symbol + period.
            new_bar: New bar.
            provisional: Whether this is a provisional bar.

        Returns:
            Updated indicator snapshot.
        """
        state = self._states.get(key)
        if state is None:
            state = IndicatorState()
            self._states[key] = state
        state.bars.append(new_bar)
        if new_bar.close_price is not None:
            state.ma5_window.append(new_bar.close_price)
            state.ma20_window.append(new_bar.close_price)
            state.boll_window.append(new_bar.close_price)
            state.ema12 = self._ema_next(state.ema12, new_bar.close_price, 12)
            state.ema26 = self._ema_next(state.ema26, new_bar.close_price, 26)
            dif = None
            if state.ema12 is not None and state.ema26 is not None:
                dif = state.ema12 - state.ema26
            if dif is not None:
                state.dea9 = self._ema_next(state.dea9, dif, 9)
            self._rebuild_rsi_state(state)
        values = self._build_snapshot_values(state)
        state.latest_snapshot = IndicatorSnapshot(
            values=values, provisional=provisional
        )
        return state.latest_snapshot

    def compare_with_reference(
        self,
        bars: list[RuntimeBar],
        snapshot: IndicatorSnapshot,
    ) -> dict[str, float]:
        """Compute deltas between local incremental results and OpenTrade reference.

        Args:
            bars: Historical bar list.
            snapshot: Locally computed snapshot.

        Returns:
            Delta mapping.
        """
        frame = bars_to_frame(bars)
        enriched = enrich_history_frame(frame, "basic") if not frame.empty else frame
        if enriched.empty:
            return {}
        latest = enriched.iloc[-1]
        reference: dict[str, float | None] = {
            "ma5": safe_float(latest.get("ma5")),
            "ma20": safe_float(latest.get("ma20")),
            "ema12": safe_float(latest.get("ema12")),
            "ema26": safe_float(latest.get("ema26")),
            "macd_dif": safe_float(latest.get("macd_dif")),
            "macd_dea": safe_float(latest.get("macd_dea")),
            "macd_histogram": safe_float(latest.get("macd_histogram")),
            "rsi14": safe_float(latest.get("rsi14")),
            "boll_middle": safe_float(latest.get("boll_middle")),
            "boll_upper": safe_float(latest.get("boll_upper")),
            "boll_lower": safe_float(latest.get("boll_lower")),
        }
        delta: dict[str, float] = {}
        for key, reference_value in reference.items():
            current_value = snapshot.values.get(key)
            if reference_value is None or current_value is None:
                continue
            delta[key] = abs(reference_value - current_value)
        return delta

    def latest(self, key: str) -> IndicatorSnapshot | None:
        """Return the latest snapshot."""
        state = self._states.get(key)
        return None if state is None else state.latest_snapshot

    def _rebuild_state_from_bars(self, state: IndicatorState) -> None:
        """Rebuild incremental state from current bars.

        In the current phase correctness is prioritized by rebuilding
        based on a limited window; this avoids full history recalculation
        while keeping the implementation stable.
        """
        state.ma5_window = RollingWindow(size=5)
        state.ma20_window = RollingWindow(size=20)
        state.boll_window = RollingWindow(size=20)
        state.ema12 = None
        state.ema26 = None
        state.dea9 = None
        closes = [bar.close_price for bar in state.bars if bar.close_price is not None]
        for _index, close_price in enumerate(closes):
            assert close_price is not None
            state.ma5_window.append(close_price)
            state.ma20_window.append(close_price)
            state.boll_window.append(close_price)
            state.ema12 = self._ema_next(state.ema12, close_price, 12)
            state.ema26 = self._ema_next(state.ema26, close_price, 26)
            dif = None
            if state.ema12 is not None and state.ema26 is not None:
                dif = state.ema12 - state.ema26
            if dif is not None:
                state.dea9 = self._ema_next(state.dea9, dif, 9)
        self._rebuild_rsi_state(state)

    def _rebuild_rsi_state(self, state: IndicatorState) -> None:
        """Rebuild average gain/loss state required for RSI."""
        closes = [bar.close_price for bar in state.bars if bar.close_price is not None]
        if len(closes) < 2:
            state.avg_gain = None
            state.avg_loss = None
            return
        gains: list[float] = []
        losses: list[float] = []
        for prev_close, current_close in zip(closes, closes[1:], strict=True):
            change = current_close - prev_close
            gains.append(max(change, 0.0))
            losses.append(abs(min(change, 0.0)))
        period = 14
        relevant_gains = gains[-period:]
        relevant_losses = losses[-period:]
        if not relevant_gains:
            state.avg_gain = None
            state.avg_loss = None
            return
        state.avg_gain = sum(relevant_gains) / len(relevant_gains)
        state.avg_loss = sum(relevant_losses) / len(relevant_losses)

    def _build_snapshot_values(self, state: IndicatorState) -> dict[str, float | None]:
        """Build snapshot values from current state."""
        dif = None
        histogram = None
        if state.ema12 is not None and state.ema26 is not None:
            dif = state.ema12 - state.ema26
        if dif is not None and state.dea9 is not None:
            histogram = (dif - state.dea9) * 2

        boll_middle = state.boll_window.mean()
        boll_std = state.boll_window.std()
        boll_upper = (
            None
            if boll_middle is None or boll_std is None
            else boll_middle + 2 * boll_std
        )
        boll_lower = (
            None
            if boll_middle is None or boll_std is None
            else boll_middle - 2 * boll_std
        )

        rsi14 = None
        if state.avg_gain is not None and state.avg_loss is not None:
            if state.avg_loss == 0:
                rsi14 = 100.0
            else:
                rs = state.avg_gain / state.avg_loss
                rsi14 = 100.0 - (100.0 / (1.0 + rs))

        return {
            "ma5": state.ma5_window.mean(),
            "ma20": state.ma20_window.mean(),
            "ema12": state.ema12,
            "ema26": state.ema26,
            "macd_dif": dif,
            "macd_dea": state.dea9,
            "macd_histogram": histogram,
            "rsi14": rsi14,
            "boll_middle": boll_middle,
            "boll_upper": boll_upper,
            "boll_lower": boll_lower,
        }

    def _ema_next(self, previous: float | None, value: float, period: int) -> float:
        """Compute the next EMA value."""
        alpha = 2 / (period + 1)
        if previous is None:
            return value
        return previous + alpha * (value - previous)
