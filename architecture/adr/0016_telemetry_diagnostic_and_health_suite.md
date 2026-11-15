---
title: "ADR 0016: Telemetry Diagnostic and Health Verification Suite"
tags: ["adr", "diagnostics", "ed-telemetry", "ed-fleet-client", "ed_cli_core"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0016: Telemetry Diagnostic and Health Verification Suite

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-integration-smoke` (`scripts/`, `src/ed_cli_core`, `ed-fleet-client`)

## 1. Context & Problem Statement

With `ed-telemetry` (`v1.0.7`) deployed as a standalone host daemon (supporting both `127.0.0.1:8080` and LAN hosts such as `192.168.1.214:8080`), we need a dedicated diagnostic and smoke-testing script in `scripts/` built on `ed-fleet-client` and `src/ed_cli_core` to verify endpoint health, latency, infrastructure readiness, and contract compliance in real time.

## 2. Decision

Implement a CLI diagnostic suite (`scripts/diagnose_telemetry.py`) with the following capabilities:

1. **Connection & Mode Parameters:**
   - `--target` (`host:port`, default `127.0.0.1:8080`, supporting remote hosts like `192.168.1.214:8080`).
   - `--api-key` (optional pre-shared API key for authenticated `ed-telemetry` deployments).
   - `--game-running` / `--no-game-running` (toggles live-telemetry assertions vs. idle/offline-game baseline checks).
2. **Diagnostic Checks:**
   - **System Health & Infrastructure:** Probe `GET /api/v1/system/health` (and legacy `GET /api/v1/health`), verify `status == "ok"`, `version`, `db.ok == True` (SQLite readiness), and `journal_dir.configured == True`.
   - **Complete Endpoint Coverage (all 14 canonical endpoints from `ed-telemetry/docs/reference/http_api_endpoints.md`):**
     - System Plane: `GET /api/v1/system/health`, `GET /api/v1/system/watcher`, `GET /api/v1/system/logs`, `POST /api/v1/system/control`
     - State & Status Plane: `GET /api/v1/state`, `GET /api/v1/state/heartbeat`, `GET /api/v1/status`
     - Snapshots Plane: `GET /api/v1/snapshots`, `GET /api/v1/snapshots/{name}`
     - Journal Plane: `GET /api/v1/journal/latest`, `GET /api/v1/journal/events`
     - Events & Stream Plane: `GET /api/v1/events/query`, `GET /api/v1/events/queue`, `GET /api/v1/events/stream` (SSE)
   - **Latency & Speed:** Measure round-trip latency (ms) per endpoint and report min/avg/max.
   - **Value & Contract Assertions:** Compare returned payloads against anticipated schemas/values (e.g., `ed-fleet-client` DTO hydration, non-empty `Status.json` fields when `--game-running` is set).
3. **Real-Time Presentation (`src/ed_cli_core`):**
   - Stream each check result live to the terminal using `ed_cli_core` Rich presentation components (status badges, latency column, expected vs. actual summary table), adding any missing reusable table/progress/check-row components to `src/ed_cli_core`.

## 3. Consequences

- **Positive:** Provides an operator-friendly, repeatable verification tool for both local and split-host `ed-telemetry` deployments.
- **Negative / Trade-offs:** Requires keeping endpoint assertions aligned with upstream `ed-telemetry` API changes.
