## ADDED Requirements

### Requirement: System SHALL render a chart-first trading workspace on desktop
The system SHALL present the watch page as a chart-first trading workspace where the primary chart area is the dominant first-screen element, and auxiliary information does not compete equally with the chart for attention.

#### Scenario: Desktop first screen prioritizes the chart workspace
- **WHEN** the watch page is opened on a desktop-width viewport
- **THEN** the system SHALL display a top command bar, a primary chart workspace, and a secondary summary rail as the first-screen structure

#### Scenario: Secondary content does not overload the first screen
- **WHEN** the watch page renders controls, diagnostics, and other low-frequency content
- **THEN** the system SHALL place that content below the primary workspace or behind progressive disclosure instead of presenting all sections as equal first-screen panels

### Requirement: System SHALL progressively disclose low-frequency controls and diagnostics
The system SHALL keep low-frequency controls and development diagnostics accessible without making them permanent first-screen distractions.

#### Scenario: Diagnostics are hidden by default
- **WHEN** the page first loads
- **THEN** the system SHALL keep connection details, subscription payloads, and comparable diagnostics collapsed, deferred, or placed below the primary workspace by default

#### Scenario: Low-frequency controls remain accessible
- **WHEN** the user needs to adjust indicator toggles or inspect diagnostics
- **THEN** the system SHALL provide a clear interaction path to reach those controls without losing access to the main chart workspace

### Requirement: System SHALL apply a unified dark cool visual system
The system SHALL use a consistent dark cool visual language across page background, panels, controls, chart container, and status elements, with restrained accent usage that supports scanability rather than visual noise.

#### Scenario: Shared tokens drive page surfaces
- **WHEN** the watch page renders containers, text, borders, and badges
- **THEN** the system SHALL use a shared set of theme tokens for background, surface, border, typography, accent, and status colors

#### Scenario: Accent colors remain semantically constrained
- **WHEN** the page highlights active context, important price-state cues, or critical status information
- **THEN** the system SHALL use accent and status colors selectively instead of applying bright highlight colors uniformly across all components

### Requirement: System SHALL preserve realtime status cues without overwhelming the chart
The system SHALL continue surfacing forming/closed bar and provisional/finalized indicator status in the UI while keeping the primary chart workspace readable.

#### Scenario: Summary rail exposes live status semantics
- **WHEN** realtime updates change the current bar state or indicator stability
- **THEN** the system SHALL reflect those changes in summary text, badges, or equivalent compact status affordances adjacent to the chart workspace

#### Scenario: Chart canvas remains visually readable during updates
- **WHEN** the chart is receiving bootstrap data or live incremental updates
- **THEN** the system SHALL keep the chart canvas readable within the dark theme and SHALL avoid overlaying verbose diagnostic text directly over the primary visualization area

### Requirement: System SHALL remain navigable across responsive breakpoints
The system SHALL adapt the trading workspace layout across desktop, tablet, and mobile viewports by preserving chart readability and allowing vertical navigation instead of forcing every module into one viewport.

#### Scenario: Tablet and mobile layouts stack secondary content below the chart
- **WHEN** the watch page is rendered on tablet or mobile width
- **THEN** the system SHALL stack the summary rail and low-frequency sections below the primary chart workspace or behind an equivalent narrow-screen interaction pattern

#### Scenario: Small screens allow scrolling instead of compression overload
- **WHEN** available viewport height or width cannot comfortably contain all sections
- **THEN** the system SHALL allow scrolling and content separation rather than compressing all modules into a single overloaded viewport