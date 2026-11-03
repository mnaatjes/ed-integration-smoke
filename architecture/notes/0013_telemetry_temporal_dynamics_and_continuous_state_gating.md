---
title: "Note 0013: Telemetry Temporal Dynamics and Continuous State Gating Patterns"
tags: ["notes", "telemetry", "state-machine", "bitmasks", "status-json", "ed-models"]
created_at: "2026-11-03"
last_updated_at: "2026-11-03"
---

# Note 0013: Telemetry Temporal Dynamics and Continuous State Gating Patterns

## 1. Diagnostic: Continuous State vs. Discrete Event Semantics

During live gameplay ingestion sessions in `ed-integration-smoke`, audit coverage metrics revealed an extreme numerical divergence between target hit counters:

* **Point-in-time Journal Events:** Low, discrete hit counts reflecting real physical player decisions (`Undocked`: 3, `Docked`: 3, `FSDJump`: 21, `CarrierFinance`: 5).
* **Telemetry Status Bitflags:** Massive, highly divergent counts spanning four orders of magnitude (`IN_MAIN_SHIP`: 19,409, `SHIELDS_UP`: 19,310, `FSD_MASS_LOCKED`: 5,502, `SCOOPING_FUEL`: 1,379, `NIGHT_VISION`: 8).

This discrepancy stems from a fundamental semantic mismatch in the telemetry ingestion layer:
1. **Discrete Events (`Journal.*.log`):** Emitted strictly upon discrete, point-in-time occurrences (e.g. ship clamps disengaged, jump tunnel entered).
2. **Continuous States (`Status.json`):** Emitted at 1 Hz as packed bitfields describing ongoing flight and spatial conditions.
3. **The Anti-Pattern:** Treating each 1 Hz polling tick as an independent "event occurrence" converts duration into frequency ($1\text{ hit} \approx 1\text{ second of active state}$). This results in notification spam, obscured causal sequences, and misleading hit counters where 8 seconds of Night Vision appears dwarfed by 5.4 hours of sitting in a ship cockpit.

---

## 2. Theory: Level-Triggered Signals vs. Edge-Triggered Transitions

In digital telemetry and distributed control architectures, real-time binary indicators are bifurcated into two signal domains:

```
Level Signal:   ───┐                               ┌──────────────
(Status.json)      │                               │
                   └───────────────────────────────┘
                     State Active (Levels = 1 Hz ticks)

Edge Signal:       ▲                               ▼
(Transitions)    Rising Edge                     Falling Edge
                 (0 -> 1: Engage)                (1 -> 0: Disengage)
```

1. **Level-Triggered Signals (Continuous Conditions):**
   * Describe ongoing operational states (`SHIELDS_UP`, `FSD_MASS_LOCKED`, `SUPERCRUISE`, `DOCKED`).
   * Polling them at 1 Hz reports whether the condition *remains true*, not that an action took place.
2. **Edge-Triggered Signals (State Transitions):**
   * Describe the boundary moment when the system transitions between states.
   * **Rising Edge ($0 \to 1$):** `Entered Mass Lock`, `Gear Deployed`, `Night Vision Engaged`.
   * **Falling Edge ($1 \to 0$):** `Mass Lock Cleared`, `Gear Stowed`, `Night Vision Disengaged`.
3. **Causal Ordering:**
   * Flight states follow strict physical sequences:
     $$\text{Docked} \longrightarrow \text{Liftoff/Undock} \longrightarrow \text{Clear Pad Mass Lock} \longrightarrow \text{Supercruise Charge} \longrightarrow \text{Supercruise}$$
   * Level polling blindly reports all active flags simultaneously without preserving the transition boundaries that define in-game accomplishments.

---

## 3. Analysis: Four Architectural Gating & Representation Patterns

To present chronological and temporal changes without inundating operators with thousands of redundant notices, four patterns are established:

### Pattern 1: Edge-Triggered Transition Detection (Rising & Falling Edges)
Instead of incrementing hit counters or surfacing notifications on every 1 Hz polling tick where a bit is high, the ingestion pipeline maintains prior state signatures (`_prior_flags: int`) and fires events strictly on transitions:
* **Rising Edge ($0 \to 1$):** Emits a single notification: `Mass Lock Engaged`, `Gear Down`, `Silent Running Active`.
* **Falling Edge ($1 \to 0$):** Emits completion: `Mass Lock Cleared`, `Gear Up`, `Radiators Opened`.
* **Behavior:** The operator receives exactly one alert upon entering mass lock and one alert upon clearing it, whether the interval spans 5 seconds or 2 hours.

### Pattern 2: Dual-Metric Schema Separation (Occurrences vs. Durations)
In reporting, databases, and TUI dashboards, metrics are explicitly partitioned into two orthogonal dimensions:
* **Discrete Events (`TargetType.EVENT`):** Measured in **Occurrences** (`hit_count: int`, e.g., 3 Dockings, 21 Hyperspace Jumps).
* **Continuous States (`TargetType.STATUS_FLAG`):** Measured in **Activations** (`transition_count: int`) and **Cumulative Duration** (`active_duration_seconds: float`, formatted as `05h:23m:10s` in Ship, `03h:07m` in Supercruise, `00h:00m:08s` in Night Vision).

### Pattern 3: State-Span Session Recording (Interval / Span Engine)
Continuous status telemetry is persisted not as individual discrete tick rows, but as temporal intervals:
```sql
CREATE TABLE state_spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_id TEXT NOT NULL,              -- e.g. 'FSD_MASS_LOCKED', 'SUPERCRUISE'
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_seconds REAL
);
CREATE INDEX idx_state_spans_active ON state_spans(state_id) WHERE ended_at IS NULL;
```
* On rising edge ($0 \to 1$): Insert active span with `started_at = now()`.
* On falling edge ($1 \to 0$): Update `ended_at = now()` and compute `duration_seconds`.
* **Benefit:** Replaces 5,502 raw rows with a single compact span record preserving exact chronological history.

### Pattern 4: Hierarchical Finite State Machine (HFSM) / Flight Regimes
Flags are contextualized by assigning them to flight regimes:
* **`DOCKED` Regime:** Clamps locked. Mass lock, gear down, and main ship flags are structural invariants; edge alerts for these are suppressed.
* **`SUPERCRUISE` Regime:** Gear and mass lock are invalid; alerts focus on throttle, FSD interdiction edges, and orbital drop boundaries.
* **`PLANETARY_FLIGHT` Regime:** Focuses on glide mode transitions, sub-orbital descent, touchdown, and on-foot disembarkation.
* **Benefit:** Eliminates illogical notifications (e.g. alerting that a ship is mass-locked while docked on a carrier pad).

---

## 4. Remediation: Recommended Implementation Roadmap

1. **Phase 1: Edge Detection in `TelemetryPipeline` (`src/ed_integration_smoke/daemon/pipeline.py`):**
   * Maintain `_last_status_flags: int` and `_last_status_flags2: int`.
   * Compute rising edge mask: `rising = current_flags & ~prior_flags`.
   * Surface dashboard notifications and trigger achievements strictly when `rising & flag.value != 0`.
2. **Phase 2: Database Schema Expansion (`src/ed_integration_smoke/daemon/storage.py`):**
   * Enhance `target_coverage` table with `transition_count INTEGER NOT NULL DEFAULT 0` and `duration_seconds REAL NOT NULL DEFAULT 0.0`.
   * Implement `state_spans` table for tracking ongoing flight intervals.
3. **Phase 3: Dashboard & Report Separation (`scripts/run_telemetry_dashboard.py` & Coverage Report):**
   * Present continuous flight indicators as steady-state annunciator lamps (green/yellow/red).
   * Present the live notification feed strictly on state transitions and discrete journal events.
   * Format coverage reports displaying discrete occurrences for events and total formatted active durations (`HH:MM:SS`) for status bitflags.
