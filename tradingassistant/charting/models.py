"""定义图表主链路的核心数据模型。

该模块集中承载：
1. 图表 bootstrap 所需的快照结构；
2. forming / closed bar 的运行态模型；
3. 供聚合器、指标引擎与传输门面共享的通用序列化结构。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RuntimeBar:
    """描述运行态中的一根 K 线。"""

    symbol: str
    period: str
    bar_time: datetime
    open_price: float | None
    high_price: float | None
    low_price: float | None
    close_price: float | None
    volume: float = 0.0
    turnover: float = 0.0
    provisional: bool = True

    def to_dict(self) -> dict[str, Any]:
        """把 bar 转为可序列化结构。

        Returns:
            适合缓存或传输的字典结构。
        """

        return {
            "symbol": self.symbol,
            "period": self.period,
            "bar_time": self.bar_time.isoformat(),
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "close_price": self.close_price,
            "volume": self.volume,
            "turnover": self.turnover,
            "provisional": self.provisional,
        }


@dataclass(slots=True)
class ChartSnapshot:
    """描述图表 bootstrap 快照。"""

    topic: str
    symbol: str
    period: str
    bars: list[dict[str, Any]]
    indicators: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转为可序列化结构。

        Returns:
            字典形式的快照结构。
        """

        return {
            "topic": self.topic,
            "symbol": self.symbol,
            "period": self.period,
            "bars": self.bars,
            "indicators": self.indicators,
            "metadata": self.metadata,
        }
