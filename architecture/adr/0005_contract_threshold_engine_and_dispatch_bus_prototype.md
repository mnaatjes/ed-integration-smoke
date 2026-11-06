---
title: "ADR 0005: Contract Threshold Engine and Event Bus Prototype"
tags: ["adr", "telemetry", "architecture", "eddn", "ed-schema", "event-bus", "accumulator", "throttling"]
created_at: "2026-11-03"
last_updated_at: "2026-11-06"
---

# ADR 0005: Contract Threshold Engine and Event Bus Prototype

* Status: Accepted
* Date: 2026-11-03 (Updated 2026-11-06)

## Context and Problem Statement

To replicate Elite Dangerous Market Connector (EDMC) and fleet integration capabilities, the software suite must transmit validated game data to third-party endpoints (EDDN, Inara, Spansh). However, Frontier's client emits data in an unbundled, asynchronous stream:
* A `Market.json` out-of-band dump contains commodity pricing and `StationName`, but lacks system coordinates (`StarPos`) and `SystemAddress`.
* An `Outfitting.json` dump contains available modules and `MarketID`, but lacks the star system name.
* Inbound journal events are emitted across separate log lines seconds or minutes apart.

If payloads are dispatched immediately upon arrival of an isolated event, they fail destination schema validation due to missing required properties. Conversely, if payloads are held indefinitely, data becomes stale.

Furthermore:
1. Target APIs require self-regulation: redundant or rapid duplicate packages (e.g., repeatedly opening station services while docked) must be throttled.
2. The system requires an event bus to observe when thresholds are met, when packages are dispatched, or when payloads fail validation without tightly coupling network transport to ingestion.
3. Optional schema properties (e.g., coordinates, body names, game versions) must be opportunistically collected from the ambient state without blocking dispatch.
4. When `AmbientTelemetryFacade` (ADR 0004) operates in an unseeded cold-start scenario, its getters may return `None`. The accumulator must perform explicit null checks to differentiate between missing data that can be siphoned vs. unhydrated state requiring staging buffers to hold.

## Decision Drivers

* **Schema-Driven Threshold Detection:** Leverage `ed-schema` data models and JSON Schema introspection to detect when all required properties for a target contract are fulfilled.
* **Ambient Context Siphoning with Null Gating:** Missing required and optional properties must be opportunistically hydrated from `AmbientTelemetryFacade` (ADR 0004), safely handling nullable returns (`Snapshot | None`).
* **Self-Regulation and Deduplication:** Implement semantic hashing and cooldown guards to prevent spamming destination endpoints.
* **Decoupled Observability:** Provide a lightweight, typed Pub/Sub event bus allowing audit loggers, UI visualizers, and network dispatchers to monitor the lifecycle of outbound packages.
* **Prototype Sandbox Boundary:** Evaluate the engine within `ed-integration-smoke` before permanent architectural placement across `ed-schema`, `ed-transport`, or an upstream dispatch daemon.

## Considered Options

1. **Option 1: Hardcoded Event-to-API Mappers.** Write dedicated procedural functions per API endpoint (e.g., `send_eddn_commodity()`). Rejected due to extreme rigidity, schema drift vulnerability, and lack of dynamic property fulfillment tracking.
2. **Option 2: Reactive Stream Combinators (RxPy / ReactiveX).** Use heavy reactive functional streams (`zip`, `combineLatest`). Rejected due to unnecessary runtime complexity, steep debugging curve, and poor introspection into partial schema completeness.
3. **Option 3: Contract Threshold Accumulator with Event Bus (Selected).** A schema-introspecting accumulator that buffers incoming events, interrogates the Ambient Telemetry Facade for missing required/optional properties, verifies completion against `ed-schema` models, enforces rate deduplication, and broadcasts lifecycle events across an in-memory event bus.

## Decision Outcome

Chosen option: **Option 3: Contract Threshold Accumulator with Event Bus**.

### Architectural Design

```
                                  +---------------------------------------+
                                  |   Ambient Telemetry Facade (ADR 0004) |
                                  +---------------------------------------+
                                                      |
                                                      | (Opportunistic Context Siphon)
                                                      | [Explicit Null Checks]
                                                      v
+------------------------+        +-----------------------------------------------+
| Ingress Event Stream   | -----> |       Contract Threshold Accumulator          |
| (Market, Outfitting,   |        |                                               |
|  Journal Events)       |        |  1. Introspect Target Contract (ed-schema)   |
+------------------------+        |  2. Check Required Fields Fulfillment         |
                                  |  3. Siphon Context if Snapshot != None        |
                                  |  4. Validate Payload against Target Schema    |
                                  +-----------------------------------------------+
                                                      |
                                                      | (Threshold Satisfied)
                                                      v
                                  +-----------------------------------------------+
                                  |     Deduplication & Rate Guard (Throttler)    |
                                  |                                               |
                                  |  - Compute Semantic Payload Hash              |
                                  |  - Evaluate Cooldown Window                   |
                                  +-----------------------------------------------+
                                                      |
                                                      | (Approved for Dispatch)
                                                      v
                                  +-----------------------------------------------+
                                  |              Asynchronous Event Bus           |
                                  +-----------------------------------------------+
                                        /                   |                  \
                                       /                    |                   \
                                      v                     v                    v
                          +-------------------+   +--------------------+   +-------------------+
                          | Network Transport |   | Telemetry Coverage |   | Real-Time TUI     |
                          | Dispatcher        |   | Audit Ledger       |   | Dashboard         |
                          | (ed-transport)    |   | (storage.py)       |   | (dashboard.py)    |
                          +-------------------+   +--------------------+   +-------------------+
```

### Core Engine Components

#### 1. Schema Introspector & Contract Descriptor
Each API target contract (e.g., `CommodityV3Contract`, `OutfittingV2Contract`, `NavRouteV1Contract`) defines:
* `target_schema_cls`: The governing `ed-schema` Pydantic/dataclass model.
* `trigger_events`: Frontier events that initiate or update package assembly (e.g., `{"Market", "Docked"}`).
* `required_properties`: Property keys strictly required before dispatch is permissible.
* `optional_properties`: Property keys to query opportunistically from `AmbientTelemetryFacade` (e.g., `star_pos`, `system_address`, `body`).

#### 2. Threshold Fulfillment, Context Siphoning & Null Gating
Upon receiving a trigger event:
1. The accumulator stores the event payload in the active contract staging buffer.
2. It evaluates missing required fields.
3. If missing fields can be satisfied by `AmbientTelemetryFacade` (`get_location()`, `get_vessel()`):
   * The accumulator queries the facade.
   * **Explicit Null Check:** If the facade returns `None` (unseeded cold start), the required properties remain unfulfilled. The buffer holds the package in staging until an incoming milestone event hydrates the facade.
   * If the facade returns a valid snapshot, properties are extracted (`star_pos = snapshot.coordinates`, `system_address = snapshot.system_address`) and merged into the buffer.
4. When all `required_properties` are populated, the payload is instantiated and validated against `target_schema_cls`.

#### 3. Deduplication and Rate Guard
To prevent redundant API transmissions:
* A deterministic hash is computed from invariant payload content (e.g., `sha256(system_address + market_id + items_payload)`).
* If an identical hash was dispatched within the cooldown window (e.g., 300 seconds), dispatch is suppressed, emitting a `PackageSuppressedDuplicateEvent`.

#### 4. Asynchronous Event Bus
A typed in-memory event bus broadcasts the complete lifecycle of outbound packages:
* `PackageThresholdSatisfiedEvent`: Emitted when all schema properties are satisfied.
* `PackageDispatchedEvent`: Emitted when the package is handed off to the outbound transport adapter.
* `PackageSuppressedDuplicateEvent`: Emitted when rate or deduplication rules prevent dispatch.
* `PackageValidationFailedEvent`: Emitted if schema validation against `ed-schema` fails.

## Consequences

### Positive
* Fully eliminates premature transmission of incomplete telemetry to external APIs.
* Integrates `ed-schema` models directly as the authoritative validation gate.
* Solves the missing coordinate problem without requiring continuous coupling between journal events.
* Safe handling of cold-start unseeded windows via explicit null gating against ADR 0004 getters.
* Provides full observability into outbound data dispatch via the event bus.

### Negative / Trade-offs
* If a player docks at an outpost without system coordinates previously emitted in the current session and backward journal scan yields no milestones, dispatch is held until an ambient location event is received or proceeds with coordinates omitted (if optional).
* Memory management: Staging buffers must enforce TTL eviction to avoid unbounded growth if a required property is never emitted.
