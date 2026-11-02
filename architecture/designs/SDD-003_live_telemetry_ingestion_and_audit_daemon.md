---
title: "SDD-003: Live Telemetry Ingestion and Audit Daemon"
tags: ["sdd", "design", "telemetry", "daemon", "ed-models", "ed-transport", "ed-integration-smoke"]
created_at: "2026-11-02"
last_updated_at: "2026-11-02"
---

# SDD-003: Live Telemetry Ingestion and Audit Daemon

## 1. Introduction & Purpose

This Software Design Document specifies the architecture, data schemas, component interfaces, and execution flow for the Live Telemetry Ingestion and Audit Daemon within `ed-integration-smoke`.

The daemon continuously captures telemetry and journal logs emitted by the remote `ed-telemetry` service running alongside *Elite Dangerous*, validates payload conformance against `ed-schema`, hydrates pure domain entities via `ed-models`, persists state in an embedded SQLite engine with WAL mode, and actively audits progress against all 258+ Journal events and telemetry status flags.

---

## 2. Component Architecture

```
                  Remote Rig (ed-telemetry)
                             │
                             ▼  [LAN: HTTP / SSE / JSON]
  ┌─────────────────────────────────────────────────────────────┐
  │                 TelemetryIngressClient                      │
  │            (ed-transport AsyncTransportClient)              │
  └──────────────────────────┬──────────────────────────────────┘
                             │ Raw Payload Dict / JSON
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               TelemetryPipelineProcessor                    │
  │                                                             │
  │   1. Route to ed-models Facade                              │
  │      - parse_journal_event(data) -> JournalEvent            │
  │      - parse_telemetry(data)     -> StatusTelemetry         │
  │                                                             │
  │   2. Exception Catch & Diagnostic Normalization             │
  │      - ValueError (Unknown Event)                           │
  │      - TypeError (Missing/Unexpected Field)                 │
  │      - ValidationError (Schema violation)                   │
  └──────────────┬───────────────────────────────┬──────────────┘
                 │ Success                       │ Failure
                 ▼                               ▼
  ┌─────────────────────────────┐ ┌─────────────────────────────┐
  │     CoverageTracker         │ │     MismatchRecorder        │
  │  - Increment hit count      │ │  - Capture error class      │
  │  - Record first/last seen   │ │  - Save stack trace         │
  │  - Calculate Chapter %      │ │  - Persist failing payload  │
  └──────────────┬──────────────┘ └──────────────┬──────────────┘
                 │                               │
                 ▼                               ▼
  ┌─────────────────────────────────────────────────────────────┐
  │               TelemetryStorageEngine (SQLite)               │
  │                                                             │
  │   - raw_events         (id, received_at, event, payload)    │
  │   - target_coverage    (name, chapter, count, first_seen)   │
  │   - domain_mismatches  (id, received_at, event, error, ...) │
  └─────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema (SQLite)

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- 1. Raw Ingest Stream
CREATE TABLE IF NOT EXISTS raw_journal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    event_name TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_raw_events_name ON raw_journal_events(event_name);

-- 2. Coverage Registry
CREATE TABLE IF NOT EXISTS target_coverage (
    target_id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,          -- 'event' or 'status_flag'
    chapter TEXT NOT NULL,              -- e.g. 'travel', 'combat', 'status'
    description TEXT,
    hit_count INTEGER NOT NULL DEFAULT 0,
    first_seen_at TEXT,
    last_seen_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_coverage_chapter ON target_coverage(chapter);

-- 3. Mismatch Ledger
CREATE TABLE IF NOT EXISTS domain_mismatches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TEXT NOT NULL,
    target_id TEXT NOT NULL,
    error_class TEXT NOT NULL,
    error_message TEXT NOT NULL,
    traceback TEXT NOT NULL,
    raw_payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mismatches_target ON domain_mismatches(target_id);
```

---

## 4. In-Memory Registry & Pipeline Flow

1. **Bootstrap:**
   - Instantiate `TelemetryStorageEngine` with path to SQLite database.
   - Run database migrations (`CREATE TABLE IF NOT EXISTS`).
   - Seed `target_coverage` table with all 258+ Journal events (across Chapters 2–13) and 47+ status bitfield flags.
   - Instantiate `EliteDomainFacade` via `ed_models.create_domain_facade()`.
2. **Processing Cycle:**
   - Receive dictionary `data`.
   - If payload contains `"event"`:
     - Dispatches to `facade.parse_journal_event(data)`.
     - On success: Record hit in `target_coverage`, append to `raw_journal_events`.
     - On exception: Record into `domain_mismatches`, append to `raw_journal_events`.
   - If payload contains `"Flags"` or `"Pips"`:
     - Dispatches to `facade.parse_telemetry(data)`.
     - Unpack active flags and record hits for every active flag in `target_coverage`.
3. **Audit Reporting:**
   - Provides summary metrics: `total_targets`, `achieved_targets`, `completion_percentage`, and grouped counts by Chapter.
