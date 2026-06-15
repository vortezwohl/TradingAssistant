## 1. Create backend package directory

- [x] 1.1 Create `tradingassistant/backend/` directory via fileglide
- [x] 1.2 Write `tradingassistant/backend/__init__.py` with English package docstring listing all sub-packages

## 2. Move source modules under backend/

- [x] 2.1 Move `tradingassistant/charting/` to `tradingassistant/backend/charting/`
- [x] 2.2 Move `tradingassistant/indicators/` to `tradingassistant/backend/indicators/`
- [x] 2.3 Move `tradingassistant/infrastructure/` to `tradingassistant/backend/infrastructure/`
- [x] 2.4 Move `tradingassistant/market_data/` to `tradingassistant/backend/market_data/`
- [x] 2.5 Move `tradingassistant/transport/` to `tradingassistant/backend/transport/`
- [x] 2.6 Move `tradingassistant/events.py` to `tradingassistant/backend/events.py`
- [x] 2.7 Move `tradingassistant/diagnostics.py` to `tradingassistant/backend/diagnostics.py`
- [x] 2.8 Move `tradingassistant/runtime.py` to `tradingassistant/backend/runtime.py`
- [x] 2.9 Move `tradingassistant/redis_upgrade.py` to `tradingassistant/backend/redis_upgrade.py`

## 3. Update absolute imports in all affected files

- [x] 3.1 Update imports in `main.py` (`tradingassistant.runtime` to `tradingassistant.backend.runtime`)
- [x] 3.2 Update imports in `tradingassistant/backend/runtime.py` (all domain imports)
- [x] 3.3 Update imports in `tradingassistant/backend/transport/app.py`
- [x] 3.4 Update imports in `tradingassistant/backend/transport/ws_alert.py`
- [x] 3.5 Update imports in `tradingassistant/backend/transport/ws_chart.py`
- [x] 3.6 Update imports in `tradingassistant/backend/transport/ws_helpers.py`
- [x] 3.7 Update imports in `tradingassistant/backend/transport/ws_quote.py`
- [x] 3.8 Update imports in `tradingassistant/backend/charting/aggregator.py`
- [x] 3.9 Update imports in `tradingassistant/backend/charting/history.py`
- [x] 3.10 Update imports in `tradingassistant/backend/indicators/engine.py`
- [x] 3.11 Update imports in `tradingassistant/backend/market_data/gateway.py`
- [x] 3.12 Update imports in `tradingassistant/backend/market_data/normalizer.py`
- [x] 3.13 Update imports in `tests/test_charting.py`
- [x] 3.14 Update imports in `tests/test_events.py`
- [x] 3.15 Update imports in `tests/test_indicators.py`
- [x] 3.16 Update imports in `tests/test_infrastructure.py`
- [x] 3.17 Update imports in `tests/test_market_data.py`
- [x] 3.18 Update imports in `tests/test_runtime_and_upgrade.py`
- [x] 3.19 Update imports in `tests/test_transport.py`

## 4. Update package root __init__.py

- [x] 4.1 Update `tradingassistant/__init__.py` to reflect new backend package structure

## 5. Verification

- [x] 5.1 Run `ruff check` on entire project (must pass with zero errors)
- [x] 5.2 Run `ruff format` on entire project (all files formatted)
- [x] 5.3 Run `python -m pytest tests/` or `python -m unittest discover tests/` (all tests pass)
- [x] 5.4 Verify `python -c "from tradingassistant.backend.events import TickEvent"` succeeds
- [x] 5.5 Verify `python -c "from tradingassistant.settings import ITICK_TOKEN"` still works
- [x] 5.6 Verify no stale `tradingassistant/__pycache__/` remains in old locations
- [x] 5.7 Git commit with structured commit message
