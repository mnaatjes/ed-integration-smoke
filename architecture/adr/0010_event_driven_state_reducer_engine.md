---
title: "ADR 0010: Event-Driven State Reducer Engine for Materialized Telemetry Projections"
tags: ["adr", "state-machine", "event-sourcing", "reducers", "ed-reducer", "ed-models"]
created_at: "2026-11-09"
last_updated_at: "2026-11-09"
---

# ADR 0010: Event-Driven State Reducer Engine for Materialized Telemetry Projections

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-09

---

## 1. Context and Problem Statement

Downstream consumers (e.g. cockpit overlays, voice assistants, fleet telemetry dashboards) require an accurate, synchronized snapshot of current player state (e.g., current star system, current ship loadout, fuel/pips telemetry, session info). 

Currently, `ed-telemetry` provides raw event streams, and `ed_hydrator` translates those payloads into typed `ed-models` domain entities. However, applications must manually inspect and accumulate individual events (e.g. tracking `FSDJump` to know where the ship is, or tracking `StatusTelemetry` for pips). In earlier experiments (such as `ed-resolver`), state mutation logic was entangled with network transport and mutable dictionaries, creating fragile coupling and state drift.

We require a decoupled workspace package (`src/ed_reducer`) implementing pure functional event reducers that project sequential `ed-models` events and cockpit telemetry into an immutable, materialized client state projection.

---

## 2. Decision Drivers

* **Pure Functional Reducers:** State transitions must follow the pure signature $(\text{State}, \text{Event}) \to \text{New State}$ without I/O or side effects.
* **Selective Event Projection:** Over 70% of Frontier events are ephemeral/transient (e.g. `Music`, `ReceiveText`, `FSSSignalDiscovered`) and should not mutate durable state projections. Reducers must focus strictly on state-mutating events (`FSDJump`, `Location`, `CarrierJump`, `StatusTelemetry`, `Commander`, `LoadGame`).
* **Immutable Materialized Projections:** Expose immutable dataclass snapshots (`ClientStateProjection`, `LocationProjection`, `ShipProjection`, `SessionProjection`) preventing caller corruption.
* **Decoupled Architecture:** Zero coupling to network transports, SSE loops, or file system watchers; operates exclusively on hydrated `ed-models` domain entities.
* **Thread-Safe State Engine:** Provide a `TelemetryStateEngine` that accumulates incoming events and exposes thread-safe current state accessors.

---

## 3. Considered Options

1. **Option 1: Monolithic In-Place Mutable State Object.** Maintain a single global dictionary mutated in-place by listeners. Rejected due to race conditions, untracked mutations, and inability to travel backwards or verify transitions.
2. **Option 2: Reducers for Every Single Event in `ed-models`.** Authoring ~300 reducers for every known Frontier event. Rejected as an anti-pattern: transient telemetry events do not alter enduring state.
3. **Option 3: Modular Slice Reducers with Immutable Projections (`src/ed_reducer`).** Group state into logical slices (`location`, `ship`, `session`) with targeted pure reducers and a thread-safe engine.

---

## 4. Decision Outcome

Chosen option: **Option 3: Modular Slice Reducers with Immutable Projections (`src/ed_reducer`)**.

### Positive Consequences
* Clear separation of concerns between event transport (`ed_telemetry_client`, `ed_stream_monitor`), domain hydration (`ed_hydrator`), and state projection (`ed_reducer`).
* Deterministic, 100% unit-testable transitions using standard Python immutable dataclasses.
* Direct compatibility with high-level reactive client facades (`@client.on(...)` + `client.state`).

### Negative Consequences
* Slices must be updated as new state-mutating events (such as Odyssey on-foot equipment changes) are added to `ed-models`.
