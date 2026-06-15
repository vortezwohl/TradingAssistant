## ADDED Requirements

### Requirement: System SHALL provide explicit time-scale switching across short and long horizons
The system SHALL provide visible time-scale controls for the primary chart console, covering short-horizon intraday views and long-horizon reference views within the same workspace.

#### Scenario: Time-scale selector covers the required range
- **WHEN** the user inspects the chart controls
- **THEN** the system SHALL provide visible time-scale choices covering `30S`, `1M`, `5M`, `15M`, `1H`, `4H`, `1D`, `1W`, `1MO`, and `1Y`

#### Scenario: Time-scale switching updates the active chart context in place
- **WHEN** the user selects a different time scale
- **THEN** the system SHALL update the active chart and dependent study context without requiring page navigation or leaving the fixed terminal workspace

### Requirement: System SHALL distinguish main-chart overlays from routed lower studies
The system SHALL distinguish between indicators that belong on the primary price pane and indicators that belong in route-based lower study panes.

#### Scenario: Main chart supports overlay indicators
- **WHEN** the user toggles overlay studies on the primary chart
- **THEN** the system SHALL support overlays such as `MA`, `EMA`, `BOLL`, and `VWAP` directly on the main price chart surface

#### Scenario: Lower study panes are driven by the active analysis route
- **WHEN** the user switches to a route that represents non-overlay studies
- **THEN** the system SHALL update the lower study strip with route-appropriate studies instead of stacking every indicator permanently under the chart

### Requirement: System SHALL provide explicit route switching for technical study groups
The system SHALL provide a visible route-switching control for grouped analysis contexts so users can move among major study modes without leaving the chart console.

#### Scenario: Route selector exposes grouped analysis contexts
- **WHEN** the user inspects route controls in the chart workspace
- **THEN** the system SHALL provide visible route choices for `Main`, `Momentum`, `Trend`, `Volatility`, `Order Flow`, and `Microstructure`

#### Scenario: Route switching changes lower studies and route metadata together
- **WHEN** the user activates a different route
- **THEN** the system SHALL update the route state, route summary metadata, and linked study panes together so the user can clearly understand the active analysis context

### Requirement: System SHALL support route-aware lower study panes inside the same workspace
The system SHALL provide a lower study strip with multiple linked panes so grouped technical readings can be compared without replacing the main chart.

#### Scenario: Lower study strip shows multiple linked panes
- **WHEN** a route is active in the chart console
- **THEN** the system SHALL show multiple lower study panes that belong to the active route instead of collapsing the route into a single-value summary

#### Scenario: Lower studies remain within the desktop fixed workspace
- **WHEN** the lower study strip is active on desktop
- **THEN** the system SHALL keep it inside the center chart console region without forcing full-page vertical expansion

### Requirement: System SHALL keep route and overlay controls understandable to financial users
The system SHALL label route controls and overlay controls using concise market-analysis language rather than engineering or implementation terminology.

#### Scenario: Overlay and route controls read like trading workstation controls
- **WHEN** the user scans the control rows above the chart
- **THEN** the system SHALL present the controls as chart overlays and analysis routes rather than as transport, debug, or internal system controls
