# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Authored ADR 0002 defining the live telemetry verification vehicle, SQLite persistence schema with WAL mode, and in-game target coverage tracker.
- Authored SDD-003 specifying component architecture, pipeline flow, and domain mismatch recording.
- Implemented `TelemetryStorageEngine` with SQLite WAL mode managing `raw_journal_events`, `target_coverage`, and `domain_mismatches`.
- Implemented target coverage registry (`build_all_targets`) cataloging all 258+ Frontier Journal events across Chapters 2–13 and 47 cockpit status telemetry flags.
- Implemented `TelemetryPipeline` dispatching raw payloads into `ed-models` domain deserializers (`parse_journal_event` and `parse_telemetry`) with automatic mismatch detection.
- Implemented `TelemetryIngressClient` providing async HTTP polling and streaming ingestion via `ed-transport`.
- Added executable CLI runner `scripts/run_telemetry_harness.py` with real-time terminal coverage progress bars and diagnostic reporting.
- Added PEP 561 `py.typed` marker to `src/ed_integration_smoke`.
- Integrated `ed-models` v0.2.0 git dependency and verified complete test suite in `tests/test_telemetry_harness.py`.
