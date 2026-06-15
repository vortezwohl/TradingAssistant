## MODIFIED Requirements

### Requirement: System SHALL expose the chart console as a coordinated control surface
The system SHALL treat the center workspace as a coordinated chart console with instrument summary, time-scale controls, overlay controls, route controls, chart stage, linked lower studies, and an integrated inspection surface for cursor-driven chart reading.

#### Scenario: Instrument strip and control rows stay attached to the chart console
- **WHEN** the chart console renders the active instrument context
- **THEN** the system SHALL show the instrument summary, compact metrics, time-scale controls, overlay controls, and route controls as a connected control surface above the chart stage

#### Scenario: Lower study strip stays linked to the active chart state
- **WHEN** the user changes active symbol, scale, or route
- **THEN** the system SHALL keep the lower study strip synchronized with the active chart state without requiring a separate page or modal context

#### Scenario: Chart inspection can follow the hovered chart unit
- **WHEN** the user hovers across the chart stage inside the terminal workspace
- **THEN** the system SHALL expose hover-following inspection detail for the active chart unit and its linked lower-study values without breaking the fixed workspace posture

### Requirement: System SHALL provide a cohesive terminal visual system across all workspace modules
The system SHALL use a consistent hard-edge terminal visual language across the top bar, control rows, chart region, watchlist rail, microstructure rail, and analysis surfaces, including dense side rails that preserve readable alignment under narrow-width constraints.

#### Scenario: Shared visual tokens drive all terminal modules
- **WHEN** the watch page renders surfaces, borders, controls, typography, scroll containers, and emphasis states
- **THEN** the system SHALL use shared theme tokens for flat dark surfaces, dense separators, compact spacing, and semantic highlight colors

#### Scenario: Numeric and market data styling remains scan-friendly
- **WHEN** the workspace renders prices, sizes, spreads, volume, or compact chart metrics
- **THEN** the system SHALL present numeric data using terminal-appropriate typography and contrast that supports quick scanability in dense layouts

#### Scenario: Dense left-rail text remains readable under terminal width constraints
- **WHEN** the left rail renders watchlist rows, movers rows, and snapshot cells in a dense desktop layout
- **THEN** the system SHALL preserve readable text alignment and predictable truncation instead of allowing clipped or visibly shifted labels within the rail
