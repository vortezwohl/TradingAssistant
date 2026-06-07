"""实现 forming bar 与多周期聚合逻辑。

该模块是实时图表主链路的核心：
1. 根据 tick / quote 更新 forming 1m bar；
2. 在分钟边界闭合当前 bar；
3. 从闭合后的 1m bar 聚合高周期 bar。
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from tradingassistant.events import KlineEvent, QuoteEvent, TickEvent
from tradingassistant.market_data.contracts import BarRecord

from .models import RuntimeBar

SUPPORTED_PERIODS = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
}


def floor_to_minute(dt: datetime, step_minutes: int = 1) -> datetime:
    """把时间归整到分钟边界。

    Args:
        dt: 原始时间。
        step_minutes: 分钟粒度。

    Returns:
        向下取整后的分钟时间。
    """

    base = dt.astimezone(timezone.utc).replace(second=0, microsecond=0)
    minute = (base.minute // step_minutes) * step_minutes
    return base.replace(minute=minute)


@dataclass(slots=True)
class BarAggregator:
    """维护 forming bar 与 closed bar，并支持高周期聚合。"""

    _forming_bars: dict[str, RuntimeBar] = field(default_factory=dict)
    _closed_bars: dict[str, list[RuntimeBar]] = field(
        default_factory=lambda: defaultdict(list),
    )

    def update_from_tick(self, event: TickEvent) -> RuntimeBar:
        """用 TickEvent 更新 forming 1m bar。

        Args:
            event: Tick 事件。

        Returns:
            更新后的 forming 1m bar。
        """

        return self._update_forming_bar(
            symbol=event.symbol,
            event_time=event.event_time,
            price=event.price,
            volume_delta=event.volume or 0.0,
            turnover_delta=event.turnover or 0.0,
        )

    def update_from_quote(self, event: QuoteEvent) -> RuntimeBar:
        """用 QuoteEvent 更新 forming 1m bar。

        Args:
            event: Quote 事件。

        Returns:
            更新后的 forming 1m bar。
        """

        return self._update_forming_bar(
            symbol=event.symbol,
            event_time=event.event_time,
            price=event.last_price,
            volume_delta=0.0,
            turnover_delta=0.0,
        )

    def finalize_due_bars(self, now: datetime) -> list[RuntimeBar]:
        """闭合所有已经跨过分钟边界的 forming 1m bar。

        Args:
            now: 当前时间。

        Returns:
            被闭合的 bar 列表。
        """

        finalized: list[RuntimeBar] = []
        current_minute = floor_to_minute(now)
        for symbol, bar in list(self._forming_bars.items()):
            if bar.bar_time < current_minute:
                bar.provisional = False
                finalized.append(bar)
                self._closed_bars[symbol].append(bar)
                self._forming_bars.pop(symbol, None)
        return finalized

    def aggregate_period(self, symbol: str, period: str) -> list[RuntimeBar]:
        """把闭合后的 1m bar 聚合为更高周期。

        Args:
            symbol: 统一 symbol。
            period: 目标周期。

        Returns:
            聚合后的 bar 列表；若周期为 `1m` 则直接返回闭合 1m bar。
        """

        if period not in SUPPORTED_PERIODS:
            raise ValueError(f"Unsupported period: {period}")
        base_bars = self._closed_bars.get(symbol, [])
        if period == "1m":
            return list(base_bars)

        step = SUPPORTED_PERIODS[period]
        grouped: list[RuntimeBar] = []
        buckets: dict[datetime, list[RuntimeBar]] = defaultdict(list)
        for bar in base_bars:
            bucket_time = floor_to_minute(bar.bar_time, step_minutes=step)
            buckets[bucket_time].append(bar)

        for bucket_time in sorted(buckets):
            grouped.append(self._merge_bars(symbol, period, bucket_time, buckets[bucket_time]))
        return grouped

    def forming_bar(self, symbol: str) -> RuntimeBar | None:
        """返回当前 forming 1m bar。"""

        return self._forming_bars.get(symbol)

    def closed_bars(self, symbol: str) -> list[RuntimeBar]:
        """返回闭合后的 1m bar。"""

        return list(self._closed_bars.get(symbol, []))

    def _update_forming_bar(
        self,
        *,
        symbol: str,
        event_time: datetime,
        price: float | None,
        volume_delta: float,
        turnover_delta: float,
    ) -> RuntimeBar:
        """更新 forming 1m bar 的内部实现。"""

        bar_time = floor_to_minute(event_time)
        current = self._forming_bars.get(symbol)
        if current is None or current.bar_time != bar_time:
            current = RuntimeBar(
                symbol=symbol,
                period="1m",
                bar_time=bar_time,
                open_price=price,
                high_price=price,
                low_price=price,
                close_price=price,
                volume=volume_delta,
                turnover=turnover_delta,
                provisional=True,
            )
            self._forming_bars[symbol] = current
            return current

        if price is not None:
            if current.open_price is None:
                current.open_price = price
            current.close_price = price
            current.high_price = (
                price if current.high_price is None else max(current.high_price, price)
            )
            current.low_price = (
                price if current.low_price is None else min(current.low_price, price)
            )
        current.volume += volume_delta
        current.turnover += turnover_delta
        return current

    def _merge_bars(
        self,
        symbol: str,
        period: str,
        bucket_time: datetime,
        bars: list[RuntimeBar],
    ) -> RuntimeBar:
        """把一组 1m bar 聚合成更高周期 bar。"""

        bars = sorted(bars, key=lambda item: item.bar_time)
        open_price = bars[0].open_price
        close_price = bars[-1].close_price
        high_price = max(bar.high_price or float("-inf") for bar in bars)
        low_price = min(bar.low_price or float("inf") for bar in bars)
        return RuntimeBar(
            symbol=symbol,
            period=period,
            bar_time=bucket_time,
            open_price=open_price,
            high_price=None if high_price == float("-inf") else high_price,
            low_price=None if low_price == float("inf") else low_price,
            close_price=close_price,
            volume=sum(bar.volume for bar in bars),
            turnover=sum(bar.turnover for bar in bars),
            provisional=False,
        )
