## ADDED Requirements

### Requirement: System SHALL preserve readable alignment in dense left-rail rows
The system SHALL keep watchlist, movers, and snapshot text aligned to stable row baselines even when the left rail is densely packed.

#### Scenario: Watchlist rows keep stable vertical alignment
- **WHEN** the watchlist renders primary codes, secondary metadata, last price, and change values
- **THEN** the system SHALL keep those fields aligned within the row without visible vertical drift or partial clipping

#### Scenario: Snapshot cells keep complete readable value blocks
- **WHEN** the lower-left snapshot module renders compact labels, primary values, and secondary captions
- **THEN** the system SHALL keep those text blocks readable within the cell bounds without truncating critical value text unexpectedly

### Requirement: System SHALL apply explicit truncation and overflow behavior in narrow left-rail regions
The system SHALL define predictable overflow behavior for narrow left-rail text so dense terminal content remains readable instead of being cut off irregularly.

#### Scenario: Secondary labels truncate predictably when space is limited
- **WHEN** watchlist or movers metadata exceeds the available horizontal space
- **THEN** the system SHALL truncate or clip that secondary text using a consistent policy that preserves the primary symbol identity and numeric fields

#### Scenario: Left-rail modules do not hide text because of container overflow mistakes
- **WHEN** dense rows are rendered inside local-scroll panels
- **THEN** the system SHALL avoid container sizing or padding rules that cause text to render outside the visible bounds of the row or cell
