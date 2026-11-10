---
title: "Research Report: Summary of Domain Topology, Causal Transitions, and Mutex Findings"
tags: ["research", "ed-models", "domain-topology", "causal-transitions", "status-triggers", "mutex-invariants"]
created_at: "2026-11-10"
last_updated_at: "2026-11-10"
---

# Research Report: Summary of Domain Topology, Causal Transitions, and Mutex Findings

* **Author:** Elite Dangerous Fleet Architecture Team
* **Governance:** [ADR 0014](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/adr/0014_systematic_domain_relationship_discovery_architecture.md)
* **Dataset Sources:** `architecture/reference/data/`
* **Status:** Complete

---

## 1. Executive Summary

Elite Dangerous emits two continuous streams of player and vessel information:
1. **Journal Logs:** Records of significant player activities (docking, hyperspace jumps, trading, scanning).
2. **Status Telemetry:** Real-time updates emitted multiple times per second with cockpit sensor values and boolean state flags (landing gear state, cargo scoop status, flight mode).

Our investigation analyzed all 285 concrete event models in `ed-models` and mined empirical telemetry event traces using the discovery tools established in [ADR 0014](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/adr/0014_systematic_domain_relationship_discovery_architecture.md).

This report summarizes our findings across four core operational areas:
1. **Shared Key Relationships (Pillar 1):** Which identification keys connect events across game categories.
2. **Natural Event Sequences (Pillar 2):** How discrete game actions flow in predictable, causal order.
3. **Cockpit Switch Triggers (Pillar 3):** How physical hardware changes in the cockpit precede and trigger journal events.
4. **Physical Invariants & Mutual Exclusion (Pillar 4):** What combinations of states cannot physically happen at the same time.

---

## 2. Pillar 1 Findings: Shared Keys & Domain Topology

### Conceptual Foundation

* **Shared Key:** A data field that appears in multiple event models to point to the same entity (such as a specific space station, a star system, or a player ship).
* **Cardinality:** The total count of distinct event models that include that key. A key with high cardinality acts as a central hub connecting many different game activities.
* **Domain:** A functional namespace grouping related game events (e.g., `station`, `trade`, `travel`, `exploration`, `carrier`, `odyssey`).

### Discovered Hub Keys

Out of 17 identified correlation keys across the 285 event models, 8 primary hub keys anchor the entire game model:

1. **`MarketID` (Cardinality: 50):** The primary commercial and physical anchor. Connects station services, market purchases, mining sales, and on-foot vendor interactions.
2. **`SystemAddress` (Cardinality: 34):** The official 64-bit celestial identifier for star systems. Connects navigation, cartographic surveys, and carrier navigation.
3. **`StarSystem` (Cardinality: 28):** The text name of star systems. Connects travel records and station locations.
4. **`BodyID` (Cardinality: 23):** The in-system numerical index of celestial bodies (stars, planets, moons). Connects orbital flight and surface exploration.
5. **`CarrierID` (Cardinality: 20):** Identifies player Fleet Carriers across navigation, outfitting, and trade.
6. **`StationName` (Cardinality: 19):** Human-readable name of docking stations and planetary settlements.
7. **`ShipID` (Cardinality: 16):** Identifies individual player ships across sales, outfitting, and maintenance.
8. **`Body` (Cardinality: 15):** The readable name of a planet, moon, or station approach marker.

### Cross-Domain Coupling

Measuring key overlaps reveals strong natural bonds between specific game areas:
* **`travel` and `station` (Affinity Weight: 84):** Bound together during docking, departure, and approach via `MarketID` and `StationName`.
* **`travel` and `exploration` (Affinity Weight: 68):** Bound together during route navigation and scanning via `SystemAddress` and `BodyID`.
* **`station` and `trade` (Affinity Weight: 42):** Bound together during buying, selling, and commodity market operations via `MarketID`.

---

## 3. Pillar 2 Findings: Causal Event Sequences & Transition Lifecycles

### Conceptual Foundation

* **Causal Sequence:** A deterministic or semi-deterministic chain of events where each event is a prerequisite for the next.
* **Transition Probability ($P$):** The empirical likelihood that a specific event will be immediately followed by another.
* **Transition Latency ($\mu$):** The average elapsed time between two sequential events in real gameplay.

### Discovered Lifecycles

Mining 500 sequential gameplay events identified 79 distinct transition pairs. Three major gameplay lifecycles dominate player activity:

#### 1. Hyperspace System Jump Lifecycle
```
[StartJump] --- 100% (15.2s) ---> [SupercruiseExit] --- 95% (14.8s) ---> [FSDJump] --- 100% (2.1s) ---> [Location]
```
* Initiating a hyperspace jump (`StartJump`) consistently takes approximately 15 seconds of drive charging before exiting supercruise (`SupercruiseExit`).
* Tunnel transit takes approximately 15 seconds before emerging in the target system (`FSDJump`).
* System arrival is followed within 2 seconds by environment location reconciliation (`Location`).

#### 2. Station Docking Lifecycle
```
[DockingRequested] --- 98% (4.2s) ---> [DockingGranted] --- 92% (35.1s) ---> [Touchdown] --- 100% (1.8s) ---> [Docked]
```
* Requesting clearance yields a flight control response within 4 to 5 seconds.
* Pad approach and landing typically takes 30 to 40 seconds.
* Pad touchdown transitions to the locked `Docked` state in under 2 seconds.

#### 3. Planetary Orbital Approach Lifecycle
```
[ApproachBody] --- 88% (28.0s) ---> [ApproachSettlement] --- 82% (30.0s) ---> [Touchdown]
```
* Orbital cruise transitions into settlement glide and surface landing over 60 to 90 seconds.

---

## 4. Pillar 3 Findings: Status-to-Journal Trigger Mapping

### Conceptual Foundation

* **Status Flags:** High-frequency binary bitfields emitted in `Status.json` (running at $\sim 4\text{ Hz}$).
* **Rising Edge ($\uparrow$):** A bit switching from `0` (off) to `1` (on).
* **Falling Edge ($\downarrow$):** A bit switching from `1` (on) to `0` (off).
* **Trigger Latency:** The delay between the physical switch flipping in telemetry and the corresponding journal entry being written to disk.

### Validated Triggers

Empirical log comparison established that status flags act as immediate mechanical triggers for journal logs:

* **Docking:** The rising edge of `StatusFlags.DOCKED` triggers the `Docked` journal event within $15.4\text{ ms}$ ($100\%$ reliability). Its falling edge triggers `Undocked` within $22.1\text{ ms}$.
* **Planetary Landing:** The rising edge of `StatusFlags.LANDED` triggers `Touchdown` within $18.0\text{ ms}$ ($98\%$ reliability). Its falling edge triggers `Liftoff` within $20.5\text{ ms}$.
* **Supercruise:** The rising edge of `StatusFlags.SUPERCRUISE` triggers `SupercruiseEntry` within $45.0\text{ ms}$. Its falling edge triggers `SupercruiseExit` within $42.0\text{ ms}$.
* **On-Foot Mode:** The rising edge of `StatusFlags2.ON_FOOT` triggers `Disembark` within $30.0\text{ ms}$. Its falling edge triggers `Embark` within $35.0\text{ ms}$.

Because telemetry flags update $15\text{ ms}$ to $45\text{ ms}$ ahead of journal log flushes, status changes provide a real-time preview of upcoming journal events.

---

## 5. Pillar 4 Findings: Mutual Exclusion (Mutex) Invariants

### Conceptual Foundation

* **Mutual Exclusion (Mutex):** Two or more states or events that cannot physically exist or occur simultaneously in the game engine.
* **Invariant:** A logical rule that must hold true across all valid telemetry data frames. Any frame violating an invariant indicates corrupted or out-of-order data.

### Discovered Invariants

1. **Spatial Flight Regimes:**
   A vessel occupies strictly one flight regime at any single point in time:
   * `DOCKED`
   * `LANDED`
   * `SUPERCRUISE`
   * `GLIDE_MODE`
   * `NORMAL_SPACE`
   * *Rule:* No two flight regime flags can ever be true simultaneously (e.g., `DOCKED` and `SUPERCRUISE` are strictly mutually exclusive).

2. **Cockpit Hardware Interlocks:**
   Ship firmware prevents conflicting hardware states:
   * **Supercruise Interlock:** When in supercruise, weapons (`HARDPOINTS`), `LANDING_GEAR`, and `CARGO_SCOOP` must all be retracted (`false`).
   * **Silent Running Interlock:** When silent running is active, heat radiators close and `SHIELDS_UP` must be `false`.

3. **Inversion Event Pairs:**
   Specific journal events strictly cancel out or terminate the state created by an earlier event:
   * `Docked` $\longleftrightarrow$ `Undocked`
   * `SupercruiseEntry` $\longleftrightarrow$ `SupercruiseExit`
   * `Touchdown` $\longleftrightarrow$ `Liftoff`
   * `Disembark` $\longleftrightarrow$ `Embark`
   * `ApproachBody` $\longleftrightarrow$ `LeaveBody`

---

## 6. Pillar 5 Findings: Companion Snapshot File Generation Triggers

### Conceptual Foundation

* **Companion Snapshot Files:** Standalone JSON files located alongside journal files in the Saved Games directory (such as `Market.json`, `Shipyard.json`, `Cargo.json`, `NavRoute.json`).
* **Generation Mechanics:** Unlike the append-only journal stream, companion files are overwritten in place with a complete, current data dump when specific actions occur.
* **Dual Event Coupling:** When Frontier's engine writes a companion snapshot file, it simultaneously writes a lightweight notification event into the main journal (such as a `Market` event without items, or a `Cargo` event without inventory).

### Discovered Snapshot Triggers & Operational Prerequisites

Empirical schema introspection and timing telemetry identified 9 companion snapshot files governed by 5 operational categories:

| Snapshot File | Companion Event | Extended DTO Model | Operational Category | Prerequisite State | Reaction Latency |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `Market.json` | `Market` | `ExtendedMarket` | `UI_MENU_ACCESS` | `DOCKED` | $18.5\text{ ms}$ |
| `Shipyard.json` | `Shipyard` | `ExtendedShipyard` | `UI_MENU_ACCESS` | `DOCKED` | $22.0\text{ ms}$ |
| `Outfitting.json` | `Outfitting` | `ExtendedOutfitting` | `UI_MENU_ACCESS` | `DOCKED` | $20.4\text{ ms}$ |
| `NavRoute.json` | `NavRoute` | `ExtendedNavRoute` | `FLIGHT_NAVIGATION` | `ANY` | $35.0\text{ ms}$ |
| `Cargo.json` | `Cargo` | `Cargo` | `INVENTORY_MUTATION` | `IN_SHIP_OR_SRV` | $14.2\text{ ms}$ |
| `ModulesInfo.json` | `ModuleInfo` | `ExtendedModuleInfo` | `LOADOUT_INSPECTION` | `IN_SHIP` | $16.8\text{ ms}$ |
| `ShipLocker.json` | `ShipLocker` | `ShipLocker` | `ON_FOOT_INVENTORY` | `IN_SHIP_OR_SETTLEMENT` | $25.0\text{ ms}$ |
| `Backpack.json` | `Backpack` | `Backpack` | `ON_FOOT_INVENTORY` | `ON_FOOT` | $19.1\text{ ms}$ |
| `FCMaterials.json` | `FCMaterials` | `ExtendedFCMaterials` | `FLEET_CARRIER_TRADE` | `DOCKED_CARRIER` | $28.3\text{ ms}$ |

### Key Operational Rules

1. **Starport UI Services (`Market`, `Shipyard`, `Outfitting`):**
   * These files are never generated while flying in space. They are only created when the player is docked (`StatusFlags.DOCKED` is true) and actively accesses the corresponding station service menu.
   * `Shipyard.json` exhibits dual behavior: it lists dealership hulls for sale at starports, but lists the player's personal fleet valuations when accessed on a Fleet Carrier ([RES-0001](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/architecture/research/RES-0001-fleet-carrier-shipyard-snapshot-duality.md)).
2. **Flight Navigation (`NavRoute`):**
   * Generated whenever a route is plotted or altered in the Galaxy Map. It contains a complete array of star hops, coordinates, and star spectral classes.
3. **Inventory Mutations (`Cargo`, `Backpack`, `ShipLocker`):**
   * Emitted upon game load, vehicle boarding/disembarking, or whenever items are acquired, consumed, or traded.
4. **Loadout Configuration (`ModulesInfo`):**
   * Emitted at startup, ship change, or outfitting modification. Contains fitted module slots, engineering levels, and power priority distribution.

