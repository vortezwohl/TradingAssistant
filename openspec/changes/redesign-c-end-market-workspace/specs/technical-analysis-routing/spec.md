## ADDED Requirements

### Requirement: System SHALL distinguish main-chart overlays from route-based studies
The system SHALL distinguish between indicators that belong directly on the primary price chart and studies that belong in a secondary route-based analysis console.

#### Scenario: Main chart supports overlay studies
- **WHEN** the user inspects the primary price chart
- **THEN** the system SHALL support overlay studies such as moving averages, exponential moving averages, Bollinger Bands, and VWAP on the main chart surface

#### Scenario: Secondary studies use routed analysis views
- **WHEN** the user switches to a non-overlay technical study
- **THEN** the system SHALL provide a dedicated analysis route for studies such as MACD, RSI, KDJ, ATR, OBV, or ADX instead of forcing all studies into the default chart view

### Requirement: System SHALL provide explicit analysis route switching
The system SHALL provide an explicit route-switching interaction for technical study groups so users can move among chart-analysis contexts without leaving the workspace.

#### Scenario: User can switch technical study groups
- **WHEN** the user wants to inspect different technical categories such as trend, momentum, volatility, or order-flow
- **THEN** the system SHALL provide a visible route-switching control for those categories inside the chart workspace

#### Scenario: Route switching preserves the fixed desktop workspace
- **WHEN** the user changes the technical analysis route
- **THEN** the system SHALL update the active analysis view without converting the page into a vertically expanding layout