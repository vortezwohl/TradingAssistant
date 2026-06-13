## ADDED Requirements

### Requirement: System SHALL present the desktop watch page as a fixed-viewport market workspace
The system SHALL render the desktop watch page as a fixed-viewport market workspace that fills the browser height and avoids whole-page scrolling during normal use.

#### Scenario: Desktop viewport locks the overall page height
- **WHEN** the watch page is opened on a desktop-width viewport
- **THEN** the system SHALL constrain the root workspace to the viewport height and SHALL prevent browser-level vertical scrolling for the primary market layout

#### Scenario: Inner panels scroll without moving the whole page
- **WHEN** self-selected symbols, market cards, or similar dense lists exceed the available vertical space
- **THEN** the system SHALL keep the main workspace fixed and SHALL provide scrolling only inside the affected panel containers

### Requirement: System SHALL use business-facing terminology for the user workspace
The system SHALL use market and trading terminology that a financial practitioner can understand directly, and SHALL avoid exposing engineering or integration terminology in the default user-facing workspace.

#### Scenario: Top-level labels use market language
- **WHEN** the page renders filters, summary cards, titles, and helper text
- **THEN** the system SHALL use labels such as instrument, latest price, change, turnover, trend, watchlist, market depth, order book, and session instead of engineering-facing labels and transport terminology

#### Scenario: Engineering diagnostics stay out of the default workspace
- **WHEN** connection details, subscription payloads, bootstrap state, or equivalent diagnostics are available in the product
- **THEN** the system SHALL hide them from the default user-facing workspace and SHALL expose them only through a secondary development-oriented path

### Requirement: System SHALL provide a customer-facing market header banner
The system SHALL display a compact market header banner that communicates product identity, current market context, and the selected instrument's core summary before the detailed workspace modules.

#### Scenario: Header banner shows market context and key numbers
- **WHEN** the watch page loads successfully
- **THEN** the system SHALL show a banner containing product identity, current market session context, selected instrument, and compact key metrics such as latest price and change

#### Scenario: Header banner remains subordinate to the chart console
- **WHEN** the user scans the first screen
- **THEN** the system SHALL keep the header banner visually compact so the chart console remains the dominant analysis surface

### Requirement: System SHALL use an English terminal tone in the static workspace reference
The system SHALL use English labels and English workspace copy in the static design reference used for the terminal-style redesign.

#### Scenario: Static reference avoids mixed-language user labels
- **WHEN** the static design reference is reviewed or implemented
- **THEN** the system SHALL use English user-facing labels, route names, panel names, and helper text throughout the reference