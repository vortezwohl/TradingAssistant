"""Input/output contracts for the market data access layer.

This module carries intermediate contracts between upstream raw data and
system-internal structures, including:
1. Normalized symbol representation;
2. Unified historical bar records;
3. WebSocket subscription and message encapsulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class SymbolRef:
    """Describe a normalized instrument reference.

    Args:
        region: Market region, e.g. `HK`, `US`.
        code: Raw code, e.g. `00700`, `AAPL`.
    """

    region: str
    code: str

    @property
    def symbol(self) -> str:
        """Return normalized symbol representation.

        Returns:
            String in `REGION.CODE` form.
        """
        return f"{self.region}.{self.code}"


@dataclass(slots=True)
class BarRecord:
    """Describe a normalized K-line record."""

    symbol: str
    period: str
    bar_time: datetime
    open_price: float | None
    high_price: float | None
    low_price: float | None
    close_price: float | None
    volume: float | None = None
    turnover: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MarketSnapshot:
    """Describe a normalized snapshot quote."""

    symbol: str
    last_price: float | None
    open_price: float | None
    high_price: float | None
    low_price: float | None
    prev_close: float | None
    volume: float | None = None
    turnover: float | None = None
    event_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SubscriptionRequest:
    """Describe a WebSocket subscription request."""

    topic: str
    symbols: list[str]
    extra: dict[str, Any] = field(default_factory=dict)
