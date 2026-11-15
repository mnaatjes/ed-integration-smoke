---
title: "ed-fleet-client v0.1.0 Integration & Context Hydration Guide"
tags: ["context", "ed-fleet-client", "integration", "v0.1.0", "refactor"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# `ed-fleet-client` (`v0.1.0`) Integration & Context Hydration Guide

This document provides complete capability, interface, and migration context for `ed-fleet-client` (`v0.1.0`) so `agy-gemini` in `ed-integration-smoke` can refactor `ed-integration-smoke/src/`, remove superseded prototype submodules, and run integration tests against the published SDK.

---

## 1. Package Source & Installation

* **Repository:** `https://github.com/mnaatjes/ed-fleet-client`
* **Release Tag:** `v0.1.0`
* **Install via `uv`:**

```bash
uv add "ed-fleet-client @ git+https://github.com/mnaatjes/ed-fleet-client.git@v0.1.0"
```

* **Runtime Architecture:** `ed-fleet-client` connects over HTTP/SSE to an independently running `ed-telemetry` API server (`http://{host}:{port}/api/v1/...`). It does **not** take `ed-telemetry` as a Python dependency.

---

## 2. Public Entry Point & Control Plane Facade

```python
from ed_fleet_client import EliteDangerousClient, create_client
from ed_fleet_client.adapters.driven.telemetry_http import TelemetryConnectionConfig
```

### `EliteDangerousClient` (`ed_fleet_client.adapters.driving.facade.EliteDangerousClient`)

* **Lifecycle:**
  * `async def connect() -> None`
  * `async def disconnect() -> None`
  * `async with create_client(config) as client:`
* **Event Listeners (`TelemetryEventDispatcher`):**
  * `@client.on(event_type)` — decorator for sync/async `ed_models` event handlers
  * `client.subscribe(event_type, handler) -> Subscription`
  * `client.unsubscribe(subscription) -> bool`
* **High-Frequency State Projections (`TelemetryStateEngine`):**
  * `client.state -> ClientStateProjection`
  * `client.location -> LocationProjection`
  * `client.session -> SessionProjection`
  * `client.ship -> ShipProjection`
* **Companion Snapshots (`UC-03`):**
  * `await client.get_snapshot(name: str, endpoint: str) -> RawSnapshotRecord`
* **Domain Services:**
  * `client.orbital -> GetOrbitalMetricsUseCase`
  * `client.navigation -> NavigationService`
  * `client.astrophysics -> AstrophysicsService`
  * `client.flight_performance -> FlightPerformanceService`
  * `client.combat_analytics -> CombatAnalyticsService`

---

## 3. Superseded Prototype Submodules in `ed-integration-smoke/src/`

All 7 prototype submodules below are now consolidated into `ed-fleet-client` `v0.1.0` and can be removed from `ed-integration-smoke/src/` once imports are updated:

| Prototype Submodule | New Location in `ed-fleet-client` |
| :--- | :--- |
| `ed_dispatcher` | `ed_fleet_client.core.domain.dispatcher` |
| `ed_reducer` | `ed_fleet_client.core.domain.state` |
| `ed_services` | `ed_fleet_client.core.domain.services` |
| `ed_hydrator` | `ed_fleet_client.adapters.driving.hydrator` |
| `ed_stream_monitor` | `ed_fleet_client.adapters.driving.stream` |
| `ed_telemetry_client` | `ed_fleet_client.adapters.driven.telemetry_http` |
| `ed_fleet_client` | `ed_fleet_client.adapters.driving.facade` & `ed_fleet_client.bootstrap.container` |

*(Note: `ed_cli_core` remains in `ed-integration-smoke` and should be updated to import `EliteDangerousClient` and `create_client` from `ed_fleet_client`.)*

---

## 4. Verification Commands in `ed-integration-smoke`

```bash
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/mypy scripts/ tests/
```
