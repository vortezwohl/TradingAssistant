## ADDED Requirements

### Requirement: System SHALL provide a dedicated market depth module with multiple presentation modes
The system SHALL provide a dedicated market depth module in the right-side microstructure rail and SHALL support multiple presentation modes for the same active instrument.

#### Scenario: Market depth defaults to a ladder-style bid / ask view
- **WHEN** the user opens the terminal workspace for an active instrument
- **THEN** the system SHALL show a multi-level market depth ladder with bid-side and ask-side size information around the active price region

#### Scenario: User can switch depth modes without leaving the workspace
- **WHEN** the user switches among depth modes such as ladder, profile, and imbalance
- **THEN** the system SHALL update the market depth presentation in place without replacing the rest of the workspace or forcing full-page navigation

### Requirement: System SHALL make depth size visually scannable as well as numerically readable
The system SHALL encode depth size using both numbers and visual ladder or trapezoid treatments so users can scan order concentration quickly.

#### Scenario: Bid and ask ladders expose size visually
- **WHEN** the depth module renders multi-level liquidity
- **THEN** the system SHALL show bid-side and ask-side size emphasis using directional visual bars or equivalent geometric treatments in addition to numeric size values

#### Scenario: Visual depth emphasis remains subordinate to price readability
- **WHEN** depth sizes vary significantly across levels
- **THEN** the system SHALL preserve readable price labels and SHALL not let the size visualization obscure the active price ladder

### Requirement: System SHALL provide a dedicated order book module beside market depth
The system SHALL provide a dedicated order book module within the microstructure rail so users can inspect bid / ask levels, sizes, and spread independently from the market depth view.

#### Scenario: Order book shows bid and ask levels together
- **WHEN** the user inspects the order book for the active instrument
- **THEN** the system SHALL show bid-side and ask-side prices and sizes together with a compact spread readout in the same module

#### Scenario: Order book remains visible inside the fixed desktop workspace
- **WHEN** the order book rows exceed the visible panel height
- **THEN** the system SHALL keep the order book inside a local scrolling region without breaking the desktop fixed-workspace contract

### Requirement: System SHALL provide a right-rail information surface for trade flow and scheduled analysis
The system SHALL provide a right-rail tab surface for `Analysis`, `Tape`, `Signals`, and `News` so the user can switch among microstructure-adjacent information views without losing chart context.

#### Scenario: Right rail exposes recent prints through the tape tab
- **WHEN** the user switches to the tape tab
- **THEN** the system SHALL show recent trade prints or time-and-sales-style rows for the active instrument

#### Scenario: Right rail exposes scheduled AI commentary through the analysis tab
- **WHEN** the user switches to the analysis tab
- **THEN** the system SHALL show non-chat scheduled analysis cards with compact market conclusions, cadence metadata, confidence cues, and risk notes for the active instrument

#### Scenario: Right-rail tabs update in place
- **WHEN** the user switches between analysis, tape, signals, and news
- **THEN** the system SHALL update only the rail content area and SHALL preserve the rest of the terminal workspace state

### Requirement: Microstructure modules SHALL respect the fixed desktop posture
The system SHALL keep depth, order book, and right-rail information views inside the right microstructure rail without forcing the center chart console into a vertically expanding layout.

#### Scenario: Dense right-rail modules preserve the chart-first posture
- **WHEN** the right-side microstructure modules render many rows or analysis cards
- **THEN** the system SHALL preserve the center chart console as the dominant workspace region and SHALL confine right-side overflow to local scrolling containers
