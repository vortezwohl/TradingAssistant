"""Verify indicator engine initialization, incremental updates, and consistency comparison."""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from tradingassistant.backend.charting.models import RuntimeBar
from tradingassistant.backend.indicators.engine import IncrementalIndicatorEngine


def build_bars(count: int = 30) -> list[RuntimeBar]:
    """Build a set of test K-lines."""
    base_time = datetime(2026, 6, 7, 9, 30, tzinfo=timezone.utc)
    bars = []
    for index in range(count):
        close_price = 500.0 + index
        bars.append(
            RuntimeBar(
                symbol="HK.00700",
                period="1m",
                bar_time=base_time + timedelta(minutes=index),
                open_price=close_price - 0.5,
                high_price=close_price + 1.0,
                low_price=close_price - 1.0,
                close_price=close_price,
                volume=1000 + index,
                turnover=500000 + index * 100,
                provisional=False,
            )
        )
    return bars


class IncrementalIndicatorEngineTests(unittest.TestCase):
    """Test incremental indicator engine."""

    def test_initialize_returns_basic_snapshot(self) -> None:
        """Should return basic indicator snapshot after initialization."""
        engine = IncrementalIndicatorEngine()
        snapshot = engine.initialize("HK.00700:1m", build_bars())
        self.assertIn("ma5", snapshot.values)
        self.assertIn("ema12", snapshot.values)
        self.assertFalse(snapshot.provisional)

    def test_update_marks_provisional_flag(self) -> None:
        """Incremental update should preserve the provisional flag."""
        engine = IncrementalIndicatorEngine()
        bars = build_bars()
        engine.initialize("HK.00700:1m", bars)
        new_bar = RuntimeBar(
            symbol="HK.00700",
            period="1m",
            bar_time=bars[-1].bar_time + timedelta(minutes=1),
            open_price=531.0,
            high_price=532.0,
            low_price=530.5,
            close_price=531.5,
            volume=1031,
            turnover=503100,
            provisional=True,
        )
        snapshot = engine.update("HK.00700:1m", new_bar, provisional=True)
        self.assertTrue(snapshot.provisional)
        self.assertIn("boll_upper", snapshot.values)

    def test_compare_with_reference_returns_small_deltas(self) -> None:
        """Deltas with OpenTrade reference results should be computable."""
        engine = IncrementalIndicatorEngine()
        bars = build_bars()
        snapshot = engine.initialize("HK.00700:1m", bars)
        delta = engine.compare_with_reference(bars, snapshot)
        self.assertIn("ma5", delta)
        self.assertGreaterEqual(delta["ma5"], 0.0)


if __name__ == "__main__":
    unittest.main()
