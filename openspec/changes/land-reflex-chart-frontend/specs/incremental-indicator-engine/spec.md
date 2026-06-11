## MODIFIED Requirements

### Requirement: System SHALL distinguish provisional and finalized indicator outputs
The system SHALL mark indicator outputs derived from a forming bar as provisional and SHALL mark outputs derived from a closed bar as finalized, and the frontend SHALL render those two states differently enough that users can tell whether indicator values are still forming.

#### Scenario: Forming bar indicator output is provisional
- **WHEN** indicator values are calculated from an unclosed 1-minute bar
- **THEN** the outbound payload SHALL identify those values as provisional

#### Scenario: Closed bar indicator output is finalized
- **WHEN** indicator values are recalculated after a bar is closed
- **THEN** the outbound payload SHALL identify those values as finalized and eligible for downstream alerts

#### Scenario: Frontend reflects provisional indicator state
- **WHEN** the chart frontend receives provisional indicator values
- **THEN** the visible indicator overlays or panels SHALL present them as in-progress values rather than as fully confirmed outputs
