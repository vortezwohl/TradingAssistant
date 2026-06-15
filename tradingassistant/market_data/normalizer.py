"""实现 iTick 原始消息到领域事件的标准化转换。

该模块是接入层的核心适配器之一，负责把原始 REST / WebSocket 数据
转换为稳定的内部契约和领域事件。所有字段提取都应集中在这里，
避免协议细节扩散到服务层。
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from tradingassistant.events import (
    ConnectionEvent,
    ConnectionState,
    KlineEvent,
    QuoteEvent,
    TickEvent,
)
from tradingassistant.market_data.contracts import BarRecord, MarketSnapshot, SymbolRef


def normalize_symbol(region: str, code: str) -> str:
    """构造统一 symbol 字符串。

    Args:
        region: 市场区域。
        code: 原始代码。

    Returns:
        统一后的 `REGION.CODE` 字符串。
    """
    return SymbolRef(region=region.upper(), code=code).symbol


def parse_timestamp(value: Any) -> datetime:
    """把多种时间表达解析为 UTC 时间。

    Args:
        value: 原始时间值。

    Returns:
        解析后的 UTC 时间。
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
    """把原始值尽量转换为浮点数。

    Args:
        value: 原始值。

    Returns:
        转换后的浮点数；无法转换时返回 `None`。
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
    """把单条历史 K 线记录转换为标准化契约。

    Args:
        region: 市场区域。
        code: 标的代码。
        period: K 线周期。
        payload: 原始记录。

    Returns:
        标准化后的 K 线记录。
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
    """把快照行情 payload 转换为标准化快照。

    Args:
        region: 市场区域。
        code: 标的代码。
        payload: 原始 payload。

    Returns:
        标准化后的快照行情。
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
    """由原始 quote payload 构造 QuoteEvent。

    Args:
        region: 市场区域。
        code: 标的代码。
        payload: 原始 payload。
        source: 来源名称。

    Returns:
        标准化后的 QuoteEvent。
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
    """由原始 tick payload 构造 TickEvent。"""
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
    """由标准化 K 线记录构造 KlineEvent。"""
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
    """构造连接状态事件。"""
    return ConnectionEvent(
        event_type=ConnectionEvent.__dataclass_fields__["event_type"].default,  # type: ignore[index]
        symbol="system",
        source=source,
        state=state,
        detail=detail,
    )


def serializable_bar(bar: BarRecord) -> dict[str, Any]:
    """把标准化 K 线记录转换为可序列化结构。

    Args:
        bar: 标准化 K 线记录。

    Returns:
        适合缓存或传输的字典结构。
    """
    payload = asdict(bar)
    payload["bar_time"] = bar.bar_time.isoformat()
    return payload
