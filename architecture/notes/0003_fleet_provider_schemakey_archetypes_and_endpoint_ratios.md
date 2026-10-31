---
title: "Architectural Notes: Fleet Provider SchemaKey Archetypes and Endpoint-to-Schema Ratios"
tags: ["architecture", "findings", "implications", "ed-schema", "ed-connectors", "schemakey", "archetypes", "ratios", "notes"]
created_at: "2026-10-31"
last_updated_at: "2026-10-31"
---

# Architectural Notes: Fleet Provider SchemaKey Archetypes and Endpoint-to-Schema Ratios

## 1. Executive Summary

Integration across the *Elite Dangerous* software fleet requires binding disparate external network APIs into the unified `SchemaKey` 4-tuple indexing abstraction established by `ed-schema`.

This architectural note formalizes the comparative taxonomies, URL routing archetypes, and endpoint-to-schema structural ratios across the primary fleet providers (EDSM, Frontier CAPI, EDDN, and Inara). These definitions establish the formal contracts governing provider implementations within the upcoming `ed-connectors` microkernel ([RFC 0001](file:///home/michael/src/github.com/mnaatjes/ed-schema/architecture/rfcs/0001_fleet_unification_and_provider_subpackage_architecture.md)).

---

## 2. Technical Analysis

### 2.1 Diagnostic: Structural Endpoint Divergence

External services developed across the community and game publisher employ divergent API structural patterns:
* **Multi-Endpoint Discrete REST:** Discrete resource URLs where each path binds to an independent contract (EDSM, Frontier CAPI).
* **Single-Endpoint Ingestion Gateway:** A singular fixed URL receiving heterogeneous event payloads discriminated by a root envelope field (EDDN).
* **Single-Endpoint Batch RPC:** A singular fixed URL receiving arrays of heterogeneous actions discriminated by an inner item field (Inara).

Without a universal abstraction, consumer clients would require distinct registry implementations (`DirectRegistry`, `PolymorphicRegistry`, `RpcRegistry`). `ed-schema` unifies these via the 4-tuple `SchemaKey(namespace, endpoint, discriminator_field, discriminator_value)`.

---

### 2.2 Theory: Endpoint-to-Schema Ratio Taxonomy

The relationship between accessible HTTP URLs (endpoints) and validatable JSON schemas determines how routing, validation, and DTO synthesis are structured:

| Provider | Upstream Ratio ($EP : S$) | Downstream Governed Ratio ($EP : S$) | Archetype Classification | Governing Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **EDSM** | **$N : 0$** (Un-schematized upstream) | **$1 : 1$** (18 discrete routes) | **Multi-Endpoint (1:1 Direct REST)** | URL route binds directly to response DTO; no payload discriminator required. |
| **Frontier CAPI** | **$N : N$** (Direct OpenAPI) | **$1 : 1$** (Discrete routes) | **Multi-Endpoint (1:1 Direct REST)** | URL route (`/profile`, `/market`) binds to exact payload DTO. |
| **EDDN** | **$1 : N$** (Polymorphic relay) | **$1 : N$** (1 gateway : 19 schemas) | **Single Endpoint (1:N Root Discriminator)** | Single gateway route (`/upload/`); payload discriminated via root `$schemaRef`. |
| **Inara** | **$1 : N$** (Batch RPC) | **$1 : N$** (1 endpoint : 40+ events) | **Single Endpoint (1:N Batch RPC)** | Single endpoint route (`/inapi/v1/`); payload discriminated via `events[*].eventName`. |

---

### 2.3 Analysis: Architectural Comparison for SchemaKey

The table below catalogs how each provider archetype maps cleanly into `ed-schema`'s universal 4-tuple `SchemaKey`:

#### Architectural Comparison for SchemaKey

| Provider | URL Archetype | `namespace` | `endpoint` | `discriminator_field` | `discriminator_value` | Target Contract Mapping |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EDSM** | Multi-Endpoint (1:1) | `"edsm"` | `"/api-v1/system"` | `None` | `None` | Discrete system response DTO |
| **EDSM** | Multi-Endpoint (1:1) | `"edsm"` | `"/api-status-v1/elite-server"` | `None` | `None` | Discrete server status response DTO |
| **Frontier CAPI** | Multi-Endpoint (1:1) | `"capi"` | `"/profile"` | `None` | `None` | Full account state DTO |
| **EDDN** | Single Endpoint (1:N) | `"eddn"` | `"/upload/"` | `"$schemaRef"` | `"journal/1"` | Polymorphic journal event schema |
| **Inara** | Single Endpoint (1:N) | `"inara"` | `"/inapi/v1/"` | `"eventName"` | `"setCommanderShip"` | Nested batch event DTO |

---

### 2.4 Remediation: Architectural Implications for `ed-connectors`

1. **Provider Facade Specialization:**
   - **EDSM & CAPI Providers (`1:1`):** Dispatch interactors execute direct parameter binding:
     ```python
     key = SchemaKey(namespace="edsm", endpoint="/api-v1/system")
     response_dto = engine.validate_and_deserialize(key, http_response.json())
     ```
   - **EDDN Provider (`1:N Root`):** Router inspects root `$schemaRef` before validating:
     ```python
     schema_ref = payload.get("$schemaRef")
     key = SchemaKey(namespace="eddn", endpoint="/upload/", discriminator_field="$schemaRef", discriminator_value=schema_ref)
     ```
   - **Inara Provider (`1:N Batch Item`):** Router iterates batch array and validates each item independently:
     ```python
     for event in batch["events"]:
         verb = event["eventName"]
         key = SchemaKey(namespace="inara", endpoint="/inapi/v1/", discriminator_field="eventName", discriminator_value=verb)
     ```

2. **DTO Synthesis Boundary:**
   - 1:1 providers generate clean, independent DTO hierarchies without top-level polymorphic wrapper unions.
   - 1:N providers generate a root envelope DTO referencing discriminated child event DTOs.
