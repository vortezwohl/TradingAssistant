"""Core data models for the chart pipeline.

This module centralizes:
1. Snapshot structures for chart bootstrap;
2. Runtime models for forming/closed bars;
3. Common serialization structures shared by aggregator, indicator engine,
   and transport facade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class RuntimeBar:
    """Describe a single K-line (bar) in runtime."""

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
        """Convert bar to a serializable structure.

        Returns:
            Dictionary suitable for caching or transport.
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
    """Describe a chart bootstrap snapshot."""

    topic: str
    symbol: str
    period: str
    bars: list[dict[str, Any]]
    indicators: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a serializable structure.

        Returns:
            Snapshot as a dictionary.
        """
        return {
            "topic": self.topic,
            "symbol": self.symbol,
            "period": self.period,
            "bars": self.bars,
            "indicators": self.indicators,
            "metadata": self.metadata,
        }
