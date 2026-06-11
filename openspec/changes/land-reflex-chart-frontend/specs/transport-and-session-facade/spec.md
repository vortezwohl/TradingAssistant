## MODIFIED Requirements

### Requirement: System SHALL expose bootstrap and realtime transport channels through FastAPI
The system SHALL provide a FastAPI-facing transport facade that separates bootstrap REST requests from realtime push channels for chart updates, quote updates, and alert events, and the frontend SHALL rely on those separate channels for chart first paint and subsequent incremental updates.

#### Scenario: Bootstrap uses request-response transport
- **WHEN** a client requests an initial chart snapshot
- **THEN** the system SHALL return bootstrap data through a synchronous request-response API

#### Scenario: Realtime chart updates use a push channel
- **WHEN** a client has completed bootstrap for a chart
- **THEN** the system SHALL deliver subsequent chart updates through a realtime push channel

#### Scenario: Frontend receives subscription acknowledgement
- **WHEN** the chart frontend subscribes to a chart topic
- **THEN** the transport layer SHALL return an acknowledgement payload that identifies the accepted subscription topic

### Requirement: System SHALL keep session-level subscriptions separate from page state management
The system SHALL manage session subscriptions inside the transport and market facade layer so that page state and transport lifecycle do not become tightly coupled, and frontend chart context switches SHALL rebuild subscriptions through the transport facade rather than by persisting raw market state in Reflex State.

#### Scenario: Page state does not directly own market subscriptions
- **WHEN** a Reflex page displays a chart
- **THEN** the active market subscription SHALL be registered through the transport facade rather than being persisted as raw realtime state in Reflex State

#### Scenario: Session unsubscribe releases transport resources
- **WHEN** a client disconnects or unsubscribes from a topic
- **THEN** the system SHALL remove the session-to-topic mapping and evaluate whether upstream subscriptions can be released

#### Scenario: Frontend context switch unsubscribes old topic
- **WHEN** the user switches away from the currently active chart topic
- **THEN** the frontend SHALL request unsubscribe for the previous topic before or during subscription setup for the new chart context
