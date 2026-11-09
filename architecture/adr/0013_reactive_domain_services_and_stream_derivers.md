---
title: "ADR 0013: Reactive Domain Services and Stream Derivation Architecture"
tags: ["adr", "domain-services", "complex-event-processing", "navigation", "ed-services", "ed-fleet-client"]
created_at: "2026-11-09"
last_updated_at: "2026-11-09"
---

# ADR 0013: Reactive Domain Services and Stream Derivation Architecture

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-09

---

## 1. Context and Problem Statement

Downstream applications require higher-order calculated values (e.g. great-circle bearing to target settlements, relative distance in kilometers, instantaneous vertical speed, and fuel burn rates) that Frontier does not directly emit.

In an event-driven system, calling calculation routines with uninitialized or missing parameters (e.g. computing bearing before a target is locked or before latitude/longitude is emitted) produces runtime exceptions or spurious zero-value coordinates.

We require a formalized domain services package (`src/ed_services`) providing higher-order telemetry derivations through two cooperative access patterns:
* **Pattern 1 (State-Guarded Pull):** Synchronous query methods on the service that inspect the client's current state projection and return `T | None`, strictly guarding against unpopulated inputs.
* **Pattern 2 (Reactive Stream Pipe):** Internal event observers that monitor the client's event bus and dispatch strongly-typed derived events (e.g. `NavBearingUpdated`) only when all calculation prerequisites are satisfied.

---

## 2. Decision Drivers

* **Contract Enforcement:** Base class `TelemetryService` mandating state accessor and dispatcher wiring.
* **Precondition Safety:** Zero runtime exceptions or undefined math errors when game telemetry is partially initialized.
* **Dual Ergonomics:** Support both polling consumers (`client.nav.bearing_to_target()`) and push-reactive listeners (`@client.on(NavBearingUpdated)`).
* **Pure Math Decoupling:** Trigonometric and spatial algorithms (haversine formula, initial bearing) implemented as pure functions for 100% unit testability.
* **Seamless Composition:** Services mounted directly as namespaces on `EliteDangerousClient` (e.g. `client.nav`).

---

## 3. Considered Options

1. **Option 1: Ad-Hoc Script Calculations.** Let each dashboard or script implement its own trigonometry. Rejected due to redundant logic, duplicate bugs, and lack of type-safe events.
2. **Option 2: Bloating `ed_reducer`.** Placing complex trajectory math inside pure state reducers. Rejected because reducers should focus strictly on state folding; heavy analytical math belongs in domain services.
3. **Option 3: Dedicated Domain Services Package (`src/ed_services`).** A decoupled submodule implementing `TelemetryService` with pure algorithms, state-guarded pull accessors, and reactive push dispatching.

---

## 4. Decision Outcome

Chosen option: **Option 3: Dedicated Domain Services Package (`src/ed_services`)**.

### Positive Consequences
* Clear lifecycle and contract enforcement via `TelemetryService`.
* Preconditions are completely encapsulated; callers never receive invalid math results.
* `ed_fleet_client` mounts services cleanly without polluting the root namespace.

### Negative Consequences
* Maintaining internal cache state in services requires careful synchronization with background threads.
