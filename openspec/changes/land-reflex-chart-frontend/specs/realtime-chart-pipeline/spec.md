## MODIFIED Requirements

### Requirement: System SHALL support chart bootstrap with history backfill
The system SHALL provide a bootstrap flow that returns the initial chart dataset before realtime updates begin, including historical bars and the initial indicator snapshot needed for first render, and the frontend SHALL consume that payload as the authoritative first paint for the visible chart.

#### Scenario: Chart bootstrap returns historical bars
- **WHEN** a client requests chart bootstrap for a symbol and period
- **THEN** the system SHALL return normalized historical bars for the requested window

#### Scenario: Chart bootstrap includes initial indicator state
- **WHEN** bootstrap data is returned to the client
- **THEN** the response SHALL include the initial indicator values required for the active indicator set

#### Scenario: Frontend first paint uses bootstrap payload
- **WHEN** the Reflex chart page receives bootstrap data
- **THEN** the visible chart SHALL be initialized from that payload before any realtime message is applied

### Requirement: System SHALL maintain forming 1m bars and closed 1m bars separately
The system SHALL distinguish between the currently forming 1-minute bar and previously closed bars so that realtime chart rendering and indicator stability are both preserved, and the frontend SHALL preserve that distinction when rendering the active chart.

#### Scenario: Forming bar is updated before close
- **WHEN** a new tick or quote arrives within the current 1-minute interval
- **THEN** the system SHALL update the forming 1-minute bar without prematurely marking it as closed

#### Scenario: Closed bar is finalized on interval boundary
- **WHEN** the current 1-minute interval completes
- **THEN** the system SHALL finalize the bar, persist the closed snapshot, and begin a new forming bar

#### Scenario: Frontend differentiates provisional chart bars
- **WHEN** the chart frontend receives an update marked as provisional
- **THEN** the visible chart SHALL treat it as the active forming bar rather than as an immutable historical bar

### Requirement: System SHALL derive higher timeframes from the 1m bar pipeline
The system SHALL compute 5m, 15m, 30m, 60m, and higher chart periods by aggregating finalized 1-minute bars rather than relying on independent upstream subscriptions by default, and the frontend SHALL rebuild its chart context when the user changes timeframe.

#### Scenario: Higher timeframe bars are aggregated from closed 1m bars
- **WHEN** enough 1-minute bars have been finalized to complete a higher timeframe window
- **THEN** the system SHALL generate the corresponding aggregated bar from those closed 1-minute bars

#### Scenario: Higher timeframe aggregation does not require a separate upstream topic
- **WHEN** a client subscribes to a higher timeframe chart
- **THEN** the default implementation SHALL source its bar stream from local aggregation of 1-minute bars

#### Scenario: Frontend timeframe switch triggers context rebuild
- **WHEN** the user switches from one timeframe to another
- **THEN** the frontend SHALL request a fresh bootstrap for the new timeframe and subscribe to the matching chart topic
