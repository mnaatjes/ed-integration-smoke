---
title: "Architectural Notes: Empirical Failure Mode Findings & Implications for ed-schema and ed-connectors"
tags: ["architecture", "findings", "implications", "ed-schema", "ed-connectors", "ed-transport", "eddn", "notes"]
created_at: "2026-10-30"
last_updated_at: "2026-10-30"
---

# Architectural Notes: Empirical Failure Mode Findings & Implications for ed-schema and ed-connectors

## 1. Executive Summary

Executing the 5-layer failure interrogation test suite (`tests/test_rfc0001_failure_modes.py`) against the in-process `MockEddnGateway` test double yielded concrete architectural insights. These findings identify critical boundary requirements, validation gaps, and error categorization rules that govern the upcoming implementation of `ed-connectors` and future maintenance of `ed-schema`.

---

## 2. Key Empirical Findings & Architectural Implications

### 2.1 Finding 1: Fallback Validator Limitations on Negation Schemas (`$ref: "#/definitions/disallowed"`)
* **Empirical Observation:**
  During `test_layer4_schema_disallowed_property_leakage`, injecting `"ActiveFine": 500` was initially accepted by `ed-schema`'s built-in `JsonSchemaParserAdapter._validate_fallback()` because the environment lacked the external `jsonschema` library. The built-in fallback validator evaluated only `type` and `required` properties, failing to resolve local definitions or evaluate schema negation blocks (`{"not": {"type": [...]}}`).
* **Architectural Implication for `ed-schema`:**
  1. **Mandatory Engine Dependency:** Consider promoting `jsonschema` (or `fastjsonschema`) from an optional dynamic import to a mandatory dependency in `ed-schema`'s `pyproject.toml`.
  2. **Ref Resolution Enhancement:** If maintaining a zero-dependency fallback engine remains an invariant, `JsonSchemaParserAdapter` must be upgraded to resolve local `#/definitions/` refs and handle `"not"` negation constraints natively so that privacy filtering is enforced deterministically.

---

### 2.2 Finding 2: Pre-Serialization Egress Privacy Scrubbing
* **Empirical Observation:**
  The EDDN schema architecture actively enforces gateway-level privacy protection by rejecting payloads containing personal commander state (e.g., `ActiveFine`, `Wanted`, `FuelLevel`, `CockpitBreach`, and any localized string matching `*_Localised$`).
* **Architectural Implication for `ed-connectors`:**
  1. **Dedicated Scrubbing Interactor:** Raw Elite Dangerous journal event dictionaries must never be serialized directly into EDDN DTOs.
  2. `ed-connectors` must feature an explicit **Egress Privacy Scrubbing Filter** (a pure domain transformer interactor) that strips blacklisted and localized fields before assembling outbound DTOs.
  3. `ed-schema`'s `validate_call()` acts as the final safety gatekeeper immediately prior to transport dispatch.

---

### 2.3 Finding 3: Poison-Pill Quarantine vs. Offline Spool Buffering
* **Empirical Observation:**
  When `MockEddnGateway` simulated an HTTP 503 outage, `ed-transport`'s retry policy automatically made 3 successive backoff attempts before returning the error. In contrast, when the mock returned an HTTP 400 schema mismatch, retrying was futile.
* **Architectural Implication for `ed-connectors` & `ed-transport`:**
  1. **Strict Error Categorization:**
     - **Transient / Retryable (`500`, `502`, `503`, `504`, TCP connection reset):** Safe to retry with exponential backoff and safe to route to offline bounded spooling on disk (`SpoolManagerPort`).
     - **Fatal / Non-Retryable (`400`, `404`, `405`, `415`):** Must **never** enter the offline spool. Buffering poison-pill payloads causes permanent retry storms and fills the spool buffer when connectivity is restored.
  2. Fatal schema errors must be quarantined or discarded immediately with structured `ERROR` log telemetry.

---

### 2.4 Finding 4: Strict Case-Insensitive Response Header Normalization
* **Empirical Observation:**
  Querying `response.headers.get("Retry-After")` failed during rate-limit testing because `ed-transport` normalizes all inbound response header keys to lowercase (`"retry-after"`).
* **Architectural Implication for `ed-connectors`:**
  1. Downstream consumers must strictly query headers using normalized lowercase keys (or case-insensitive mapping lookups) when reading operational headers (`retry-after`, `x-ratelimit-remaining`, `etag`).

---

### 2.5 Finding 5: Structured Telemetry Logging for Operational Observability
* **Empirical Observation:**
  Unstructured string logging during simulated network drops or schema rejections yields opaque logs that cannot be programmatically triaged by downstream TUIs or background daemons.
* **Architectural Implication for `ed-connectors`:**
  1. `ed-connectors` should incorporate the RFC 0001 structured JSON event model demonstrated by `StructuredJsonLogger`.
  2. Every failed or retried dispatch must emit structured attributes (`category`, `status_code`, `action`, `target`, `schema_ref`), enabling downstream UI components to present clear operator feedback (e.g. "EDDN Gateway under maintenance; requests spooling to disk").
