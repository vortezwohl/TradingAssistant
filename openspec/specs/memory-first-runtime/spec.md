# memory-first-runtime Specification

## Purpose
TBD - created by archiving change build-memory-first-market-monitor. Update Purpose after archive.
## Requirements
### Requirement: System SHALL use MEMORY as the default runtime state backend
The system SHALL run without Redis in the default deployment path and SHALL keep runtime cache, topic broadcast state, and subscription registry state in process memory during the first implementation phase.

#### Scenario: Default startup does not require Redis
- **WHEN** the application starts in the default local deployment mode
- **THEN** it SHALL initialize successfully without requiring any Redis service or Redis configuration

#### Scenario: Runtime state is available in memory
- **WHEN** a chart session subscribes to a symbol topic
- **THEN** the system SHALL store the active topic state, hot cache entries, and subscription mappings in in-memory runtime structures

### Requirement: System SHALL access runtime state through abstract infrastructure interfaces
The system SHALL use abstract interfaces for cache access, topic broadcast, and subscription registry so that business logic is not coupled to process-local dictionaries.

#### Scenario: Cache access uses interface abstraction
- **WHEN** a service reads or writes chart bootstrap data, bar snapshots, or indicator snapshots
- **THEN** it SHALL do so through the cache interface rather than directly mutating module-level dictionaries

#### Scenario: Topic broadcast uses interface abstraction
- **WHEN** a realtime processor emits an update for chart or quote subscribers
- **THEN** it SHALL publish through the topic bus abstraction rather than directly iterating over low-level socket collections

