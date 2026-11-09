---
title: "ADR 0012: Unified Reactive Fleet Client Composition Facade"
tags: ["adr", "facade", "client-sdk", "reactive", "ed-fleet-client", "composition"]
created_at: "2026-11-09"
last_updated_at: "2026-11-09"
---

# ADR 0012: Unified Reactive Fleet Client Composition Facade

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-09

---

## 1. Context and Problem Statement

`ed-integration-smoke` has established four specialized internal packages:
1. `ed_telemetry_client`: HTTP REST client for synchronous telemetry endpoints.
2. `ed_stream_monitor`: Low-latency Server-Sent Events (SSE) streaming and file-delta detection.
3. `ed_hydrator`: Anti-Corruption Layer (ACL) parsing telemetry envelopes into typed `ed-models`.
4. `ed_reducer` (ADR 0010): Pure-functional event folding into immutable state projections (`ClientStateProjection`).
5. `ed_dispatcher` (ADR 0011): Exhaustive, type-safe observer event registry with error isolation.

End-users (overlay developers, voice assistant authors, fleet dashboard engineers) should not be forced to manually wire these disparate packages together. We require a single, unified client facade (`EliteDangerousClient`) that presents a comprehensive, cohesive API while encapsulating background thread lifecycles, stream recovery, and data pipeline coordination.

---

## 2. Decision Drivers

* **Single Entry Point:** Consumers interact solely with `EliteDangerousClient`.
* **Four Canonical Capability Groups:**
  * **Group A (Reactive Subscriptions):** `@client.on(EventType)` decorator and `client.subscribe()`.
  * **Group B (Materialized State Projections):** Thread-safe `client.state` exposing `location`, `ship`, `session`.
  * **Group C (On-Demand Query Services):** Synchronous/async queries (`get_status()`, `get_latest_journal()`, `query_events()`).
  * **Group D (Lifecycle Management):** Synchronous blocking (`client.start()`), background worker thread (`client.start_background()` / `stop()`), and async generator (`client.stream()`).
* **Order of Execution Guarantee:** Ingested events must be folded through the state reducer *before* notifying event listeners, ensuring callbacks observe up-to-date state.
* **Resilient Stream Ingestion:** Automatic claim-check resolution from SSE file deltas and journal event streams into typed `ed-models`.

---

## 3. Considered Options

1. **Option 1: Ad-Hoc Script Composition.** Requiring application scripts to instantiate all 5 packages manually. Rejected due to high cognitive load, boilerplate duplication, and race conditions during stream reconnection.
2. **Option 2: Megapackage Merging.** Consolidating all source files into a single flat repository. Rejected because keeping modules decoupled allows independent testing and unit verification.
3. **Option 3: Composition Facade (`src/ed_fleet_client`).** A dedicated composition library that depends on internal workspace components and exports `EliteDangerousClient` as the public interface.

---

## 4. Decision Outcome

Chosen option: **Option 3: Composition Facade (`src/ed_fleet_client`)**.

### Positive Consequences
* Intuitive, idiomatic Python developer experience (`from ed_fleet_client import EliteDangerousClient`).
* Clean separation of concerns with full encapsulation of internal networking and state reduction.
* Thread-safe execution suitable for CLI scripts, GUI loops (PyQt/Textual), and async web servers.

### Negative Consequences
* Facade adds one layer of delegation between public methods and underlying adapters.
