## MODIFIED Requirements

### Requirement: System SHALL render a chart-first trading workspace on desktop
The system SHALL present the watch page as a fixed-viewport, chart-first trading workspace on desktop, where the center chart console remains the dominant first-screen surface and supporting modules are arranged as stable terminal regions instead of vertically stacked cards.

#### Scenario: Desktop first screen follows the terminal module hierarchy
- **WHEN** the watch page is opened on a desktop-width viewport
- **THEN** the system SHALL show a compact top bar, a left navigation rail, a center chart console, a right microstructure rail, and a lower study strip inside one stable desktop workspace

#### Scenario: Dense supporting content stays in terminal side regions
- **WHEN** watchlist rows, movers, studies, or microstructure content become dense
- **THEN** the system SHALL keep them inside side regions, lower study strips, or local scroll panels rather than converting the first screen into a long vertically stacked dashboard

### Requirement: System SHALL provide a cohesive terminal visual system across all workspace modules
The system SHALL use a consistent hard-edge terminal visual language across the top bar, control rows, chart region, watchlist rail, microstructure rail, and analysis surfaces.

#### Scenario: Shared visual tokens drive all terminal modules
- **WHEN** the watch page renders surfaces, borders, controls, typography, scroll containers, and emphasis states
- **THEN** the system SHALL use shared theme tokens for flat dark surfaces, dense separators, compact spacing, and semantic highlight colors

#### Scenario: Numeric and market data styling remains scan-friendly
- **WHEN** the workspace renders prices, sizes, spreads, volume, or compact chart metrics
- **THEN** the system SHALL present numeric data using terminal-appropriate typography and contrast that supports quick scanability in dense layouts

### Requirement: System SHALL expose the chart console as a coordinated control surface
The system SHALL treat the center workspace as a coordinated chart console with instrument summary, time-scale controls, overlay controls, route controls, chart stage, and linked lower studies.

#### Scenario: Instrument strip and control rows stay attached to the chart console
- **WHEN** the chart console renders the active instrument context
- **THEN** the system SHALL show the instrument summary, compact metrics, time-scale controls, overlay controls, and route controls as a connected control surface above the chart stage

#### Scenario: Lower study strip stays linked to the active chart state
- **WHEN** the user changes active symbol, scale, or route
- **THEN** the system SHALL keep the lower study strip synchronized with the active chart state without requiring a separate page or modal context

### Requirement: System SHALL preserve realtime status cues without overwhelming the chart
The system SHALL continue surfacing realtime price-state and indicator-state cues while keeping the main chart readable and analysis-first.

#### Scenario: Compact live-state cues remain visible near the chart console
- **WHEN** realtime updates change the active bar state, price bias, or route context
- **THEN** the system SHALL surface those changes through compact status text, legend values, or small badges adjacent to the chart console

#### Scenario: Realtime cues do not replace primary chart readability
- **WHEN** the chart receives bootstrap data or live incremental changes
- **THEN** the system SHALL preserve chart readability and SHALL avoid placing verbose diagnostics over the main visualization area

### Requirement: System SHALL expose right-rail information views without turning them into a chat workflow
The system SHALL allow the right-side rail to host multiple information views, including scheduled AI analysis, without turning the workspace into a messaging interface.

#### Scenario: Scheduled AI analysis appears as a non-chat terminal surface
- **WHEN** the user opens the `Analysis` rail tab
- **THEN** the system SHALL present scheduled AI push content as structured cards, summaries, or compact status blocks instead of a free-form chat input and transcript UI

#### Scenario: Right-rail information switching preserves the chart-first posture
- **WHEN** the user switches among analysis, tape, signals, or news in the rail
- **THEN** the system SHALL update the right-side content area only and SHALL preserve the rest of the trading workspace state

### Requirement: System SHALL remain navigable across responsive breakpoints
The system SHALL preserve the fixed desktop terminal posture on desktop while allowing narrower breakpoints to reorganize supporting modules when necessary.

#### Scenario: Desktop preserves the non-scrolling terminal shell
- **WHEN** the workspace is rendered on desktop width
- **THEN** the system SHALL keep the terminal shell fixed to the viewport and SHALL rely on local scroll containers inside dense modules

#### Scenario: Narrow layouts may stack secondary regions when needed
- **WHEN** the workspace is rendered on tablet or mobile width
- **THEN** the system MAY stack or defer supporting regions below the chart, but it SHALL preserve readable chart and control access rather than compressing every module into one overloaded viewport
