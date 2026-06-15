"""定义市场数据接入层使用的输入输出契约。

该模块用于承载上游原始数据到系统内部结构之间的中间契约，包括：
1. 标准化后的 symbol 表示；
2. 统一的历史 bar 记录；
3. WebSocket 订阅与消息封装。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True, frozen=True)
class SymbolRef:
    """描述统一后的标的引用。

    Args:
        region: 市场区域，例如 `HK`、`US`。
        code: 原始代码，例如 `00700`、`AAPL`。
    """

    region: str
    code: str

    @property
    def symbol(self) -> str:
        """返回统一 symbol 表示。

        Returns:
            `REGION.CODE` 形式的字符串。
        """
        return f"{self.region}.{self.code}"


@dataclass(slots=True)
class BarRecord:
    """描述标准化后的 K 线记录。"""

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
    """描述标准化后的快照行情。"""

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
    """描述 WebSocket 订阅请求。"""

    topic: str
    symbols: list[str]
    extra: dict[str, Any] = field(default_factory=dict)
