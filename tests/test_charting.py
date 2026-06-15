"""Verify history backfill and K-line aggregation main pipeline.

This file covers:
1. Cache-hit-prioritized history backfill with MemoryCacheStore;
2. Forming / closed 1m bars;
3. Aggregating 1m bars into higher-period bars.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from tradingassistant.backend.charting.aggregator import BarAggregator
from tradingassistant.backend.charting.history import HistoryBackfillService
from tradingassistant.backend.events import QuoteEvent, TickEvent
from tradingassistant.backend.infrastructure.cache import MemoryCacheStore
from tradingassistant.backend.market_data.contracts import BarRecord


class FakeHistoryGateway:
    """Fake gateway for testing history backfill."""

    def __init__(self) -> None:
        self.calls = 0

    def get_stock_history(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
    ) -> list[BarRecord]:
        self.calls += 1
        base_time = datetime(2026, 6, 7, 9, 30, tzinfo=timezone.utc)
        return [
            BarRecord(
                symbol=f"{region}.{code}",
                period=period,
                bar_time=base_time + timedelta(minutes=index),
                open_price=500.0 + index,
                high_price=501.0 + index,
                low_price=499.0 + index,
                close_price=500.5 + index,
                volume=1000 + index,
                turnover=500000 + index,
            )
            for index in range(limit)
        ]


class HistoryBackfillServiceTests(unittest.TestCase):
    """Test history backfill service."""

    def test_cache_is_used_before_gateway(self) -> None:
        """A second call with the same request should hit the cache."""
        gateway = FakeHistoryGateway()
        cache = MemoryCacheStore()
        service = HistoryBackfillService(gateway=gateway, cache_store=cache)
        first = service.get_bars(region="HK", code="00700", period="1m", limit=2)
        second = service.get_bars(region="HK", code="00700", period="1m", limit=2)
        self.assertEqual(len(first), 2)
        self.assertEqual(len(second), 2)
        self.assertEqual(gateway.calls, 1)


class BarAggregatorTests(unittest.TestCase):
    """Test forming/closed bar and aggregation logic."""

    def test_tick_updates_forming_bar(self) -> None:
        """Tick should update forming 1m bar price and volume."""
        aggregator = BarAggregator()
        event = TickEvent(
            event_type=None,  # type: ignore[arg-type]
            symbol="HK.00700",
            source="itick",
            event_time=datetime(2026, 6, 7, 9, 30, 10, tzinfo=timezone.utc),
            price=500.0,
            volume=100.0,
            turnover=50000.0,
        )
        bar = aggregator.update_from_tick(event)
        self.assertEqual(bar.open_price, 500.0)
        self.assertEqual(bar.close_price, 500.0)
        self.assertEqual(bar.volume, 100.0)

    def test_quote_updates_same_forming_bar(self) -> None:
        """Quote in the same minute should update the same forming bar."""
        aggregator = BarAggregator()
        aggregator.update_from_tick(
            TickEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 30, 10, tzinfo=timezone.utc),
                price=500.0,
                volume=100.0,
                turnover=50000.0,
            )
        )
        bar = aggregator.update_from_quote(
            QuoteEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 30, 45, tzinfo=timezone.utc),
                last_price=501.2,
            )
        )
        self.assertEqual(bar.close_price, 501.2)
        self.assertEqual(bar.high_price, 501.2)

    def test_finalize_due_bars_closes_old_minute(self) -> None:
        """Bars should be closed when crossing minute boundary."""
        aggregator = BarAggregator()
        aggregator.update_from_tick(
            TickEvent(
                event_type=None,  # type: ignore[arg-type]
                symbol="HK.00700",
                source="itick",
                event_time=datetime(2026, 6, 7, 9, 30, 10, tzinfo=timezone.utc),
                price=500.0,
                volume=100.0,
                turnover=50000.0,
            )
        )
        finalized = aggregator.finalize_due_bars(
            datetime(2026, 6, 7, 9, 31, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(len(finalized), 1)
        self.assertFalse(finalized[0].provisional)

    def test_aggregate_period_groups_closed_bars(self) -> None:
        """Closed 1m bars should aggregate into 5m bars."""
        aggregator = BarAggregator()
        base_time = datetime(2026, 6, 7, 9, 30, tzinfo=timezone.utc)
        for index in range(5):
            event_time = base_time + timedelta(minutes=index, seconds=10)
            aggregator.update_from_tick(
                TickEvent(
                    event_type=None,  # type: ignore[arg-type]
                    symbol="HK.00700",
                    source="itick",
                    event_time=event_time,
                    price=500.0 + index,
                    volume=100.0,
                    turnover=50000.0,
                )
            )
            aggregator.finalize_due_bars(event_time + timedelta(minutes=1))
        grouped = aggregator.aggregate_period("HK.00700", "5m")
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0].open_price, 500.0)
        self.assertEqual(grouped[0].close_price, 504.0)
        self.assertEqual(grouped[0].volume, 500.0)


if __name__ == "__main__":
    unittest.main()
