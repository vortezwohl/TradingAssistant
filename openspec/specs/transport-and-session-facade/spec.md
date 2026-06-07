# transport-and-session-facade Specification

## Purpose
TBD - created by archiving change build-memory-first-market-monitor. Update Purpose after archive.
## Requirements
### Requirement: System SHALL expose bootstrap and realtime transport channels through FastAPI
The system SHALL provide a FastAPI-facing transport facade that separates bootstrap REST requests from realtime push channels for chart updates, quote updates, and alert events.

#### Scenario: Bootstrap uses request-response transport
- **WHEN** a client requests an initial chart snapshot
- **THEN** the system SHALL return bootstrap data through a synchronous request-response API

#### Scenario: Realtime chart updates use a push channel
- **WHEN** a client has completed bootstrap for a chart
- **THEN** the system SHALL deliver subsequent chart updates through a realtime push channel

### Requirement: System SHALL keep session-level subscriptions separate from page state management
The system SHALL manage session subscriptions inside the transport and market facade layer so that page state and transport lifecycle do not become tightly coupled.

#### Scenario: Page state does not directly own market subscriptions
- **WHEN** a Reflex page displays a chart
- **THEN** the active market subscription SHALL be registered through the transport facade rather than being persisted as raw realtime state in Reflex State

#### Scenario: Session unsubscribe releases transport resources
- **WHEN** a client disconnects or unsubscribes from a topic
- **THEN** the system SHALL remove the session-to-topic mapping and evaluate whether upstream subscriptions can be released

