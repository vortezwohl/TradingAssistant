"""Chart history backfill service.

This module prioritizes `MemoryCacheStore` hits, falls back to iTick REST
on miss, and converts results into stable structures usable by downstream
K-line aggregation and chart bootstrap.
"""

from __future__ import annotations

from dataclasses import dataclass

from tradingassistant.backend.infrastructure.cache import CacheStore
from tradingassistant.backend.market_data.contracts import BarRecord
from tradingassistant.backend.market_data.gateway import ITickMarketGateway

from .keys import bar_history_key


@dataclass(slots=True)
class HistoryBackfillService:
    """Encapsulate history backfill logic."""

    gateway: ITickMarketGateway
    cache_store: CacheStore

    def get_bars(
        self,
        *,
        region: str,
        code: str,
        period: str,
        limit: int,
        end: str | None = None,
        ttl_seconds: int = 30,
    ) -> list[BarRecord]:
        """Retrieve normalized historical K-lines.

        Args:
            region: Market region.
            code: Instrument code.
            period: Chart period.
            limit: Maximum bar count.
            end: End time.
            ttl_seconds: Cache TTL in seconds.

        Returns:
            List of normalized historical bar records.
        """
        cache_key = bar_history_key(f"{region.upper()}.{code}", period, limit)
        cached = self.cache_store.get(cache_key)
        if cached is not None:
            return cached

        bars = self.gateway.get_stock_history(
            region=region,
            code=code,
            period=period,
            limit=limit,
            end=end,
        )
        self.cache_store.set(cache_key, bars, ttl_seconds=ttl_seconds)
        return bars
