## ADDED Requirements

### Requirement: System SHALL provide dedicated market depth and order book modules
The system SHALL provide dedicated desktop workspace modules for market depth and order book inspection instead of reducing microstructure information to summary cards.

#### Scenario: Right rail exposes market depth ladder
- **WHEN** the watch page is rendered on a desktop-width viewport
- **THEN** the system SHALL provide a market depth module that presents multi-level bid and ask depth in a dedicated workspace region

#### Scenario: Right rail exposes order book view
- **WHEN** the user inspects current trading interest for the active instrument
- **THEN** the system SHALL provide an order book module with bid-side and ask-side levels, prices, and sizes in a dedicated workspace region

### Requirement: System SHALL provide recent prints or time-and-sales context
The system SHALL provide a recent prints or time-and-sales view so the user can inspect the latest trade flow alongside market depth and order book context.

#### Scenario: Recent trade flow remains accessible from the microstructure workspace
- **WHEN** the user needs to inspect the latest executed prints
- **THEN** the system SHALL provide a recent prints or equivalent time-and-sales module within the market microstructure workspace

#### Scenario: Microstructure modules do not force full-page scrolling
- **WHEN** depth, order book, or time-and-sales rows exceed the available vertical space
- **THEN** the system SHALL keep those modules inside local scrolling containers without breaking the fixed desktop workspace