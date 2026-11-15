---
title: "SDD-005: Telemetry Diagnostic and Health Verification Suite"
tags: ["sdd", "design", "diagnostics", "ed-telemetry", "ed-fleet-client", "ed_cli_core"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# SDD-005: Telemetry Diagnostic and Health Verification Suite

- **Status:** Approved for Implementation
- **Governing ADR:** [ADR 0016](../adr/0016_telemetry_diagnostic_and_health_suite.md)

## 1. Implementation Plan

1. **CLI Presentation Component (`src/ed_cli_core/ed_cli_core/diagnostics.py`):**
   - `DiagnosticCheckResult`: dataclass (`name`, `endpoint`, `passed`, `latency_ms`, `detail`).
   - `DiagnosticReporter`: streams each check result live to the terminal with `[PASS]` / `[FAIL]` badges and latency, then prints a Rich summary table (total, passed, failed, min/avg/max latency).
2. **Diagnostic Script (`scripts/diagnose_telemetry.py`):**
   - CLI arguments: `--target` (`127.0.0.1:8080`), `--api-key` (optional), `--game-running` / `--no-game-running`.
   - Exercises all 14 canonical `ed-telemetry` endpoints:
     - System Plane: `/api/v1/system/health`, `/api/v1/system/watcher`, `/api/v1/system/logs`, `POST /api/v1/system/control` (read-only/safe status probe)
     - State & Status Plane: `/api/v1/state`, `/api/v1/state/heartbeat`, `/api/v1/status`
     - Snapshots Plane: `/api/v1/snapshots`, `/api/v1/snapshots/{name}`
     - Journal Plane: `/api/v1/journal/latest`, `/api/v1/journal/events`
     - Events & Stream Plane: `/api/v1/events/query`, `/api/v1/events/queue`, `/api/v1/events/stream` (SSE)
   - Verifies `db.ok == True`, `journal_dir.configured == True`, and `ed_fleet_client.EliteDangerousClient` connectivity.

## 2. Verification Plan

- `.venv/bin/ruff check .`
- `.venv/bin/pytest`
