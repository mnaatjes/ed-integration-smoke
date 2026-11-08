---
title: "ADR 0008: Lightweight Domain Hydration Framework for Telemetry Endpoints"
tags: ["adr", "hydration", "ed-models", "ed-telemetry", "ed-resolver", "facade"]
created_at: "2026-11-08"
last_updated_at: "2026-11-08"
---

# ADR 0008: Lightweight Domain Hydration Framework for Telemetry Endpoints

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-08

---

## 1. Context and Problem Statement

`ed-resolver` provides long-running continuous state reduction over Server-Sent Events (SSE), but does not provide an instantaneous, synchronous on-demand hydration mechanism for arbitrary REST endpoint responses from `ed-telemetry`.

Furthermore, companion scripts, inspection tools, and diagnostic harnesses require direct access to strongly typed `ed-models` domain entities (e.g. `StatusTelemetry`, `JournalEvent`, `CommodityEntity`, `ShipModule`) transformed directly from raw JSON envelopes across all `ed-telemetry` endpoints (`/api/v1/state`, `/api/v1/status/game`, `/api/v1/snapshots/{name}`, `/api/v1/journal/latest`).

We need a lightweight, pure-functional hydration library (`src/ed_hydrator`) that converts incoming `TelemetryResponseDTO` envelopes into typed domain entities without the heavyweight runtime overhead of background queue workers.

---

## 2. Decision Drivers

* **Instantaneous Single-Shot Hydration:** Enable one-shot query scripts to hydrate typed domain entities immediately upon receiving HTTP responses without waiting for SSE stream ticks.
* **Universal Endpoint Compatibility:** Capable of hydrating payloads arriving from any `ed-telemetry` plane (`state`, `status`, `snapshots`, `journal`).
* **Zero Infrastructure Overhead:** Pure domain transformations depending strictly on `ed-models` and `ed-telemetry-client` without threading, background workers, or SQLite dependencies.
* **Bridge to `ed-resolver`:** Ability to cold-start `ed-resolver` state stores using instantaneous hydrated domain models.

---

## 3. Considered Options

1. **Option 1: Rely Solely on Upstream `ed-resolver`.** Lacks REST-native on-demand hydration, couples to blocking `urllib` SSE loops, and only outputs 9 high-level reduced state dataclasses rather than granular `ed-models` entities.
2. **Option 2: Ad-Hoc In-Script Deserialization.** Each script writes custom JSON extraction logic. Leads to code duplication, fragile parsing, and schema drift.
3. **Option 3: Lightweight Workspace Package (`src/ed_hydrator`).** Pure functional domain hydrator mapping raw payloads into strongly typed `ed-models` entities and unified `HydratedTelemetryState` bundles.

---

## 4. Decision Outcome

Chosen option: **Option 3: Lightweight Workspace Package (`src/ed_hydrator`)**.

### Positive Consequences
* `TelemetryDomainHydrator` converts responses from any endpoint into typed `ed-models` domain entities (`StatusTelemetry`, `JournalEvent`, etc.).
* `HydratedTelemetryState` encapsulates the complete consolidated game state from `GET /api/v1/state` in a single strongly typed DTO.
* Seamlessly composes with `TelemetryHttpClient` in `ed_telemetry_client`.

### Negative Consequences
* Auxiliary snapshot parsing requires maintaining mapping definitions for specialized snapshots as new game files emerge.
