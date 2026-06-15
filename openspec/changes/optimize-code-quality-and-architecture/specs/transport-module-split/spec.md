# transport-module-split Specification

## Purpose
将 `transport/app.py` 中 `create_app` 函数的 WebSocket 路由实现提取为独立模块，降低函数圈复杂度至可维护水平。

## ADDED Requirements

### Requirement: Transport layer SHALL have WebSocket routes in separate modules
The system SHALL extract the three WebSocket route implementations from `create_app` into independent files:
- `transport/ws_chart.py` — chart stream WebSocket endpoint
- `transport/ws_quote.py` — quote stream WebSocket endpoint
- `transport/ws_alert.py` — alert stream WebSocket endpoint
- `transport/ws_helpers.py` — shared subscription lifecycle functions

#### Scenario: create_app cyclomatic complexity is at most 10
- **WHEN** `ruff check --select C901 tradingassistant/transport/app.py` is executed
- **THEN** zero complexity errors SHALL be reported

#### Scenario: create_app contains at most 50 statements
- **WHEN** `ruff check --select PLR0915 tradingassistant/transport/app.py` is executed
- **THEN** zero too-many-statements errors SHALL be reported

#### Scenario: WebSocket route behavior is unchanged after split
- **WHEN** `pytest tests/test_transport.py -v` is executed
- **THEN** all previously passing tests SHALL continue to pass

#### Scenario: Each route module imports only its required dependencies
- **WHEN** `ws_chart.py` is opened
- **THEN** it SHALL import only the symbols it directly uses (not all transport-layer symbols)

### Requirement: Shared WebSocket helper functions SHALL be centralized in ws_helpers.py
The subscription lifecycle functions (`_subscribe_topic`, `_unsubscribe_topic`, `_cleanup_connection`, `_make_sender_callback`, `_subscription_ack`) SHALL be defined in `ws_helpers.py` and imported by each route module.

#### Scenario: Helper functions are importable by all route modules
- **WHEN** `ws_chart.py`, `ws_quote.py`, and `ws_alert.py` are opened
- **THEN** each SHALL import shared helpers from `tradingassistant.transport.ws_helpers`
