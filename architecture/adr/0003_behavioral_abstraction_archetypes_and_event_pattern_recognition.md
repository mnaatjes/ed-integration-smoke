---
title: "ADR 0003: Behavioral Abstraction Archetypes and Telemetry Pattern Recognition"
tags: ["adr", "telemetry", "architecture", "patterns", "state-machine", "event-driven", "ed-models"]
created_at: "2026-11-03"
last_updated_at: "2026-11-03"
---

# ADR 0003: Behavioral Abstraction Archetypes and Telemetry Pattern Recognition

* Status: Accepted
* Date: 2026-11-03

## Context and Problem Statement

Frontier client telemetry consists of two fundamentally distinct data channels:
1. High-frequency continuous status samples (`Status.json`) polled at 1 Hz, generating thousands of redundant ticks for static states (`LANDING_GEAR_DOWN`, `SHIELDS_UP`, `FSD_MASS_LOCKED`).
2. Low-frequency discrete journal events (`Journal.*.log`) emitted upon player actions (`Docked`, `FSDJump`, `Undocked`).

Historically, telemetry consumers attempt to track game state by reconstructing rigid sequential state machines (e.g., verifying `DockingRequested` -> `DockingGranted` -> `Docked` -> `Undocked`). This approach fails in production:
* Frontier game updates introduce subtle ordering mutations or omit intermediate events.
* Network jitter and replay buffer processing reorder discrete messages.
* Session restarts inject historical events out of current sequence.
* Downstream UI and alert components are overwhelmed by continuous 1 Hz status repetitions unless explicit deduplication or transitions are derived.

We need a standardized behavioral abstraction architecture that eliminates fragile sequential graphs and maps arbitrary telemetry events into decoupled behavioral archetypes.

## Decision Drivers

* **Zero Sequential Coupling:** State consumers must not require strict linear event ordering to recognize operational conditions.
* **Notification Deduping (Noise Reduction):** Downstream UI and audial annunciators must only receive notifications upon state *transitions* (edges), not steady-state polling levels.
* **Idempotency & Replay Resilience:** Replaying historical logs must yield deterministic final state without triggering artificial alert storms.
* **Computational Efficiency:** Evaluation of high-frequency status flags must execute in sub-microsecond bitwise operations.

## Considered Options

1. **Option 1: Explicit Finite State Machines (FSMs).** Model complete game lifecycle graphs with transition matrices. Rejected due to extreme fragility when Frontier client behavior varies, events are dropped, or client restarts replay out-of-order logs.
2. **Option 2: Raw Change Filters (Previous != Current).** Filter identical subsequent payloads. Rejected because it does not classify *nature* of change (e.g., scalar drift vs. binary toggle vs. structural mutation).
3. **Option 3: Behavioral Abstraction Archetypes (Selected).** Classify inbound events and status ticks into four decoupled mathematical archetypes:
   - **Edge Transitions:** Binary bitfield delta gating ($\Delta 0 \to 1, 1 \to 0$).
   - **Monotonic & Quantized Gauges:** Scalar levels with rate derivation and hysteresis thresholding.
   - **Epoch Milestones:** Idempotent point-in-time state updates without sequential preconditions.
   - **Context Mutators:** Set differentials ($A \Delta B$) for cargo, modules, and loadouts.

## Decision Outcome

Chosen option: **Option 3: Behavioral Abstraction Archetypes**.

### The 4 Behavioral Archetypes

```
+--------------------------------------------------------------------------+
|                        Inbound Telemetry Stream                          |
+--------------------------------------------------------------------------+
            |                          |                       |
            v                          v                       v
   +------------------+       +------------------+    +------------------+
   |  Edge Transition |       | Metric Quantizer |    |  Epoch Milestone |
   |  (Flags, Flags2) |       |  (Fuel, Pips)    |    | (Docked, Jump)   |
   +------------------+       +------------------+    +------------------+
            |                          |                       |
   - Rising: 0 -> 1           - Value drift           - Idempotent stamp
   - Falling: 1 -> 0          - Hysteresis band       - Context frame
   - Masked filter            - Rate (d/dt)           - No order prereq
            \                          |                      /
             +-------------------------+---------------------+
                                       |
                                       v
                     +-----------------------------------+
                     | Consolidated Semantic Surface     |
                     +-----------------------------------+
```

### 1. Edge-Triggered State Transitions
For bitfield flags (`Flags`, `Flags2`), evaluation is purely bitwise against the preceding tick:
$$\text{Rising} = \text{Current} \land \neg \text{Previous}$$
$$\text{Falling} = \neg \text{Current} \land \text{Previous}$$
Consumers subscribe strictly to rising or falling edges. Static levels are suppressed from generating alerts.

### 2. Quantized Metric Gauges
Scalar metrics (fuel, pips, cargo tons, shield percentage) drift continuously. The abstraction engine applies:
* **Hysteresis Bands:** Notifications trigger only when crossing defined boundaries (e.g., Fuel `< 10%`, `< 25%`).
* **First Derivative ($\frac{d}{dt}$):** Rate-of-change metrics identify sudden drops (jumps, structural damage) versus steady depletion.

### 3. Epoch Milestones
Discrete journal actions (`Docked`, `FSDJump`, `CarrierJump`, `Undocked`) apply directly to an ambient `PlayerEnvironmentContext`. A `Docked` event sets `context.docked_at = station_name` and `context.flight_mode = FlightMode.DOCKED` regardless of whether preceding docking events were observed.

### 4. Context Mutators
Inventory and equipment modifications (`Loadout`, `Cargo`, `Materials`) are modeled as set operations. Inbound payloads are compared against the active inventory set to yield added/removed item deltas.

## Consequences

### Positive
* Eliminates conversational and UI notification flooding from high-frequency 1 Hz status polling.
* Robust against dropped events, network disconnects, and log replays.
* Pure, stateless or single-tick-memory algorithms guarantee extreme throughput.
* Clean integration with existing `ed-models` domain dataclasses.

### Negative / Trade-offs
* Requires downstream components to read current state from an aggregated context object rather than listening to single events in isolation.
* Rate derivation requires retaining a tiny sliding time-series window (e.g., 5 seconds) for scalar values.
