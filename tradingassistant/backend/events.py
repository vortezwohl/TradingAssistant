"""Unified domain event model for internal system use.

This module abstracts upstream data source protocol differences and converts
raw REST/WebSocket data into standardized event objects that downstream
modules can reliably depend on. All downstream modules should depend on
the event types defined here, rather than directly parsing raw iTick payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC time.

    Returns:
        Current UTC time with timezone info.
    """
    return datetime.now(timezone.utc)


class MarketEventType(str, Enum):
    """Unified domain event type categories supported by the system."""

    TICK = "tick"
    QUOTE = "quote"
    KLINE = "kline"
    DEPTH = "depth"
    CONNECTION = "connection"


class ConnectionState(str, Enum):
    """Define upstream connection lifecycle states."""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


@dataclass(slots=True)
class MarketEvent:
    """Common base class for all market events.

    Args:
        event_type: Event category.
        symbol: Normalized instrument identifier.
        source: Event source name, e.g. `itick`.
        event_time: Business time of the event; defaults to current UTC time.
        received_at: System receive time; defaults to current UTC time.
        metadata: Additional debug or source context fields.
    """

    event_type: MarketEventType
    symbol: str
    source: str
    event_time: datetime = field(default_factory=utc_now)
    received_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TickEvent(MarketEvent):
    """Describe a tick-by-tick trade or order-driven event."""

    price: float | None = None
    volume: float | None = None
    turnover: float | None = None
    direction: str | None = None

    def __post_init__(self) -> None:
        """Ensure event type is fixed to tick."""
        self.event_type = MarketEventType.TICK


@dataclass(slots=True)
class QuoteEvent(MarketEvent):
    """Describe a snapshot quote event."""

    last_price: float | None = None
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    prev_close: float | None = None
    volume: float | None = None
    turnover: float | None = None

    def __post_init__(self) -> None:
        """Ensure event type is fixed to quote."""
        self.event_type = MarketEventType.QUOTE


@dataclass(slots=True)
class KlineEvent(MarketEvent):
    """Describe a K-line (candlestick) update event."""

    period: str = "1m"
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    close_price: float | None = None
    volume: float | None = None
    turnover: float | None = None
    bar_time: datetime | None = None
    provisional: bool = True

    def __post_init__(self) -> None:
        """Ensure event type is fixed to kline."""
        self.event_type = MarketEventType.KLINE


@dataclass(slots=True)
class DepthEvent(MarketEvent):
    """Describe a depth-of-market event."""

    bids: list[tuple[float, float]] = field(default_factory=list)
    asks: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure event type is fixed to depth."""
        self.event_type = MarketEventType.DEPTH


@dataclass(slots=True)
class ConnectionEvent(MarketEvent):
    """Describe an upstream connection status event."""

    state: ConnectionState = ConnectionState.CONNECTING
    detail: str | None = None

    def __post_init__(self) -> None:
        """Ensure event type is fixed to connection."""
        self.event_type = MarketEventType.CONNECTION
