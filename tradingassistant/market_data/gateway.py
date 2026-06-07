"""封装 iTick REST 与 WebSocket 接入层。

该模块负责：
1. 调用 iTick SDK 完成 REST 查询；
2. 建立股票 WebSocket 连接并管理消息/错误回调；
3. 对外只暴露稳定的 Python 接口，不泄漏上游 SDK 的线程与异常细节。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from itick.sdk import Client as ITickClient

from tradingassistant.events import ConnectionEvent, ConnectionState
from tradingassistant.market_data.contracts import BarRecord, SubscriptionRequest
from tradingassistant.market_data.normalizer import (
    connection_event,
    normalize_history_bar,
)


MessageHandler = Callable[[dict[str, Any]], None]
ConnectionHandler = Callable[[ConnectionEvent], None]


class ITickGatewayError(RuntimeError):
    """描述 iTick 接入层统一错误。"""


class ITickMarketGateway:
    """封装 iTick 的 REST 与 WebSocket 能力。"""

    def __init__(self, token: str) -> None:
        """初始化 iTick 接入层。

        Args:
            token: iTick API token。
        """

        self._client = ITickClient(token)
        self._message_handler: MessageHandler | None = None
        self._connection_handler: ConnectionHandler | None = None

    def set_message_handler(self, handler: MessageHandler) -> None:
        """设置标准化前的消息处理函数。

        Args:
            handler: 接收原始消息字典的回调。
        """

        self._message_handler = handler

    def set_connection_handler(self, handler: ConnectionHandler) -> None:
        """设置连接状态事件处理函数。

        Args:
            handler: 接收连接状态事件的回调。
        """

        self._connection_handler = handler

    def list_symbols(self) -> list[dict[str, Any]]:
        """获取 symbol 列表。

        Returns:
            原始 symbol 列表结构。

        Raises:
            ITickGatewayError: 当上游请求失败时抛出。
        """

        try:
            data = self._client.get_symbol_list()
        except Exception as exc:  # noqa: BLE001
            raise ITickGatewayError("Failed to fetch symbol list from iTick.") from exc
        return data or []

    def get_stock_history(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ) -> list[BarRecord]:
        """获取并标准化股票历史 K 线。

        Args:
            region: 市场区域。
            code: 标的代码。
            period: 周期。
            limit: 最大记录数。
            end: 截止时间。

        Returns:
            标准化后的 K 线列表。

        Raises:
            ITickGatewayError: 当上游请求失败时抛出。
        """

        try:
            rows = self._client.get_stock_kline(region, code, period, limit, end=end)
        except Exception as exc:  # noqa: BLE001
            raise ITickGatewayError("Failed to fetch stock history from iTick.") from exc
        return [
            normalize_history_bar(
                region=region,
                code=code,
                period=period,
                payload=row,
            )
            for row in (rows or [])
        ]

    def connect_stock_stream(self) -> None:
        """连接股票 WebSocket 流并绑定内部回调。"""

        self._emit_connection(
            connection_event(state=ConnectionState.CONNECTING),
        )
        self._client.set_message_handler(self._handle_message)
        self._client.set_error_handler(self._handle_error)
        self._client.connect_stock_websocket()
        self._emit_connection(connection_event(state=ConnectionState.CONNECTED))

    def subscribe(self, request: SubscriptionRequest) -> None:
        """发送订阅消息。

        Args:
            request: 订阅请求。

        Raises:
            ITickGatewayError: 当序列化或发送失败时抛出。
        """

        payload = {
            "ac": "subscribe",
            "params": request.symbols,
            "types": [request.topic],
            **request.extra,
        }
        try:
            self._client.send_websocket_message(json.dumps(payload))
        except Exception as exc:  # noqa: BLE001
            raise ITickGatewayError("Failed to send subscription to iTick.") from exc

    def close(self) -> None:
        """关闭 WebSocket 连接。"""

        self._client.close_websocket()
        self._emit_connection(connection_event(state=ConnectionState.CLOSED))

    def _handle_message(self, message: str) -> None:
        """处理上游 WebSocket 文本消息。

        Args:
            message: 原始文本消息。
        """

        if self._message_handler is None:
            return
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            payload = {"type": "raw_text", "payload": message}
        self._message_handler(payload)

    def _handle_error(self, error: Exception) -> None:
        """把上游错误转换为连接状态事件。

        Args:
            error: 原始异常。
        """

        self._emit_connection(
            connection_event(
                state=ConnectionState.ERROR,
                detail=str(error),
            ),
        )

    def _emit_connection(self, event: ConnectionEvent) -> None:
        """向外发出连接状态事件。

        Args:
            event: 连接状态事件。
        """

        if self._connection_handler is not None:
            self._connection_handler(event)
