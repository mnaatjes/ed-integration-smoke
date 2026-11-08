---
title: "ADR 0004: Ambient Telemetry Facade Prototype"
tags: ["adr", "telemetry", "architecture", "facade", "archetypes", "state", "ed-models"]
created_at: "2026-11-03"
last_updated_at: "2026-11-06"
---

# ADR 0004: Ambient Telemetry Facade Prototype

* Status: Accepted
* Date: 2026-11-03 (Updated 2026-11-06)

## Context and Problem Statement

Frontier client telemetry is temporal, fragmented, and heterogeneous. Inbound telemetry arrives via two starkly different channels:
1. High-frequency 1 Hz status ticks (`Status.json`) carrying continuous integer bitfields and scalar measurements.
2. Low-frequency discrete journal events (`Journal.*.log`) emitted upon specific game occurrences.

Downstream applications (copilots, in-game overlays, dashboard TUI visualizers, and outbound API aggregators) require instantaneous access to contextual truths, such as:
* *Where is the commander?* (`get_location()`)
* *What ship/vessel is active?* (`get_vessel()`)
* *Is the commander currently disembarked on foot?* (`is_on_foot()`)
* *What is the current flight state?* (`get_flight_mode()`)

Without a consolidated query surface, every downstream consumer must independently parse raw journal payloads, track historical event sequences, and perform bitwise math. This leads to duplicate state tracking, inconsistent heuristics, and high maintenance overhead across fleet tools.

Furthermore, applications can be launched mid-session or during cold game starts before any Epoch Milestone (e.g., `Location` or `FSDJump`) has been emitted in the active session stream. The facade query interface must handle these unhydrated windows deterministically without throwing unexpected exceptions or hanging callers.

## Decision Drivers

* **Ergonomic, Direct Query Interface:** Provide typed, synchronous getters returning consolidated dataclasses (`LocationSnapshot | None`, `VesselSnapshot | None`, `FlightMode`).
* **Deterministic Cold-Start Handling:** Seamlessly recover prior active state upon process startup without requiring downstream consumers to implement defensive exception-handling wrappers.
* **Behavioral Archetype Foundation:** The mechanism of capturing and mutating state must adhere strictly to the mathematical archetypes defined in ADR 0003 (Edge-Transition, Metric-Quantizer, Epoch-Milestone, Context-Mutator).
* **Decoupled from Event Sequence:** The facade must remain resilient against missed events, client crashes, or historical log replays.
* **Rapid Prototyping in `ed-integration-smoke`:** Prototype the interface and semantics in `ed-integration-smoke` to validate against real-time gameplay before extracting to an upstream core fleet package (e.g., `ed-models` or a dedicated client library).

## Considered Options

1. **Option 1: Raw SQLite State Queries.** Write all events to SQLite and query latest rows per query method. Rejected due to synchronous disk I/O latency, lock contention during high-frequency ingestion, and serialization overhead.
2. **Option 2: Ad-Hoc Global Dictionary.** Store key-value pairs in an unvalidated dictionary. Rejected due to lack of type safety, missing edge detection, and fragile state mutation.
3. **Option 3: Ambient Telemetry Facade grounded in ADR 0003 Archetypes (Selected).** An in-memory, thread-safe domain surface backed by the four mathematical archetypes from ADR 0003.

### Cold-Start Hydration Strategies Evaluated

* **Strategy A: Raise Uninitialized Exception (`StateNotReadyError`).** Rejected because using exceptions for routine startup latency forces defensive `try...except` control flow on all downstream callers.
* **Strategy B: Return Nullable Dataclass (`Snapshot | None`).** Clean, non-blocking $O(1)$ returns, but leaves consumers responsible for null checks if startup state is unseeded.
* **Strategy C: Asynchronous Future Gating (`await wait_for_location()`).** Rejected due to async contagion violating the synchronous getter contract and deadlock risk if milestone events never arrive while docked.
* **Strategy D: Startup Back-Replay Hydration.** Fast backward seek in the active journal file at initialization to restore the last emitted milestone before serving queries.
* **Selected Cold-Start Resolution: Hybrid Strategy D + Strategy B.** Execute Strategy D (backward journal scan) during facade initialization to pre-seed state from the preceding `Location` or `FSDJump`. Supplement with Strategy B (`LocationSnapshot | None`) to provide strict type safety for rare edge cases (e.g., empty directory or brand-new commander profile).

## Decision Outcome

Chosen option: **Option 3: Ambient Telemetry Facade grounded in ADR 0003 Archetypes** with **Hybrid Strategy D + B Cold-Start Hydration**.

### Architectural Design

```
+--------------------------------------------------------------------------+
|                       Inbound Telemetry Channels                         |
|      (Status 1 Hz Ticks, Journal Events, Out-of-band JSON Payloads)      |
+--------------------------------------------------------------------------+
                                     |
                                     | (Startup: Back-Replay Hydration)
                                     v
+--------------------------------------------------------------------------+
|                       Ingress Dispatch Pipeline                          |
+--------------------------------------------------------------------------+
         |                        |                     |
         v                        v                     v
+------------------+    +-------------------+    +--------------------+
| Bitfield Edge    |    | Epoch Milestone   |    | Context Mutator    |
| Detector         |    | Aggregator        |    | Differ             |
| (ADR 0003)       |    | (ADR 0003)        |    | (ADR 0003)         |
+------------------+    +-------------------+    +--------------------+
         \                        |                     /
          +-----------------------+--------------------+
                                  |
                                  v
+--------------------------------------------------------------------------+
|                  Ambient Commander State Surface                         |
|                                                                          |
|  - location: LocationSnapshot | None (system, coords, body, station)      |
|  - vessel: VesselSnapshot | None (ship_type, ship_id, ship_name)         |
|  - on_foot: bool (derived via edge triggers & suit state)               |
|  - flight_mode: FlightMode (NORMAL_SPACE, SUPERCRUISE, DOCKED, etc.)     |
|  - fuel: QuantizedFuelState(level_band, main_mass, res_mass)             |
+--------------------------------------------------------------------------+
                                  |
                                  v
+--------------------------------------------------------------------------+
|                 Ambient Telemetry Facade (Synchronous Getters)           |
|                                                                          |
|  - get_location() -> LocationSnapshot | None                             |
|  - get_vessel() -> VesselSnapshot | None                                 |
|  - is_on_foot() -> bool                                                  |
|  - get_flight_mode() -> FlightMode                                       |
|  - get_fuel_state() -> QuantizedFuelState                                |
+--------------------------------------------------------------------------+
```

### Archetype Mapping to Facade Getters

1. **`get_location() -> LocationSnapshot | None` $\leftarrow$ Epoch Milestone:**
   * Ingests `Location`, `FSDJump`, `CarrierJump`, `Docked`, `Undocked`, `SupercruiseExit`, `Touchdown`.
   * On startup, scans backward from the active journal head to the most recent milestone event to achieve instant hydration.
   * Idempotently overwrites system coordinates (`StarPos`), system address (`SystemAddress`), star system name, station name, and body name without requiring prior travel history.
   * Returns `None` only if no milestone has ever been logged in the active journal stream.

2. **`get_vessel() -> VesselSnapshot | None` $\leftarrow$ Context Mutator & Milestone:**
   * Ingests `Loadout`, `ShipyardSwap`, `ShipyardBuy`, `SetUserShipName`.
   * Pre-hydrated on startup via journal backward scan for the latest `Loadout` event.
   * Tracks active vessel ID, ship type, custom name, and callsign. Resets smoothly upon ship destruction (`Resurrect`) or SRV boarding.
   * Returns `None` if unseeded prior to initial loadout observation.

3. **`is_on_foot() -> bool` $\leftarrow$ State-Edge Transition:**
   * Evaluated dynamically against `Status.json` bitfields:
     - `Flags2 & HAS_LAT_LONG_SRV_OR_FOOT` combined with absence of `Flags & IN_MAIN_SHIP` and `Flags & IN_SRV`.
     - Cross-correlated with discrete `Disembark`, `Embark`, and `SuitLoadout` journal events.
   * Immediate toggle upon rising/falling edge without waiting for journal latency.

4. **`get_flight_mode() -> FlightMode` $\leftarrow$ Milestone & Edge Hybrid:**
   * Transitioned by `SupercruiseEntry`, `SupercruiseExit`, `Docked`, `Undocked`, `Touchdown`, `Liftoff` or status bitmask (`SUPERCRUISE`, `LANDED`, `DOCKED`).

5. **`get_fuel_state() -> QuantizedFuelState` $\leftarrow$ Metric Quantizer:**
   * Categorizes scalar `Fuel.FuelMain` and `Fuel.FuelReservoir` into hysteresis bands (`CRITICAL`, `LOW`, `NOMINAL`) to alert downstream systems only when threshold boundaries are breached.

## Consequences

### Positive
* Single source of truth for commander context across the entire integration harness.
* Downstream components make simple, non-blocking synchronous method calls without complex event-parsing or exception-catching overhead.
* Startup back-replay hydration guarantees valid location and vessel state from the very first tick during mid-session restarts.
* Strict `Snapshot | None` typing makes unseeded edge cases explicit and safe.
* Decoupled from Frontier client event emission timing.
* Validates API contracts in integration before freezing the design into an upstream package.

### Negative / Trade-offs
* Startup back-replay incurs a bounded, one-time filesystem read across the active journal file during initialization.
* Callers consuming `get_location()` or `get_vessel()` must support null checks (`if location is not None`) when handling unseeded scenarios.
