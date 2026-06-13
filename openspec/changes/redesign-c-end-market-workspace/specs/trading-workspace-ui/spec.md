## MODIFIED Requirements

### Requirement: System SHALL render a chart-first trading workspace on desktop
The system SHALL present the watch page as a fixed-viewport, chart-first trading workspace on desktop, where the primary chart area remains the dominant first-screen element and supporting modules are organized as stable terminal regions instead of a vertically expanding page.

#### Scenario: Desktop first screen prioritizes the chart workspace
- **WHEN** the watch page is opened on a desktop-width viewport
- **THEN** the system SHALL display a compact market header, a central chart console, and adjacent supporting regions for navigation and microstructure data

#### Scenario: Secondary content does not overload the first screen
- **WHEN** the watch page renders controls, summaries, technical studies, or microstructure data
- **THEN** the system SHALL keep that content in fixed side regions, route panes, or deferred panels instead of presenting all sections as equal vertically stacked first-screen panels

### Requirement: System SHALL progressively disclose low-frequency controls and diagnostics
The system SHALL keep low-frequency controls and development diagnostics accessible without making them permanent first-screen distractions in the user-facing workspace.

#### Scenario: Diagnostics are hidden by default
- **WHEN** the page first loads
- **THEN** the system SHALL keep connection details, subscription payloads, and comparable diagnostics outside the default user-facing workspace by default

#### Scenario: Low-frequency controls remain accessible
- **WHEN** the user needs to adjust secondary settings or inspect additional configuration
- **THEN** the system SHALL provide a clear secondary interaction path that preserves access to the main chart workspace instead of forcing the user into a long scrolling page

### Requirement: System SHALL apply a unified dark cool visual system
The system SHALL use a consistent dark terminal visual language across page background, panels, controls, chart container, and status elements, with restrained highlight usage that supports scanability rather than visual softness.

#### Scenario: Shared tokens drive terminal surfaces
- **WHEN** the watch page renders containers, text, borders, separators, ladders, and scrollable market panels
- **THEN** the system SHALL use a shared set of theme tokens for hard dark surfaces, dense separators, typography, and semantic highlight colors

#### Scenario: Accent colors remain semantically constrained
- **WHEN** the page highlights active context, important price-state cues, or critical status information
- **THEN** the system SHALL use accent and status colors selectively instead of applying bright highlight colors uniformly across all components

### Requirement: System SHALL preserve realtime status cues without overwhelming the chart
The system SHALL continue surfacing realtime price-state and indicator-state cues in the UI while keeping the primary chart console readable and analysis-first.

#### Scenario: Workspace exposes live status semantics
- **WHEN** realtime updates change the current bar state or indicator stability
- **THEN** the system SHALL reflect those changes in compact terminal-friendly status text, markers, or badges adjacent to the chart console

#### Scenario: Chart canvas remains visually readable during updates
- **WHEN** the chart is receiving bootstrap data or live incremental updates
- **THEN** the system SHALL keep the chart canvas readable within the terminal theme and SHALL avoid overlaying verbose diagnostic text directly over the primary visualization area

### Requirement: System SHALL remain navigable across responsive breakpoints
The system SHALL adapt the trading workspace layout across desktop, tablet, and mobile viewports by preserving chart readability and using fixed-workspace behavior on desktop while allowing narrower layouts to stack secondary content when necessary.

#### Scenario: Tablet and mobile layouts stack supporting regions below the chart
- **WHEN** the watch page is rendered on tablet or mobile width
- **THEN** the system SHALL stack the supporting regions below the primary chart console or behind an equivalent narrow-screen interaction pattern

#### Scenario: Small screens allow scrolling instead of compression overload
- **WHEN** available viewport height or width cannot comfortably contain the desktop workspace structure
- **THEN** the system SHALL allow segmented scrolling on narrow screens rather than compressing every module into a single overloaded viewport