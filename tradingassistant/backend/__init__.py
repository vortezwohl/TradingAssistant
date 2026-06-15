"""Backend domain modules for the TradingAssistant system.

This package consolidates all server-side domain logic:
- charting: K-line aggregation, history backfill, bar models
- indicators: Technical indicator engine (MA, EMA, RSI, MACD, Bollinger)
- infrastructure: Cache, topic bus, subscription registry abstractions
- market_data: iTick REST/WebSocket access and payload normalization
- transport: FastAPI facade, REST endpoints, WebSocket push channels

Plus standalone modules:
- events: Unified domain event model
- diagnostics: Runtime metrics and observability
- runtime: Default runtime assembly and dependency wiring
- redis_upgrade: Redis migration plan and validation checklist
"""

from . import (
    charting,  # noqa: F401
    indicators,  # noqa: F401
    infrastructure,  # noqa: F401
    market_data,  # noqa: F401
    transport,  # noqa: F401
)
