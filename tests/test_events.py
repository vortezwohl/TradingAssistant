"""验证统一领域事件模型的基础行为。

该文件聚焦基础领域事件类型是否具备稳定默认值和正确事件类别，
以确保后续接入层与聚合层都能依赖一致的事件契约。
"""

from __future__ import annotations

import unittest
from datetime import datetime

from tradingassistant.events import (
    ConnectionEvent,
    ConnectionState,
    DepthEvent,
    KlineEvent,
    MarketEventType,
    QuoteEvent,
    TickEvent,
)


class MarketEventTests(unittest.TestCase):
    """验证领域事件模型。"""

    def test_tick_event_sets_tick_type(self) -> None:
        """TickEvent 应固定为 tick 类型。"""
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
        """QuoteEvent 应固定为 quote 类型。"""
        event = QuoteEvent(
            event_type=MarketEventType.TICK,
            symbol="US.AAPL",
            source="itick",
            last_price=201.3,
        )
        self.assertEqual(event.event_type, MarketEventType.QUOTE)

    def test_kline_event_defaults_to_provisional(self) -> None:
        """KlineEvent 默认应标记为 provisional。"""
        event = KlineEvent(
            event_type=MarketEventType.TICK,
            symbol="HK.00700",
            source="itick",
            period="1m",
        )
        self.assertEqual(event.event_type, MarketEventType.KLINE)
        self.assertTrue(event.provisional)

    def test_depth_event_sets_depth_type(self) -> None:
        """DepthEvent 应固定为 depth 类型。"""
        event = DepthEvent(
            event_type=MarketEventType.QUOTE,
            symbol="HK.00700",
            source="itick",
        )
        self.assertEqual(event.event_type, MarketEventType.DEPTH)

    def test_connection_event_sets_connection_type(self) -> None:
        """ConnectionEvent 应固定为 connection 类型。"""
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
