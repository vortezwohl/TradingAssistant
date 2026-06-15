"""Unified key and topic construction rules for the chart pipeline.

These keys are used for caching, broadcasting, and future smooth Redis
upgrade, so they must remain stable.
"""

from __future__ import annotations


def chart_topic(symbol: str, period: str) -> str:
    """Generate chart topic identifier."""
    return f"chart:{symbol}:{period}"


def quotes_topic(name: str = "watchlist") -> str:
    """Generate quote list topic identifier."""
    return f"quotes:{name}"


def alerts_topic(name: str = "default") -> str:
    """Generate alert topic identifier."""
    return f"alerts:{name}"


def chart_snapshot_key(symbol: str, period: str) -> str:
    """Generate chart snapshot cache key."""
    return f"snapshot:{chart_topic(symbol, period)}"


def bar_history_key(symbol: str, period: str, limit: int) -> str:
    """Generate historical K-line cache key."""
    return f"history:{symbol}:{period}:{limit}"


def indicator_snapshot_key(symbol: str, period: str) -> str:
    """Generate indicator snapshot cache key."""
    return f"indicator:{symbol}:{period}"
