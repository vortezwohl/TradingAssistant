# frontend-module-architecture Specification

## Purpose
将前端巨型模块拆分为职责聚焦的子模块，建立可维护的文件级架构，并统一前端文档语言与项目规范。

## ADDED Requirements

### Requirement: Frontend charting logic SHALL be split into four focused sub-modules
The system SHALL separate `tradingassistant/frontend/charting.py` (1200 lines) into four files:
- `models.py` — market data generation functions (`build_market_model`, `build_watchlist_rows`, `build_movers_rows`, etc.)
- `studies.py` — technical indicator computation functions (`_moving_average`, `_ema`, `_rsi`, `_atr`, `_obv`, `_build_route_study_models`, etc.)
- `renders.py` — SVG and display rendering functions (`build_primary_chart_svg`, `build_chart_legend`, `build_depth_rows`, etc.)
- `utils.py` — utility and helper functions (`format_number`, `format_signed`, `normalize_code`, `build_tape_rows`, etc.)

#### Scenario: Each sub-module is under 400 lines
- **WHEN** the split is complete
- **THEN** each new file SHALL contain no more than 400 lines of code

#### Scenario: Original charting.py remains as compatibility re-export layer
- **WHEN** `app.py` or `state.py` imports from `charting`
- **THEN** all previously available symbols SHALL still be accessible without import path changes

#### Scenario: No circular imports exist between sub-modules
- **WHEN** `python -c "import tradingassistant.frontend"` is executed
- **THEN** the import SHALL succeed without circular dependency errors

### Requirement: Frontend module docstrings and comments SHALL use Simplified Chinese
All docstrings, file-level descriptions, and inline comments in `tradingassistant/frontend/` SHALL be written in Simplified Chinese, consistent with the project AGENTS.md rule 0.1 and the remaining 30 Python source files.

#### Scenario: app.py uses Chinese for its module docstring
- **WHEN** `tradingassistant/frontend/app.py` is opened
- **THEN** the file-level docstring SHALL be in Simplified Chinese

#### Scenario: charting sub-modules use Chinese for their docstrings
- **WHEN** `tradingassistant/frontend/models.py`, `studies.py`, `renders.py`, and `utils.py` are opened
- **THEN** each file-level docstring and function docstring SHALL be in Simplified Chinese

#### Scenario: state.py uses Chinese for its docstring
- **WHEN** `tradingassistant/frontend/state.py` is opened
- **THEN** the file-level docstring and `_reset_hover` docstring SHALL be in Simplified Chinese

#### Scenario: theme.py uses Chinese for its docstring and style function descriptions
- **WHEN** `tradingassistant/frontend/theme.py` is opened
- **THEN** the file-level docstring and function Return descriptions SHALL be in Simplified Chinese
