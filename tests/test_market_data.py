"""Verify market data access layer and normalization logic.

This file focuses on:
1. Conversion of raw payloads to normalized contracts / domain events;
2. iTick gateway encapsulation behavior for REST queries, WebSocket
   messages, and error events.
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from tradingassistant.events import ConnectionState
from tradingassistant.market_data.contracts import SubscriptionRequest
from tradingassistant.market_data.gateway import ITickGatewayError, ITickMarketGateway
from tradingassistant.market_data.normalizer import (
    connection_event,
    kline_event_from_bar,
    normalize_history_bar,
    normalize_quote_payload,
    normalize_symbol,
    quote_event_from_payload,
    tick_event_from_payload,
)


class NormalizerTests(unittest.TestCase):
    """Test normalization logic."""

    def test_normalize_symbol_formats_region_and_code(self) -> None:
        """symbol should normalize to REGION.CODE."""
        self.assertEqual(normalize_symbol("hk", "00700"), "HK.00700")

    def test_normalize_history_bar_maps_ohlcv_fields(self) -> None:
        """Historical K-line fields should be correctly extracted."""
        bar = normalize_history_bar(
            region="HK",
            code="00700",
            period="1m",
            payload={
                "t": 1710000000,
                "o": "500",
                "h": "505",
                "l": "498",
                "c": "503",
                "v": "1000",
                "tu": "503000",
            },
        )
        self.assertEqual(bar.symbol, "HK.00700")
        self.assertEqual(bar.period, "1m")
        self.assertEqual(bar.open_price, 500.0)
        self.assertEqual(bar.close_price, 503.0)
        self.assertEqual(bar.volume, 1000.0)

    def test_quote_event_from_payload_creates_domain_event(self) -> None:
        """Quote payload should be converted to QuoteEvent."""
        event = quote_event_from_payload(
            region="US",
            code="AAPL",
            payload={
                "t": 1710000000,
                "ld": "201.2",
                "o": "200.0",
                "h": "202.5",
                "l": "199.8",
                "p": "198.6",
                "v": "2000",
                "tu": "402400",
            },
        )
        self.assertEqual(event.symbol, "US.AAPL")
        self.assertEqual(event.last_price, 201.2)
        self.assertEqual(event.prev_close, 198.6)

    def test_tick_event_from_payload_creates_domain_event(self) -> None:
        """Tick payload should be converted to TickEvent."""
        event = tick_event_from_payload(
            region="HK",
            code="00700",
            payload={
                "t": 1710000000,
                "p": "503.2",
                "v": "100",
                "tu": "50320",
                "d": "buy",
            },
        )
        self.assertEqual(event.symbol, "HK.00700")
        self.assertEqual(event.price, 503.2)
        self.assertEqual(event.direction, "buy")

    def test_kline_event_from_bar_marks_provisional_flag(self) -> None:
        """KlineEvent should carry bar info and set provisional flag."""
        bar = normalize_history_bar(
            region="HK",
            code="00700",
            period="5m",
            payload={
                "t": 1710000000,
                "o": "500",
                "h": "505",
                "l": "498",
                "c": "503",
            },
        )
        event = kline_event_from_bar(bar=bar, provisional=True)
        self.assertEqual(event.symbol, "HK.00700")
        self.assertEqual(event.period, "5m")
        self.assertTrue(event.provisional)

    def test_connection_event_wraps_state(self) -> None:
        """Connection status event should preserve state and detail."""
        event = connection_event(
            state=ConnectionState.RECONNECTING,
            detail="retrying",
        )
        self.assertEqual(event.state, ConnectionState.RECONNECTING)
        self.assertEqual(event.detail, "retrying")

    def test_normalize_quote_payload_maps_fields(self) -> None:
        """Raw snapshot should be mapped to unified structure."""
        snapshot = normalize_quote_payload(
            region="HK",
            code="00700",
            payload={
                "t": 1710000000,
                "ld": "503.2",
                "o": "500.1",
                "h": "505.0",
                "l": "498.8",
                "p": "497.5",
                "v": "1200",
                "tu": "603840",
            },
        )
        self.assertEqual(snapshot.symbol, "HK.00700")
        self.assertEqual(snapshot.last_price, 503.2)
        self.assertEqual(snapshot.turnover, 603840.0)


class FakeITickClient:
    """Fake iTick client for gateway testing."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.message_handler = None
        self.error_handler = None
        self.connected = False
        self.sent_messages: list[str] = []

    def get_symbol_list(self) -> list[dict[str, str]]:
        """Return fake symbol list."""
        return [{"region": "HK", "code": "00700"}]

    def get_stock_kline(
        self,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ) -> list[dict[str, str]]:
        """Return fake historical K-lines."""
        return [
            {
                "t": 1710000000,
                "o": "500",
                "h": "505",
                "l": "498",
                "c": "503",
                "v": "1000",
                "tu": "503000",
            }
        ]

    def set_message_handler(self, handler) -> None:
        """Record message handler callback."""
        self.message_handler = handler

    def set_error_handler(self, handler) -> None:
        """Record error handler callback."""
        self.error_handler = handler

    def connect_stock_websocket(self) -> None:
        """Mark as connected."""
        self.connected = True

    def send_websocket_message(self, message: str) -> None:
        """Record sent content."""
        self.sent_messages.append(message)

    def close_websocket(self) -> None:
        """Mark connection as closed."""
        self.connected = False


class BrokenITickClient(FakeITickClient):
    """Fake client for testing error paths."""

    def get_symbol_list(self) -> list[dict[str, str]]:
        """Raise an exception."""
        raise RuntimeError("boom")


class ITickMarketGatewayTests(unittest.TestCase):
    """Test iTick access layer."""

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_list_symbols_returns_data(self) -> None:
        """Symbol query should return upstream data."""
        gateway = ITickMarketGateway("demo-token")
        self.assertEqual(gateway.list_symbols(), [{"region": "HK", "code": "00700"}])

    @patch("tradingassistant.market_data.gateway.ITickClient", BrokenITickClient)
    def test_list_symbols_wraps_upstream_error(self) -> None:
        """Upstream exception should be wrapped as unified error."""
        gateway = ITickMarketGateway("demo-token")
        with self.assertRaises(ITickGatewayError):
            gateway.list_symbols()

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_get_stock_history_returns_normalized_bars(self) -> None:
        """Historical K-lines should be output in normalized form."""
        gateway = ITickMarketGateway("demo-token")
        bars = gateway.get_stock_history(
            region="HK",
            code="00700",
            period="1m",
            limit=10,
        )
        self.assertEqual(len(bars), 1)
        self.assertEqual(bars[0].symbol, "HK.00700")
        self.assertEqual(bars[0].close_price, 503.0)

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_connect_stock_stream_emits_connection_events(self) -> None:
        """Should emit connecting and connected states when connecting stock stream."""
        events = []
        gateway = ITickMarketGateway("demo-token")
        gateway.set_connection_handler(events.append)
        gateway.connect_stock_stream()
        self.assertEqual(events[0].state, ConnectionState.CONNECTING)
        self.assertEqual(events[1].state, ConnectionState.CONNECTED)

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_subscribe_serializes_request(self) -> None:
        """Subscription message should be serialized before sending."""
        gateway = ITickMarketGateway("demo-token")
        gateway.subscribe(
            SubscriptionRequest(
                topic="quote",
                symbols=["HK.00700", "US.AAPL"],
            ),
        )
        payload = json.loads(gateway._client.sent_messages[0])  # noqa: SLF001
        self.assertEqual(payload["ac"], "subscribe")
        self.assertEqual(payload["types"], ["quote"])
        self.assertEqual(payload["params"], ["HK.00700", "US.AAPL"])

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_handle_message_decodes_json_before_callback(self) -> None:
        """Message callback should receive decoded dict."""
        received = []
        gateway = ITickMarketGateway("demo-token")
        gateway.set_message_handler(received.append)
        gateway._handle_message('{"topic":"quote","data":{"code":"00700"}}')  # noqa: SLF001
        self.assertEqual(received[0]["topic"], "quote")

    @patch("tradingassistant.market_data.gateway.ITickClient", FakeITickClient)
    def test_handle_error_emits_connection_error_event(self) -> None:
        """Error callback should be converted to connection status event."""
        received = []
        gateway = ITickMarketGateway("demo-token")
        gateway.set_connection_handler(received.append)
        gateway._handle_error(RuntimeError("bad stream"))  # noqa: SLF001
        self.assertEqual(received[0].state, ConnectionState.ERROR)
        self.assertEqual(received[0].detail, "bad stream")


if __name__ == "__main__":
    unittest.main()
