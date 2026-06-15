## ADDED Requirements

### Requirement: Backend domains reside under backend/ package

All backend domain modules SHALL reside under `tradingassistant.backend/` instead of directly under `tradingassistant/`. The following modules SHALL be relocated:

- `tradingassistant.charting` to `tradingassistant.backend.charting`
- `tradingassistant.indicators` to `tradingassistant.backend.indicators`
- `tradingassistant.infrastructure` to `tradingassistant.backend.infrastructure`
- `tradingassistant.market_data` to `tradingassistant.backend.market_data`
- `tradingassistant.transport` to `tradingassistant.backend.transport`
- `tradingassistant.events` to `tradingassistant.backend.events`
- `tradingassistant.diagnostics` to `tradingassistant.backend.diagnostics`
- `tradingassistant.runtime` to `tradingassistant.backend.runtime`
- `tradingassistant.redis_upgrade` to `tradingassistant.backend.redis_upgrade`

#### Scenario: Import from backend sub-package

- **WHEN** any module imports from tradingassistant.backend.charting.models
- **THEN** the import SHALL resolve to the same RuntimeBar class as before

#### Scenario: Settings module remains at root

- **WHEN** any module imports from tradingassistant.settings
- **THEN** the import SHALL resolve from tradingassistant/settings.py without changes

### Requirement: All absolute imports reference backend-prefixed paths

Every absolute import that previously referenced a relocated domain SHALL be updated to the new backend-prefixed path.

#### Scenario: Runtime assembly imports are correct

- **WHEN** tradingassistant/backend/runtime.py imports domain modules
- **THEN** it SHALL use the tradingassistant.backend.* prefix

#### Scenario: Test files import backend paths

- **WHEN** tests/test_charting.py imports BarAggregator
- **THEN** it SHALL use the tradingassistant.backend.charting.aggregator path

### Requirement: Frontend package remains at root

The tradingassistant/frontend/ directory SHALL remain at tradingassistant.frontend.

#### Scenario: Frontend imports are unchanged

- **WHEN** rxconfig.py references the frontend app module
- **THEN** the reference SHALL remain valid without modification

### Requirement: Backend __init__.py documents the package boundary

The new tradingassistant/backend/__init__.py SHALL contain module-level documentation.

#### Scenario: Package documentation is present

- **WHEN** a developer opens tradingassistant/backend/__init__.py
- **THEN** they SHALL see English documentation describing the backend package
