## ADDED Requirements

### Requirement: System SHALL initialize indicator state from historical windows
The system SHALL initialize indicator state using historical market data before realtime incremental updates start so that first render and subsequent updates share a consistent baseline.

#### Scenario: Historical initialization computes indicator baseline
- **WHEN** chart bootstrap is requested with one or more enabled indicators
- **THEN** the system SHALL compute the indicator baseline from the requested history window before subscribing to realtime updates

#### Scenario: OpenTrade can be used for initialization
- **WHEN** indicator initialization requires batch historical calculations
- **THEN** the system MAY use OpenTrade-based historical enrichment as the initializer source

### Requirement: System SHALL update realtime indicators incrementally
The system SHALL update indicator state incrementally as new ticks or bars arrive, instead of recomputing the full historical dataframe for each update.

#### Scenario: O(1) indicators update from latest state
- **WHEN** a new bar or tick affects an indicator with recursive state
- **THEN** the indicator engine SHALL update the result from the latest stored state and the new input event

#### Scenario: Window indicators use bounded rolling state
- **WHEN** a window-based indicator requires recent N samples
- **THEN** the indicator engine SHALL maintain bounded rolling state sufficient to update that indicator without replaying the full history

### Requirement: System SHALL distinguish provisional and finalized indicator outputs
The system SHALL mark indicator outputs derived from a forming bar as provisional and SHALL mark outputs derived from a closed bar as finalized.

#### Scenario: Forming bar indicator output is provisional
- **WHEN** indicator values are calculated from an unclosed 1-minute bar
- **THEN** the outbound payload SHALL identify those values as provisional

#### Scenario: Closed bar indicator output is finalized
- **WHEN** indicator values are recalculated after a bar is closed
- **THEN** the outbound payload SHALL identify those values as finalized and eligible for downstream alerts
