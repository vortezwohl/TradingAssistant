## ADDED Requirements

### Requirement: System SHALL preserve infrastructure replacement points for Redis migration
The system SHALL define stable replacement points for cache storage, topic broadcasting, and subscription registry so that Redis-backed implementations can replace MEMORY-backed implementations without changing core business service contracts.

#### Scenario: Redis cache can replace memory cache without changing service API
- **WHEN** a Redis-backed cache implementation is introduced
- **THEN** chart, indicator, and history services SHALL continue using the same cache interface contract

#### Scenario: Redis topic bus can replace in-memory topic bus without changing processor flow
- **WHEN** a Redis-backed topic bus implementation is introduced
- **THEN** realtime processors SHALL publish through the same topic bus interface and SHALL not require call-site signature changes

### Requirement: System SHALL use stable serialized keys and payload shapes for migration-sensitive state
The system SHALL use stable topic keys, cache keys, and payload envelope structures for runtime state that may later be externalized to Redis.

#### Scenario: Topic key shape remains stable across backend switch
- **WHEN** runtime broadcast backend changes from MEMORY to Redis
- **THEN** topic identifiers used by publishers and subscribers SHALL remain compatible

#### Scenario: Snapshot payload shape remains stable across backend switch
- **WHEN** runtime cache backend changes from MEMORY to Redis
- **THEN** serialized chart snapshot and indicator snapshot payload structures SHALL remain compatible with existing readers
