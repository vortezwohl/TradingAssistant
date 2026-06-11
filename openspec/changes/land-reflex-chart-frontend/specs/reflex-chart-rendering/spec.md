## ADDED Requirements

### Requirement: Reflex frontend SHALL render chart bootstrap data into a visible chart view
The Reflex frontend SHALL convert chart bootstrap payloads into a visible chart view so that users can see historical bars and initial indicator state immediately after opening the page.

#### Scenario: Bootstrap response populates the chart
- **WHEN** the page requests chart bootstrap for a symbol and period
- **THEN** the frontend SHALL render the returned historical bars and initial indicator snapshot into the chart container before realtime updates begin

#### Scenario: Bootstrap failure is surfaced to the page
- **WHEN** the bootstrap request fails or returns invalid chart payload
- **THEN** the frontend SHALL show an explicit load failure state instead of leaving the chart area silently empty

### Requirement: Reflex frontend SHALL apply realtime chart updates in the browser without persisting high-frequency state in Reflex State
The Reflex frontend SHALL apply chart update messages directly inside the browser chart component and SHALL keep high-frequency bar mutations outside Reflex State.

#### Scenario: Realtime bar update mutates chart locally
- **WHEN** the frontend receives a `bar_update` payload for the active chart topic
- **THEN** the browser chart component SHALL update the visible series without requiring Reflex State to store the full high-frequency bar stream

#### Scenario: Inactive topics do not mutate the active chart
- **WHEN** the frontend receives an update for a topic that is no longer active after a page switch
- **THEN** the update SHALL be ignored by the active chart instance

### Requirement: Reflex frontend SHALL support symbol, timeframe, and indicator interactions as chart context switches
The Reflex frontend SHALL treat symbol, timeframe, and indicator changes as chart context switches that rebuild the visible chart from a fresh bootstrap plus a new realtime subscription.

#### Scenario: Symbol switch rebuilds chart context
- **WHEN** the user selects a different symbol
- **THEN** the frontend SHALL dispose the previous chart context, request a fresh bootstrap, and subscribe to the new chart topic

#### Scenario: Indicator switch refreshes visible overlays
- **WHEN** the user enables or disables an indicator
- **THEN** the frontend SHALL refresh the visible chart overlays to match the new indicator set
