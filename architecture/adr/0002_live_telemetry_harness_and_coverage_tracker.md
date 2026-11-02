---
title: "ADR 0002: Live Telemetry Verification Vehicle and Coverage Audit Tracker"
tags: ["adr", "telemetry", "integration", "sqlite", "coverage", "ed-models", "ed-transport"]
created_at: "2026-11-02"
last_updated_at: "2026-11-02"
---

# ADR 0002: Live Telemetry Verification Vehicle and Coverage Audit Tracker

* Status: Accepted
* Date: 2026-11-02

## Context and Problem Statement

`ed-models` provides pure, zero-I/O domain entities, static catalogs, and journal deserializers covering 258+ Frontier Journal event types and 32-bit cockpit status telemetry flags. However, real-world Frontier log payloads collected live during active gameplay frequently exhibit schema drift, unexpected nullability, undocumented keys, or numeric representation variations.

We need a dedicated, long-running test vehicle within `ed-integration-smoke` to:
1. Connect across the LAN via `ed-transport` to the `ed-telemetry` streaming service running on the active gaming rig.
2. Ingest live raw payloads and pass them through `ed-models` domain deserializers (`EliteDomainFacade.parse_journal_event()` and `parse_telemetry()`).
3. Cross-validate incoming payloads against `ed-schema`.
4. Persist raw payloads and audit events in a local embedded database without external operational overhead.
5. Track achievement against the complete checklist of 258+ in-game target events and telemetry flags codified in `in_game_telemetry_and_event_targets.md`.
6. Record and isolate any domain hydration failures or unmapped schemas for offline analysis.

## Decision Drivers

* **Zero Operational Friction:** The integration test runner must execute autonomously without requiring external database servers (e.g., MySQL, Postgres).
* **Crash-Resilience & Auditability:** Raw payloads and diagnostic stack traces must be safely committed even if individual entity deserializations fail.
* **Strict Hexagonal & Fleet Boundary Adherence:** The harness must cleanly utilize `ed-transport` for network ingress, `ed-schema` for meta-schema compliance, and `ed-models` for domain hydration.
* **Granular Target Auditing:** Live in-game actions must actively check off entries against the 258+ target events catalog.

## Considered Options

1. **Option 1: Flat JSONL Files + In-Memory Dictionaries.** Simple append-only logs, but lacks transactional integrity, concurrent reader support, index queries, and relational coverage summaries.
2. **Option 2: Standalone MySQL / PostgreSQL Server.** Full relational database, but adds heavy deployment overhead, container requirements, and external networking configuration.
3. **Option 3: Embedded SQLite with Write-Ahead Logging (WAL).** Zero configuration, single-file storage, ACID transactions, concurrent readers while writing, native JSON operators (`json_extract`), and negligible memory overhead.

## Decision Outcome

Chosen option: **Option 3: Embedded SQLite with Write-Ahead Logging (WAL)**.

### Architectural Structure

The test vehicle is structured into four decoupled layers inside `ed_integration_smoke.daemon`:

1. **Ingress Client (`client.py`):** Utilizes `ed-transport`'s `AsyncTransportClient` to establish streaming SSE or HTTP connections to remote `ed-telemetry` endpoints.
2. **Domain Pipeline (`pipeline.py`):**
   - Receives raw telemetry envelopes.
   - Dispatches payload to `ed-models.create_domain_facade().parse_journal_event()` or `parse_telemetry()`.
   - Flags unhandled event names, missing dataclass fields, type coercion errors, or schema validation errors.
3. **Storage Engine (`storage.py`):**
   - SQLite database (`fleet_telemetry_smoke.db`) configured with `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;`.
   - Maintains three primary tables:
     - `raw_journal_events`: Complete raw payload with ingest timestamp, sequence ID, and event name.
     - `target_coverage`: Pre-seeded table of all 258+ Journal events and status bitflags tracking first-seen timestamp, occurrence count, and last status.
     - `domain_mismatches`: Ledger recording failed deserializations, raw JSON payload, exception type, message, and traceback.
4. **Target Tracker (`tracker.py`):**
   - In-memory cache synced with `target_coverage` table.
   - Calculates real-time completion percentage across all 11 Journal chapters and telemetry bitfield categories.

## Consequences

### Positive
* Complete real-time auditability of which in-game actions have been executed and verified against domain models.
* Immediate surfacing of domain bugs or missing attributes when new game content or edge cases are triggered.
* Fully self-contained inside `ed-integration-smoke` with zero external service dependencies.

### Negative
* SQLite requires WAL file housekeeping in high-throughput local disk scenarios (negligible for 1–10 Hz telemetry streams).
