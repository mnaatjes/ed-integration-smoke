---
title: "SDD-006: Live --game-running Hydration Diagnostics via ed-fleet-client"
tags: ["sdd", "design", "diagnostics", "ed-fleet-client", "hydration"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# SDD-006: Live `--game-running` Hydration Diagnostics via `ed-fleet-client`

- **Status:** Approved for Implementation
- **Governing ADR:** [ADR 0017](../adr/0017_game_running_fleet_client_hydration_diagnostics.md)

## 1. Implementation Plan

1. **Helper `_run_fleet_client_diagnostics(reporter, base_url, api_key)` in `scripts/diagnose_telemetry.py`:**
   - Executed when `--game-running` is set.
   - **Connection:** Instantiate `create_client(...)` and probe `connect()` / `disconnect()`.
   - **Snapshot Hydration:** Call `get_snapshot("Status.json")` (and optional `Cargo.json`, `Market.json`).
   - **State Projections:** Inspect `client.state`, `client.ship`, `client.location`, `client.session`.
   - **Domain Services:** Probe `navigation`, `orbital`, `flight_performance`, `combat_analytics`, `astrophysics` (treating state-dependent `None` / N/A as `PASS (N/A)` and schema/hydration exceptions as `FAIL`).
   - **Event & Stream Subscriptions:** Register/unregister a test handler via `on()` / `subscribe()` / `unsubscribe()` and verify `dispatcher`.
   - Report every check immediately via `reporter.report_live(...)`.

## 2. Verification Plan

- `.venv/bin/ruff check scripts/diagnose_telemetry.py`
- `.venv/bin/pytest`
- `.venv/bin/python scripts/diagnose_telemetry.py --target 192.168.1.214:8080 --no-game-running`
