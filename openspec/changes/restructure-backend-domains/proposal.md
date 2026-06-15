## Why

The current project structure scatters backend domain modules (charting, indicators, infrastructure, market_data, transport) across the top-level `tradingassistant/` namespace alongside `frontend/` and standalone modules. This flat layout obscures the clear frontend/backend boundary, making it harder for new contributors to navigate and for CI/CD to isolate backend-specific checks.

## What Changes

- **BREAKING**: Move `charting/`, `indicators/`, `infrastructure/`, `market_data/`, `transport/` directories under new `tradingassistant/backend/`
- **BREAKING**: Move `events.py`, `diagnostics.py`, `runtime.py`, `redis_upgrade.py` under `tradingassistant/backend/`
- **BREAKING**: Update all absolute imports from `tradingassistant.<domain>` to `tradingassistant.backend.<domain>` (70 import lines across 19 files)
- Create `tradingassistant/backend/__init__.py` with package documentation
- Keep `tradingassistant/frontend/` and `tradingassistant/settings.py` at their current locations

## Capabilities

### New Capabilities
- `backend-package-structure`: Consolidate all backend domain modules under a single `backend/` package for clear separation of concerns

### Modified Capabilities
<!-- No existing spec requirements change - this is purely a directory reorganization -->

## Impact

- Affected files: 19 files with 70 import lines to update (9 backend source files + 8 test files + main.py + rxconfig.py)
- `tradingassistant/__init__.py` needs update to reflect new package structure
- All existing OpenSpec specs remain valid - no behavioral changes
- Import paths change but runtime behavior is identical
