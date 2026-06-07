# market-data-ingestion Specification

## Purpose
TBD - created by archiving change build-memory-first-market-monitor. Update Purpose after archive.
## Requirements
### Requirement: System SHALL normalize iTick market events into internal domain events
The system SHALL consume iTick REST and WebSocket responses through an adapter layer and convert them into stable internal domain events so that downstream modules do not depend on upstream raw payload structure.

#### Scenario: WebSocket quote event is normalized
- **WHEN** the market gateway receives a quote payload from iTick WebSocket
- **THEN** the adapter SHALL emit a `QuoteEvent` with normalized symbol, timestamp, price, volume, turnover, and source metadata fields

#### Scenario: REST history response is normalized
- **WHEN** the history service fetches K-line data from iTick REST
- **THEN** the adapter SHALL convert the response into normalized bar records with consistent open, high, low, close, volume, turnover, and period fields

### Requirement: System SHALL isolate upstream connection management from downstream business modules
The system SHALL encapsulate heartbeat, reconnect, connection lifecycle events, and protocol-specific error handling inside the market gateway so that downstream modules consume only domain events and connection state signals.

#### Scenario: Upstream reconnect does not leak raw client errors
- **WHEN** the iTick WebSocket connection disconnects and reconnect logic is triggered
- **THEN** downstream modules SHALL receive structured connection state events instead of direct SDK exceptions

#### Scenario: Market processors subscribe to internal events only
- **WHEN** a downstream module needs realtime market data
- **THEN** it SHALL subscribe to normalized internal event channels rather than calling the iTick SDK directly

