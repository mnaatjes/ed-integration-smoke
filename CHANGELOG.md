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
- Added executable CLI runner `scripts/run_telemetry_harness.py` with full-screen 3-pane Rich TUI dashboard (Header, Chapter Progress & Live In-Game Events middle split, and Audits & Achievements bottom feed).
- Added JSONL domain mismatch streaming ledger (`data/domain_mismatches.jsonl`) for human-readable audit logs alongside SQLite storage.
- Added telemetry delta gating in `TelemetryPipeline` to prevent persisting duplicate `Status.json` 1-second snapshots when flags and GUI focus are unchanged.
- Added exemplar reservoir sampling in `TelemetryPipeline` to retain up to $N$ raw samples per event type while continuously admitting events containing novel property keys.
- Added database maintenance utilities (`vacuum_database`, `checkpoint_wal`) to reclaim disk space.
- Added PEP 561 `py.typed` marker to `src/ed_integration_smoke`.
- Integrated `ed-models` v0.2.1 supporting polymorphic `Scan` resolution and `GameModeChange` domain events.

