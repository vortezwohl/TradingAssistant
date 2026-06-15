"""Verify basic behavior of the unified domain event model.

This file focuses on whether basic domain event types have stable defaults
and correct event categories, ensuring downstream access and aggregation
layers can depend on consistent event contracts.
"""

from __future__ import annotations

import unittest
from datetime import datetime

from tradingassistant.backend.events import (
    ConnectionEvent,
    ConnectionState,
    DepthEvent,
    KlineEvent,
    MarketEventType,
    QuoteEvent,
    TickEvent,
)


class MarketEventTests(unittest.TestCase):
    """Test domain event model."""

    def test_tick_event_sets_tick_type(self) -> None:
        """TickEvent should be fixed as tick type."""
        event = TickEvent(
            event_type=MarketEventType.CONNECTION,
            symbol="HK.00700",
            source="itick",
            price=500.0,
        )
        self.assertEqual(event.event_type, MarketEventType.TICK)
        self.assertIsInstance(event.event_time, datetime)
        self.assertIsInstance(event.received_at, datetime)

    def test_quote_event_sets_quote_type(self) -> None:
        """QuoteEvent should be fixed as quote type."""
        event = QuoteEvent(
            event_type=MarketEventType.TICK,
            symbol="US.AAPL",
            source="itick",
            last_price=201.3,
        )
        self.assertEqual(event.event_type, MarketEventType.QUOTE)

    def test_kline_event_defaults_to_provisional(self) -> None:
        """KlineEvent should default to provisional."""
        event = KlineEvent(
            event_type=MarketEventType.TICK,
            symbol="HK.00700",
            source="itick",
            period="1m",
        )
        self.assertEqual(event.event_type, MarketEventType.KLINE)
        self.assertTrue(event.provisional)

    def test_depth_event_sets_depth_type(self) -> None:
        """DepthEvent should be fixed as depth type."""
        event = DepthEvent(
            event_type=MarketEventType.QUOTE,
            symbol="HK.00700",
            source="itick",
        )
        self.assertEqual(event.event_type, MarketEventType.DEPTH)

    def test_connection_event_sets_connection_type(self) -> None:
        """ConnectionEvent should be fixed as connection type."""
        event = ConnectionEvent(
            event_type=MarketEventType.QUOTE,
            symbol="system",
            source="itick",
            state=ConnectionState.CONNECTED,
        )
        self.assertEqual(event.event_type, MarketEventType.CONNECTION)
        self.assertEqual(event.state, ConnectionState.CONNECTED)


if __name__ == "__main__":
    unittest.main()
