# code-quality-enforcement Specification

## Purpose
建立项目级的持续代码质量门禁，固化 ruff 配置，消除已知的 lint 违规项，为后续所有 agent 变更提供一致的代码卫生基线。

## ADDED Requirements

### Requirement: Project SHALL include a ruff lint configuration in pyproject.toml
The project SHALL define a `[tool.ruff.lint]` section in `pyproject.toml` that specifies the set of enabled rules and ignores rules incompatible with Chinese-language docstrings.

#### Scenario: Ruff configuration is present and valid
- **WHEN** `pyproject.toml` is read by `ruff`
- **THEN** the configuration SHALL enable rules E, W, F, I, N, B, SIM, C, PL
- **AND** the configuration SHALL ignore D400, D415, and RUF002 (not applicable to Chinese docstring conventions)

#### Scenario: Ruff check passes on all source files
- **WHEN** `ruff check .` is executed
- **THEN** zero errors SHALL be reported for the enabled rule set

### Requirement: Project SHALL have zero unused imports in all source modules
Every `import` statement SHALL reference a symbol that is used in the module, either at runtime or in a `TYPE_CHECKING` block.

#### Scenario: aggregator.py has no unused imports
- **WHEN** `ruff check --select F401 tradingassistant/charting/aggregator.py` is executed
- **THEN** zero unused import errors SHALL be reported

### Requirement: All zip() calls in frontend/charting.py SHALL use strict=True
Every `zip()` call in `tradingassistant/frontend/charting.py` SHALL include the `strict=True` parameter to enforce equal-length iteration.

#### Scenario: zip strict mode is enforced
- **WHEN** `ruff check --select B905 tradingassistant/frontend/charting.py` is executed
- **THEN** zero `zip()` without `strict=` errors SHALL be reported

#### Scenario: Unequal-length data raises ValueError loudly
- **WHEN** two input lists of unequal length are passed to `zip(a, b, strict=True)`
- **THEN** a `ValueError` SHALL be raised immediately rather than silently truncating data

### Requirement: All source files SHALL have imports in sorted order
Import blocks SHALL follow the standard library → third-party → first-party ordering convention, with each group sorted alphabetically.

#### Scenario: Import sorting passes for all files
- **WHEN** `ruff check --select I .` is executed
- **THEN** zero import sorting errors SHALL be reported

### Requirement: Top-level function definitions SHALL be separated by exactly two blank lines
All top-level function and class definitions in `tradingassistant/frontend/app.py` SHALL be preceded by exactly two blank lines, per PEP 8 E302.

#### Scenario: No extraneous blank lines before top-level functions
- **WHEN** `ruff check --select E302 tradingassistant/frontend/app.py` is executed
- **THEN** zero blank line errors SHALL be reported
