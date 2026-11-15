---
title: "ADR 0017: Live --game-running Hydration Diagnostics via ed-fleet-client"
tags: ["adr", "diagnostics", "ed-fleet-client", "hydration", "smoke-test"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0017: Live `--game-running` Hydration Diagnostics via `ed-fleet-client`

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-integration-smoke` (`scripts/diagnose_telemetry.py`, `ed-fleet-client`)

## 1. Context & Problem Statement

`scripts/diagnose_telemetry.py` (ADR 0016 / SDD-005) currently verifies HTTP/SSE reachability for all 14 `ed-telemetry` endpoints and instantiates `ed_fleet_client.create_client()`, but does not exercise `EliteDangerousClient` facade methods against live game data when `--game-running` is passed.

## 2. Decision

Extend `scripts/diagnose_telemetry.py` under `--game-running` to run end-to-end hydration and domain-service diagnostics through `EliteDangerousClient`, streaming each result live to the terminal via `DiagnosticReporter.report_live()`:

1. **Facade Connection & Lifecycle:**
   - `connect()` / `disconnect()` against the target `ed-telemetry` host (`--target`, `--api-key`).
2. **State & Snapshot Hydration:**
   - `get_snapshot()` for `Status.json` (and optional `Market.json`, `Shipyard.json`, `Outfitting.json`, `Cargo.json`).
   - State projections: `state`, `ship`, `location`, `session` (asserting non-empty commander/ship/system fields when live).
3. **Domain Service Probes (Edge-Case Aware):**
   - `navigation`, `orbital`, `flight_performance`, `combat_analytics`, `astrophysics`: invoke read/compute paths and treat "not applicable in current game state" (e.g., no active target or not docked) as `PASS (N/A)` rather than a false failure, while catching schema/hydration exceptions as `FAIL`.
4. **Live Event & Stream Subscription:**
   - `on()` / `subscribe()` / `unsubscribe()` / `dispatcher`: verify handler registration and SSE event dispatch without blocking indefinitely.
5. **Real-Time Terminal Reporting:**
   - Every check reports immediately as it executes via `DiagnosticReporter.report_live()` with `[PASS]` / `[FAIL]`, latency (`ms`), and hydrated summary detail.

## 3. Consequences

- **Positive:** Validates true end-to-end DTO hydration and schema compatibility between `ed-telemetry` and `ed-fleet-client` under live game conditions.
- **Negative / Trade-offs:** Requires graceful handling of state-dependent fields (docked vs. supercruise vs. combat) so valid idle states do not produce false negatives.
