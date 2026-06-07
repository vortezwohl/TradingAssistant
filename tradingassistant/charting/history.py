"""实现图表历史回填服务。

该模块负责优先命中 `MemoryCacheStore`，未命中时回源 iTick REST，
并把结果转换为后续 K 线聚合与图表 bootstrap 可以直接使用的稳定结构。
"""

from __future__ import annotations

from dataclasses import dataclass

from tradingassistant.infrastructure.cache import CacheStore
from tradingassistant.market_data.contracts import BarRecord
from tradingassistant.market_data.gateway import ITickMarketGateway

from .keys import bar_history_key


@dataclass(slots=True)
class HistoryBackfillService:
    """封装历史回填逻辑。"""

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
        """获取标准化历史 K 线。

        Args:
            region: 市场区域。
            code: 标的代码。
            period: 图表周期。
            limit: 最大条数。
            end: 截止时间。
            ttl_seconds: 缓存生存时间。

        Returns:
            标准化后的历史 K 线列表。
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
