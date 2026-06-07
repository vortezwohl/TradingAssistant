"""定义系统内部统一使用的领域事件模型。

该模块负责屏蔽上游数据源协议差异，把原始 REST / WebSocket 数据
转换为后续模块可稳定依赖的标准化事件对象。所有下游模块都应该依赖
这里的事件类型，而不是直接解析 iTick 原始 payload。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> datetime:
    """返回当前 UTC 时间。

    Returns:
        当前带时区信息的 UTC 时间。
    """

    return datetime.now(timezone.utc)


class MarketEventType(str, Enum):
    """统一定义系统支持的领域事件类别。"""

    TICK = "tick"
    QUOTE = "quote"
    KLINE = "kline"
    DEPTH = "depth"
    CONNECTION = "connection"


class ConnectionState(str, Enum):
    """定义上游连接生命周期状态。"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


@dataclass(slots=True)
class MarketEvent:
    """所有市场事件的公共基类。

    Args:
        event_type: 事件类别。
        symbol: 统一后的标的标识。
        source: 事件来源名称，例如 `itick`。
        event_time: 事件业务时间；若未提供则使用当前 UTC 时间。
        received_at: 系统接收时间；默认使用当前 UTC 时间。
        metadata: 额外的调试或来源上下文字段。
    """

    event_type: MarketEventType
    symbol: str
    source: str
    event_time: datetime = field(default_factory=utc_now)
    received_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TickEvent(MarketEvent):
    """描述逐笔成交或逐笔驱动的事件。"""

    price: float | None = None
    volume: float | None = None
    turnover: float | None = None
    direction: str | None = None

    def __post_init__(self) -> None:
        """确保事件类型被固定为 tick。"""

        self.event_type = MarketEventType.TICK


@dataclass(slots=True)
class QuoteEvent(MarketEvent):
    """描述快照行情事件。"""

    last_price: float | None = None
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    prev_close: float | None = None
    volume: float | None = None
    turnover: float | None = None

    def __post_init__(self) -> None:
        """确保事件类型被固定为 quote。"""

        self.event_type = MarketEventType.QUOTE


@dataclass(slots=True)
class KlineEvent(MarketEvent):
    """描述 K 线更新事件。"""

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
        """确保事件类型被固定为 kline。"""

        self.event_type = MarketEventType.KLINE


@dataclass(slots=True)
class DepthEvent(MarketEvent):
    """描述盘口深度事件。"""

    bids: list[tuple[float, float]] = field(default_factory=list)
    asks: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """确保事件类型被固定为 depth。"""

        self.event_type = MarketEventType.DEPTH


@dataclass(slots=True)
class ConnectionEvent(MarketEvent):
    """描述上游连接状态事件。"""

    state: ConnectionState = ConnectionState.CONNECTING
    detail: str | None = None

    def __post_init__(self) -> None:
        """确保事件类型被固定为 connection。"""

        self.event_type = MarketEventType.CONNECTION
