"""iTick REST and WebSocket access layer.

This module is responsible for:
1. Calling iTick SDK for REST queries;
2. Establishing stock WebSocket connections and managing message/error callbacks;
3. Exposing only stable Python interfaces without leaking upstream SDK thread
   and exception details.
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
    """Describe a unified iTick access layer error."""


class ITickMarketGateway:
    """Encapsulate iTick REST and WebSocket capabilities."""

    def __init__(self, token: str) -> None:
        """Initialize iTick access layer.

        Args:
            token: iTick API token.
        """
        self._client = ITickClient(token)
        self._message_handler: MessageHandler | None = None
        self._connection_handler: ConnectionHandler | None = None

    def set_message_handler(self, handler: MessageHandler) -> None:
        """Set the pre-normalization message handler.

        Args:
            handler: Callback that receives raw message dicts.
        """
        self._message_handler = handler

    def set_connection_handler(self, handler: ConnectionHandler) -> None:
        """Set the connection status event handler.

        Args:
            handler: Callback that receives connection status events.
        """
        self._connection_handler = handler

    def list_symbols(self) -> list[dict[str, Any]]:
        """Get symbol list.

        Returns:
            Raw symbol list structure.

        Raises:
            ITickGatewayError: Raised when upstream request fails.
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
        """Retrieve and normalize historical stock K-lines.

        Args:
            region: Market region.
            code: Instrument code.
            period: Period.
            limit: Maximum record count.
            end: End time.

        Returns:
            List of normalized K-line records.

        Raises:
            ITickGatewayError: Raised when upstream request fails.
        """
        try:
            rows = self._client.get_stock_kline(region, code, period, limit, end=end)
        except Exception as exc:  # noqa: BLE001
            raise ITickGatewayError(
                "Failed to fetch stock history from iTick."
            ) from exc
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
        """Connect the stock WebSocket stream and bind internal callbacks."""
        self._emit_connection(
            connection_event(state=ConnectionState.CONNECTING),
        )
        self._client.set_message_handler(self._handle_message)
        self._client.set_error_handler(self._handle_error)
        self._client.connect_stock_websocket()
        self._emit_connection(connection_event(state=ConnectionState.CONNECTED))

    def subscribe(self, request: SubscriptionRequest) -> None:
        """Send a subscription message.

        Args:
            request: Subscription request.

        Raises:
            ITickGatewayError: Raised when serialization or send fails.
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
        """Close the WebSocket connection."""
        self._client.close_websocket()
        self._emit_connection(connection_event(state=ConnectionState.CLOSED))

    def _handle_message(self, message: str) -> None:
        """Handle upstream WebSocket text messages.

        Args:
            message: Raw text message.
        """
        if self._message_handler is None:
            return
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            payload = {"type": "raw_text", "payload": message}
        self._message_handler(payload)

    def _handle_error(self, error: Exception) -> None:
        """Convert upstream errors to connection status events.

        Args:
            error: Raw exception.
        """
        self._emit_connection(
            connection_event(
                state=ConnectionState.ERROR,
                detail=str(error),
            ),
        )

    def _emit_connection(self, event: ConnectionEvent) -> None:
        """Emit a connection status event.

        Args:
            event: Connection status event.
        """
        if self._connection_handler is not None:
            self._connection_handler(event)
