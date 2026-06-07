"""统一定义图表主链路中的 key 与 topic 构造规则。

这些 key 会同时用于缓存、广播与后续 Redis 平滑升级，因此必须保持稳定。
"""

from __future__ import annotations


def chart_topic(symbol: str, period: str) -> str:
    """生成图表主题标识。"""

    return f"chart:{symbol}:{period}"


def quotes_topic(name: str = "watchlist") -> str:
    """生成列表行情主题标识。"""

    return f"quotes:{name}"


def alerts_topic(name: str = "default") -> str:
    """生成预警主题标识。"""

    return f"alerts:{name}"


def chart_snapshot_key(symbol: str, period: str) -> str:
    """生成图表快照缓存键。"""

    return f"snapshot:{chart_topic(symbol, period)}"


def bar_history_key(symbol: str, period: str, limit: int) -> str:
    """生成历史 K 线缓存键。"""

    return f"history:{symbol}:{period}:{limit}"


def indicator_snapshot_key(symbol: str, period: str) -> str:
    """生成指标快照缓存键。"""

    return f"indicator:{symbol}:{period}"
