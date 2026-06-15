## ADDED Requirements

### Requirement: System SHALL provide hover-following detail inside the terminal chart console
The system SHALL provide a hover detail surface inside the terminal chart console so users can inspect the active candle and linked indicator values by moving the pointer across the chart region.

#### Scenario: Primary chart hover shows active candle detail
- **WHEN** the user hovers over a candle position in the primary chart stage
- **THEN** the system SHALL show a detail surface inside the chart console with the active bar's price and contextual values for that hovered position

#### Scenario: Hover detail follows the active chart unit
- **WHEN** the user moves the pointer from one chart position to another
- **THEN** the system SHALL update the hover detail surface to the newly active chart unit instead of leaving it pinned to the latest bar only

### Requirement: System SHALL synchronize lower-study hover values with the primary chart hover position
The system SHALL keep lower-study inspection tied to the same active chart index as the primary chart hover interaction.

#### Scenario: Lower studies update with the active hover index
- **WHEN** the user hovers a chart position that maps to an existing study point
- **THEN** the system SHALL show lower-study values that correspond to that same hovered position

#### Scenario: Route switching preserves hover-readout consistency
- **WHEN** the user changes the active analysis route and then hovers the chart console
- **THEN** the system SHALL show hover detail that reflects the active route's study set for the same hovered index

### Requirement: System SHALL keep hover detail inside the fixed terminal workspace
The system SHALL present chart hover detail without breaking the fixed desktop terminal posture or requiring full-page expansion.

#### Scenario: Hover detail renders as an in-console terminal surface
- **WHEN** hover detail becomes visible in the desktop chart console
- **THEN** the system SHALL render it as a compact in-console surface that remains inside the chart workspace bounds

#### Scenario: Hover exit clears transient chart inspection state
- **WHEN** the pointer leaves the chart interaction region
- **THEN** the system SHALL clear or reset transient hover detail state instead of leaving a stale historical readout active indefinitely
