## ADDED Requirements

### Requirement: System SHALL present the desktop watch page as a fixed-viewport terminal workspace
The system SHALL render the desktop watch page as a fixed-viewport terminal workspace that fills the browser height, keeps whole-page scrolling disabled on desktop, and organizes the first screen into stable terminal regions instead of vertically stacked cards.

#### Scenario: Desktop layout follows the terminal region contract
- **WHEN** the watch page is opened on a desktop-width viewport
- **THEN** the system SHALL present a top terminal bar, a left navigation rail, a center chart console, a right microstructure rail, and a lower study strip within the same fixed workspace

#### Scenario: Dense modules scroll locally without moving the workspace shell
- **WHEN** watchlist rows, mover rows, depth rows, order book rows, or rail items exceed the available height
- **THEN** the system SHALL keep the workspace shell fixed and SHALL allow scrolling only inside the affected dense module containers

### Requirement: System SHALL use market-facing English terminology throughout the terminal workspace
The system SHALL use English trading and market terminology that is understandable to financial practitioners, and SHALL avoid default user-facing labels that read like engineering diagnostics or computer infrastructure.

#### Scenario: Controls and modules use market-facing naming
- **WHEN** the page renders labels for panels, controls, tabs, routes, and compact metrics
- **THEN** the system SHALL use market-facing names such as watchlist, market movers, market depth, order book, tape, analysis, route, overlay, session, and turnover

#### Scenario: Engineering detail remains outside the default trading surface
- **WHEN** connection state, payload data, bootstrap state, or similar diagnostics exist in the product
- **THEN** the system SHALL keep them out of the default terminal workspace and SHALL not let them replace the user-facing module titles or helper copy

### Requirement: System SHALL provide a compact terminal bar instead of a hero banner
The system SHALL provide a compact market terminal bar that communicates product identity, live state, macro context, and the selected instrument summary without diluting the chart-first posture.

#### Scenario: Terminal bar shows market identity and macro context
- **WHEN** the desktop workspace loads
- **THEN** the system SHALL show a compact top bar with product lockup, live-state marker, macro strip, and selected instrument summary metrics

#### Scenario: Terminal bar remains subordinate to the chart console
- **WHEN** the user scans the first screen
- **THEN** the system SHALL keep the terminal bar visually compact so the chart console remains the dominant analytical surface

### Requirement: System SHALL support direct code-driven symbol selection in the terminal reference
The system SHALL support direct symbol selection by code in the terminal reference instead of requiring a search-first flow.

#### Scenario: User adds a symbol by code only
- **WHEN** the user enters a symbol code such as `US.NVDA` or `HK.00700`
- **THEN** the system SHALL allow the symbol to be added to the watchlist without requiring a separate search result flow

#### Scenario: Active symbol switch updates workspace context
- **WHEN** the user selects another watchlist symbol
- **THEN** the system SHALL update the active instrument identity, chart console context, and dependent terminal modules to match the newly selected code

### Requirement: System SHALL keep the static design reference fully English
The system SHALL keep the static design reference fully English for panel names, controls, helper copy, and route labels.

#### Scenario: Static reference avoids mixed-language terminal copy
- **WHEN** the terminal reference is reviewed or implemented
- **THEN** the system SHALL use English labels throughout the design artifact and SHALL not mix in Chinese user-facing terminal text
