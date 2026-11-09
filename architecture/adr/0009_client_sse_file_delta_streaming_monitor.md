---
title: "ADR 0009: Client-Side SSE File-Delta Streaming Monitor and Claim-Check Hydration"
tags: ["adr", "streaming", "sse", "file-delta", "claim-check", "ed-transport", "ed-stream-monitor"]
created_at: "2026-11-09"
last_updated_at: "2026-11-09"
---

# ADR 0009: Client-Side SSE File-Delta Streaming Monitor and Claim-Check Hydration

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-09

---

## 1. Context and Problem Statement

`ed-telemetry` v0.10.0 (ADR 0039, SDD-034) introduces lightweight Server-Sent Events (SSE) push notifications on `GET /api/v1/stream` with topic `telemetry.file_delta`. These events notify connected clients in sub-millisecond real time when companion files (`Status.json`, `ModulesInfo.json`, `Cargo.json`, etc.) are written by Frontier's game engine, emitting minimal metadata (`target`, `action`, `raw_hash`, `timestamp`).

Downstream integration testing, diagnostic CLI tools, and prototyping overlays in `ed-integration-smoke` currently lack a standardized client-side streaming monitor. Client applications need to:
1. Passively monitor the SSE stream with zero HTTP polling loops.
2. Decode raw SSE chunks into strongly typed `FileDeltaDTO` data structures.
3. Allow consumers to filter notifications by specific companion file targets.
4. Provide an optional claim-check hydration mechanism to automatically resolve the updated file into a typed domain entity via `ed-telemetry-client` and `ed-hydrator` only when needed.

We require a decoupled workspace member package (`src/ed_stream_monitor`) providing reusable streaming primitives.

---

## 2. Decision Drivers

* **Zero-Polling Reactivity:** Passive stream listening over a single persistent HTTP connection using `ed-transport`.
* **Decoupled Claim-Check Architecture:** The core streaming listener must only decode and yield `FileDeltaDTO` metadata without automatically triggering heavy REST round-trips for unwanted files.
* **Granular Target Filtering:** Allow consumers to listen exclusively for specific files (e.g. `{"ModulesInfo.json", "Cargo.json"}`).
* **Seamless Composition:** Easily compose with existing `ed-telemetry-client` and `ed-hydrator` packages for on-demand payload hydration.
* **Prototyping & Inspection Ready:** Enable CLI scripts (`scripts/watch_file_deltas.py`) to stream deltas with formatted terminal output.

---

## 3. Considered Options

1. **Option 1: Embed SSE Loop in `ed-telemetry-client`.** Adding continuous streaming loops to `TelemetryHttpClient` conflates synchronous request/response contracts with long-lived streaming connections.
2. **Option 2: Ad-Hoc `requests`/`urllib` Streaming in Scripts.** Each script implements its own chunk parsing and SSE regexes, leading to fragile reconnection logic and duplicate error handling.
3. **Option 3: Dedicated Member Package (`src/ed_stream_monitor`).** A decoupled client library packaging `FileDeltaDTO`, `StreamMessageDTO`, and `TelemetryStreamMonitor`, complete with generator interfaces and optional hydration hooks.

---

## 4. Decision Outcome

Chosen option: **Option 3: Dedicated Member Package (`src/ed_stream_monitor`)**.

### Positive Consequences
* `FileDeltaDTO` models file modification notifications cleanly.
* `TelemetryStreamMonitor.listen_deltas()` provides a clean generator yielding deltas matching target filter sets.
* Optional `listen_and_hydrate()` provides an automated bridge to `ed_hydrator` for applications needing full domain entities on delta triggers.
* Provides a foundational streaming primitive for future cockpit annunciator and live TUI dashboards.

### Negative Consequences
* Long-lived streaming requires robust network disconnect and reconnection backoff handling in production daemon contexts.
