"""Normalize iTick raw messages into domain events.

This module is one of the core adapters in the access layer, responsible for
converting raw REST/WebSocket data into stable internal contracts and domain
events. All field extraction should be centralized here to prevent protocol
details from leaking into the service layer.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from tradingassistant.backend.events import (
    ConnectionEvent,
    ConnectionState,
    KlineEvent,
    QuoteEvent,
    TickEvent,
)
from tradingassistant.backend.market_data.contracts import (
    BarRecord,
    MarketSnapshot,
    SymbolRef,
)


def normalize_symbol(region: str, code: str) -> str:
    """Build a unified symbol string.

    Args:
        region: Market region.
        code: Raw code.

    Returns:
        Normalized `REGION.CODE` string.
    """
    return SymbolRef(region=region.upper(), code=code).symbol


def parse_timestamp(value: Any) -> datetime:
    """Parse various time representations to UTC datetime.

    Args:
        value: Raw time value.

    Returns:
        Parsed UTC datetime.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return datetime.fromtimestamp(int(text), tz=timezone.utc)
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now(timezone.utc)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def to_float(value: Any) -> float | None:
    """Convert raw value to float when possible.

    Args:
        value: Raw value.

    Returns:
        Converted float; returns `None` when conversion fails.
    """
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_history_bar(
    *,
    region: str,
    code: str,
    period: str,
    payload: dict[str, Any],
) -> BarRecord:
    """Convert a single historical K-line record to a normalized contract.

    Args:
        region: Market region.
        code: Instrument code.
        period: K-line period.
        payload: Raw record.

    Returns:
        Normalized K-line record.
    """
    symbol = normalize_symbol(region, code)
    return BarRecord(
        symbol=symbol,
        period=period,
        bar_time=parse_timestamp(payload.get("t") or payload.get("time")),
        open_price=to_float(payload.get("o") or payload.get("open")),
        high_price=to_float(payload.get("h") or payload.get("high")),
        low_price=to_float(payload.get("l") or payload.get("low")),
        close_price=to_float(payload.get("c") or payload.get("close")),
        volume=to_float(payload.get("v") or payload.get("volume")),
        turnover=to_float(payload.get("tu") or payload.get("turnover")),
        metadata={"raw": payload},
    )


def normalize_quote_payload(
    *,
    region: str,
    code: str,
    payload: dict[str, Any],
) -> MarketSnapshot:
    """Convert a quote snapshot payload to a normalized snapshot.

    Args:
        region: Market region.
        code: Instrument code.
        payload: Raw payload.

    Returns:
        Normalized snapshot quote.
    """
    symbol = normalize_symbol(region, code)
    return MarketSnapshot(
        symbol=symbol,
        last_price=to_float(payload.get("ld") or payload.get("price")),
        open_price=to_float(payload.get("o") or payload.get("open")),
        high_price=to_float(payload.get("h") or payload.get("high")),
        low_price=to_float(payload.get("l") or payload.get("low")),
        prev_close=to_float(payload.get("p") or payload.get("prev_close")),
        volume=to_float(payload.get("v") or payload.get("volume")),
        turnover=to_float(payload.get("tu") or payload.get("turnover")),
        event_time=parse_timestamp(payload.get("t") or payload.get("time")),
        metadata={"raw": payload},
    )


def quote_event_from_payload(
    *,
    region: str,
    code: str,
    payload: dict[str, Any],
    source: str = "itick",
) -> QuoteEvent:
    """Build a QuoteEvent from raw quote payload.

    Args:
        region: Market region.
        code: Instrument code.
        payload: Raw payload.
        source: Source name.

    Returns:
        Normalized QuoteEvent.
    """
    snapshot = normalize_quote_payload(region=region, code=code, payload=payload)
    return QuoteEvent(
        event_type=QuoteEvent.__dataclass_fields__["event_type"].default,  # type: ignore[index]
        symbol=snapshot.symbol,
        source=source,
        event_time=snapshot.event_time or datetime.now(timezone.utc),
        last_price=snapshot.last_price,
        open_price=snapshot.open_price,
        high_price=snapshot.high_price,
        low_price=snapshot.low_price,
        prev_close=snapshot.prev_close,
        volume=snapshot.volume,
        turnover=snapshot.turnover,
        metadata=snapshot.metadata,
    )


def tick_event_from_payload(
    *,
    region: str,
    code: str,
    payload: dict[str, Any],
    source: str = "itick",
) -> TickEvent:
    """Build a TickEvent from raw tick payload."""
    return TickEvent(
        event_type=TickEvent.__dataclass_fields__["event_type"].default,  # type: ignore[index]
        symbol=normalize_symbol(region, code),
        source=source,
        event_time=parse_timestamp(payload.get("t") or payload.get("time")),
        price=to_float(payload.get("p") or payload.get("price")),
        volume=to_float(payload.get("v") or payload.get("volume")),
        turnover=to_float(payload.get("tu") or payload.get("turnover")),
        direction=str(payload.get("d")) if payload.get("d") is not None else None,
        metadata={"raw": payload},
    )


def kline_event_from_bar(
    *,
    bar: BarRecord,
    source: str = "itick",
    provisional: bool = False,
) -> KlineEvent:
    """Build a KlineEvent from a normalized K-line record."""
    return KlineEvent(
        event_type=KlineEvent.__dataclass_fields__["event_type"].default,  # type: ignore[index]
        symbol=bar.symbol,
        source=source,
        event_time=bar.bar_time,
        period=bar.period,
        open_price=bar.open_price,
        high_price=bar.high_price,
        low_price=bar.low_price,
        close_price=bar.close_price,
        volume=bar.volume,
        turnover=bar.turnover,
        bar_time=bar.bar_time,
        provisional=provisional,
        metadata=bar.metadata,
    )


def connection_event(
    *,
    state: ConnectionState,
    detail: str | None = None,
    source: str = "itick",
) -> ConnectionEvent:
    """Build a connection status event."""
    return ConnectionEvent(
        event_type=ConnectionEvent.__dataclass_fields__["event_type"].default,  # type: ignore[index]
        symbol="system",
        source=source,
        state=state,
        detail=detail,
    )


def serializable_bar(bar: BarRecord) -> dict[str, Any]:
    """Convert a normalized K-line record to a serializable structure.

    Args:
        bar: Normalized K-line record.

    Returns:
        Dictionary suitable for caching or transport.
    """
    payload = asdict(bar)
    payload["bar_time"] = bar.bar_time.isoformat()
    return payload
