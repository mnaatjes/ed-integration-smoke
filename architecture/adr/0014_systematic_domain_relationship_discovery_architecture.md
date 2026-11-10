---
title: "ADR 0014: Systematic Discovery, Correlation, and Trigger Mapping Architecture"
tags: ["adr", "domain-mapping", "schema-correlation", "causal-dag", "finite-state-machine", "telemetry-triggers"]
created_at: "2026-11-10"
last_updated_at: "2026-11-10"
---

# ADR 0014: Systematic Discovery, Correlation, and Trigger Mapping Architecture

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-10

---

## 1. Context and Problem Statement

The `ed-models` package models 295 typed journal events across 12 distinct game domains, complemented by continuous 64-bit status bitfields (`Status.json`). While individual data contracts are strongly typed, the global system lacks a formal, verifiable map of:

1. **Static Domain Relationships:** Which domain models correlate through shared foreign keys (e.g. `SystemAddress`, `MarketID`, `BodyID`, `ShipID`), forming relational entity boundaries.
2. **Causal Event Sequences:** What temporal, sequential, and causal patterns govern event emissions during real gameplay (e.g. the deterministic lifecycle from `StartJump` to `SupercruiseExit`, `FSDJump`, and `Location`).
3. **State-Flag Differential Triggers:** How continuous cockpit bitmask state transitions (`StatusFlags`, `StatusFlags2`) correlate with, precede, or trigger discrete Journal events (e.g. `DOCK_STATUS` rising edge $\Longleftrightarrow$ `Docked`).

Without systematic discovery tooling, architectural development relies on heuristic developer assumptions. We require an automated, deterministic discovery and mapping architecture.

---

## 2. Decision Drivers

* **Determinism & Reproducibility:** Discovery methodologies must rely on programmatic introspection of Python AST/dataclass signatures and empirical event logs rather than manual documentation review.
* **Tripartite Discovery Framework:** Cover structural static schema correlation, sequential dynamic workflow discovery, and cross-plane status-to-journal trigger mapping.
* **Exportable Graph Artifacts:** Outputs must be machine-readable (JSON adjacency matrices, Graphviz `.dot`, Mermaid graphs) for ingestion into documentation, IDE tooling, and validation engines.
* **Non-Invasive Introspection:** Tooling must operate offline against `ed-models` source code or online against historical telemetry archives (`ed-telemetry` REST endpoints).

---

## 3. Considered Options

* **Option 1: Manual Community Wiki Scraping.** Rely on third-party community documentation (EDCD / Frontier Journal Manual). Rejected due to schema drift, unversioned changes, and lack of programmatic verification.
* **Option 2: Runtime Logging Assertions Only.** Add arbitrary print statements inside the client facade during gameplay. Rejected because it provides no global architectural topology and fails to systematically discover edge-case relationships.
* **Option 3: Tripartite Deterministic Discovery Framework (Approved).** A dedicated suite of automated analysis tools covering Static Schema Key Correlation, Causal Sequence Induction, and State-Flag Differential Triggering.

---

## 4. Decision Outcome

Chosen Option: **Option 3: Tripartite Deterministic Discovery Framework**.

The architecture establishes three specialized discovery engines:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Tripartite Discovery Engine                       │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Static Schema Key           │ Programmatically traverses ed-models  │
│    Correlation Engine          │ dataclasses to build entity graphs    │
│    (Entity Relational Graph)   │ linked by shared primary/foreign keys.│
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. Causal Sequence Induction   │ Mines historical journal logs to build│
│    Engine                      │ empirical transition matrices and     │
│    (Markov & Prefix DAG)       │ causal precedence workflows.          │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. State-Flag Differential     │ Correlates microsecond status bitmask │
│    Trigger Mapping Engine      │ edge transitions (rising/falling) with│
│    (Status-to-Journal Triggers)│ discrete lifecycle journal emissions. │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 5. Architectural Specification & Methodologies

### 5.1 Pillar 1: Static Schema Key Correlation (Entity Relational Graph)

* **Objective:** Extract an interconnected entity-relationship graph connecting all 295 `ed-models` events.
* **Mechanism:**
  1. Inspect dataclass field annotations across `ed_models.core.domain.events.*`.
  2. Identify canonical foreign key archetypes:
     * **Spatial:** `SystemAddress` (int64), `StarSystem` (str), `BodyID` (int), `Body` (str), `StarPos` (vec3).
     * **Commercial & Asset:** `MarketID` (int64), `ShipID` (int), `CarrierID` (str/int), `StationName` (str).
     * **Identity & Societal:** `Commander` (`FID`), `Faction` (str), `SquadronID` (int), `Power` (str).
  3. Form an undirected bipartite graph $G = (V_E \cup V_K, E)$ where $V_E$ are event classes and $V_K$ are canonical keys.
  4. Project into a one-mode event-to-event graph $G_E = (V_E, E_E)$ where edge weights $w(e_1, e_2)$ equal the count of shared keys.
* **Tooling Implementation:** `scripts/map_domain_schema.py`
  * Emits `architecture/reference/domain_entity_graph.json` and Mermaid visualization diagrams.

### 5.2 Pillar 2: Causal Sequence Induction (Markov & Prefix DAG)

* **Objective:** Discover empirical flight lifecycles and causal event precedence chains from real gameplay logs.
* **Mechanism:**
  1. Ingest chronological event streams $[e_1, e_2, \dots, e_N]$ from `ed-telemetry` `/api/v1/events` or local journal files.
  2. Compute 1st-order Markov Transition Probabilities:
     $$P(e_j \mid e_i) = \frac{C(e_i \to e_j)}{\sum_k C(e_i \to e_k)}$$
  3. Filter noise by enforcing significance thresholds ($P > 0.15$, $C > 5$).
  4. Construct Directed Acyclic Graphs (DAGs) representing core game workflows:
     * **Hyperspace Jump:** `StartJump` $\to$ `SupercruiseExit` $\to$ `FSDJump` $\to$ `Location`.
     * **Orbital Descent:** `SupercruiseExit` $\to$ `ApproachBody` $\to$ `ApproachSettlement` $\to$ `Touchdown`.
     * **Station Docking:** `DockingRequested` $\to$ `DockingGranted` $\to$ `Touchdown` $\to$ `Docked`.
* **Tooling Implementation:** `scripts/mine_event_sequences.py`
  * Emits transition adjacency matrices and workflow sequence diagrams.

### 5.3 Pillar 3: State-Flag Differential Triggering (Status-to-Journal Trigger Map)

* **Objective:** Map high-frequency hardware telemetry flag edge transitions to discrete Journal event emissions.
* **Mechanism:**
  1. Continuously evaluate status bitfields $F_t = (\text{Flags}_t, \text{Flags2}_t)$ against $F_{t-1}$.
  2. Identify bitmask differentials:
     $$\Delta F = F_t \oplus F_{t-1}$$
     * **Rising Edge (Activation):** $\Delta F \ \& \ F_t$
     * **Falling Edge (Deactivation):** $\Delta F \ \& \ F_{t-1}$
  3. Associate rising/falling edges occurring within temporal window $\tau \le 500\text{ ms}$ of a Journal event $J_t$.
  4. Build a deterministic Trigger Matrix:
     $$\text{Trigger}(J) = \{ b \in \text{Flags} \mid \text{Edge}(b) \iff J \}$$
* **Deterministic Mappings:**
  * `StatusFlags.DOCKED` (Bit 0) $\uparrow \implies$ `Docked`
  * `StatusFlags.LANDED` (Bit 1) $\uparrow \implies$ `Touchdown`
  * `StatusFlags.SUPERCRUISE` (Bit 4) $\downarrow \implies$ `SupercruiseExit`
  * `StatusFlags2.GLIDE_MODE` (Bit 12) $\downarrow \implies$ Surface flight transition
* **Tooling Implementation:** `scripts/map_trigger_matrix.py`
  * Emits formal mapping specification linking bitwise flags to event handlers.

---

## 6. Implementation Roadmap

1. **Step 1:** Implement `scripts/map_domain_schema.py` to introspect `ed-models` dataclasses and generate the canonical entity-relationship topology.
2. **Step 2:** Implement `scripts/mine_event_sequences.py` to stream historical telemetry and build empirical Markov transition DAGs.
3. **Step 3:** Implement `scripts/map_trigger_matrix.py` to verify status flag bitmask edges against journal emissions.
4. **Step 4:** Integrate the discovered trigger rules into `ed_services` to power predictive event synthesizers.

---

## 7. Consequences

### Positive
* Eliminates guesswork regarding event dependencies and preconditions.
* Enables automated synthetic test generation by replaying valid DAG sequence paths.
* Informs predictive caching (e.g. pre-fetching system market data upon `StartJump` or `FSDTarget`).

### Negative / Trade-offs
* Requires historical log corpora to establish statistically significant sequence probabilities.
* Asynchronous player actions (e.g. opening cargo scoop while jumping) can introduce noisy parallel branches in empirical DAG mining.
