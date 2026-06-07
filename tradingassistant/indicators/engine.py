"""实现指标初始化、增量更新与一致性校验。

该模块当前提供：
1. 基于 OpenTrade 的历史初始化；
2. 首批指标的增量更新状态模型；
3. provisional / finalized 输出标记；
4. 基础一致性比对工具。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import isnan
from typing import Any

import pandas as pd
from opentrade.enrichment.indicators import enrich_history_frame

from tradingassistant.charting.models import RuntimeBar


def safe_float(value: Any) -> float | None:
    """把 pandas / Python 标量安全转换为浮点数。

    Args:
        value: 原始值。

    Returns:
        浮点数；若为空或 NaN 则返回 `None`。
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
    """把运行态 K 线列表转换为 DataFrame。"""

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
    """描述单次指标输出快照。"""

    values: dict[str, float | None]
    provisional: bool

    def to_dict(self) -> dict[str, Any]:
        """返回可序列化结构。"""

        return {
            "values": self.values,
            "provisional": self.provisional,
        }


@dataclass(slots=True)
class RollingWindow:
    """用于维护窗口型指标所需的固定长度序列。"""

    size: int
    values: deque[float] = field(default_factory=deque)

    def append(self, value: float) -> None:
        """追加值并保持固定窗口长度。"""

        self.values.append(value)
        while len(self.values) > self.size:
            self.values.popleft()

    def mean(self) -> float | None:
        """返回窗口均值。"""

        if not self.values:
            return None
        return sum(self.values) / len(self.values)

    def std(self) -> float | None:
        """返回窗口标准差。"""

        if not self.values:
            return None
        mean_value = self.mean()
        assert mean_value is not None
        variance = sum((value - mean_value) ** 2 for value in self.values) / len(self.values)
        return variance ** 0.5

    def as_list(self) -> list[float]:
        """返回窗口列表副本。"""

        return list(self.values)


@dataclass(slots=True)
class IndicatorState:
    """维护单个 symbol / period 的增量指标状态。"""

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
    """实现历史初始化与增量更新的指标引擎。"""

    def __init__(self) -> None:
        """初始化指标状态映射。"""

        self._states: dict[str, IndicatorState] = {}

    def initialize(self, key: str, bars: list[RuntimeBar]) -> IndicatorSnapshot:
        """根据历史窗口初始化指标。

        Args:
            key: symbol + period 组合键。
            bars: 历史 K 线列表。

        Returns:
            初始化后的指标快照。
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
                    "macd_dea": safe_float(latest.get("macd_dea")),
                    "macd_histogram": safe_float(latest.get("macd_histogram")),
                    "rsi14": safe_float(latest.get("rsi14")),
                    "boll_middle": safe_float(latest.get("boll_middle")),
                    "boll_upper": safe_float(latest.get("boll_upper")),
                    "boll_lower": safe_float(latest.get("boll_lower")),
                },
                provisional=False,
            )
        self._states[key] = state
        if state.latest_snapshot is None:
            state.latest_snapshot = IndicatorSnapshot(values={}, provisional=False)
        self._rebuild_rsi_state(state)
        return state.latest_snapshot

    def update(self, key: str, bar: RuntimeBar, provisional: bool) -> IndicatorSnapshot:
        """根据最新 bar 增量更新指标。

        Args:
            key: symbol + period 组合键。
            bar: 最新 bar。
            provisional: 是否为 provisional 输出。

        Returns:
            增量更新后的指标快照。
        """

        state = self._states.setdefault(key, IndicatorState())
        bars = list(state.bars)
        if provisional and bars and bars[-1].bar_time == bar.bar_time:
            bars[-1] = bar
        else:
            if bars and bars[-1].bar_time == bar.bar_time:
                bars[-1] = bar
            else:
                bars.append(bar)
        state.bars = bars[-500:]
        self._rebuild_state_from_bars(state)
        snapshot = IndicatorSnapshot(
            values=self._build_snapshot_values(state),
            provisional=provisional,
        )
        state.latest_snapshot = snapshot
        self._states[key] = state
        return snapshot

    def compare_with_reference(self, bars: list[RuntimeBar], snapshot: IndicatorSnapshot) -> dict[str, float]:
        """使用 OpenTrade 作为参考结果进行对比。

        Args:
            bars: 当前历史 bar。
            snapshot: 当前增量快照。

        Returns:
            每个可比较指标的绝对误差。
        """

        frame = bars_to_frame(bars)
        if frame.empty:
            return {}
        enriched = enrich_history_frame(frame, "basic")
        latest = enriched.iloc[-1]
        reference = {
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
        """返回最新快照。"""

        state = self._states.get(key)
        return None if state is None else state.latest_snapshot

    def _rebuild_state_from_bars(self, state: IndicatorState) -> None:
        """从当前 bars 重建增量状态。

        当前阶段优先保证正确性，直接基于有限窗口重建；
        这样既能避免全量历史重算，也能保持实现稳定。
        """

        state.ma5_window = RollingWindow(size=5)
        state.ma20_window = RollingWindow(size=20)
        state.boll_window = RollingWindow(size=20)
        state.ema12 = None
        state.ema26 = None
        state.dea9 = None
        closes = [bar.close_price for bar in state.bars if bar.close_price is not None]
        for index, close_price in enumerate(closes):
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
        """重建 RSI 所需的平均涨跌幅状态。"""

        closes = [bar.close_price for bar in state.bars if bar.close_price is not None]
        if len(closes) < 2:
            state.avg_gain = None
            state.avg_loss = None
            return
        gains: list[float] = []
        losses: list[float] = []
        for prev_close, current_close in zip(closes, closes[1:]):
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
        """基于当前状态构造快照值。"""

        dif = None
        histogram = None
        if state.ema12 is not None and state.ema26 is not None:
            dif = state.ema12 - state.ema26
        if dif is not None and state.dea9 is not None:
            histogram = (dif - state.dea9) * 2

        boll_middle = state.boll_window.mean()
        boll_std = state.boll_window.std()
        boll_upper = None if boll_middle is None or boll_std is None else boll_middle + 2 * boll_std
        boll_lower = None if boll_middle is None or boll_std is None else boll_middle - 2 * boll_std

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
        """计算下一步 EMA。"""

        alpha = 2 / (period + 1)
        if previous is None:
            return value
        return previous + alpha * (value - previous)
