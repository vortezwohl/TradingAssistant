"""Core package entry for the TradingAssistant project.

This package hosts the backend for the enhanced market monitoring system:
1. Market data ingestion via iTick;
2. In-memory runtime cache, subscription registry, and topic broadcast;
3. Stable domain models and base abstractions for chart aggregation,
   indicator computation, and FastAPI/Reflex integration.

The current phase prioritizes foundational infrastructure with unified interfaces,
reserving replacement points for a smooth MEMORY-to-Redis upgrade path.
"""

__all__ = [
    "events",
]
