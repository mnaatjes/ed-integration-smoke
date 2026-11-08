---
title: "ADR 0006: Workspace-Driven Monorepo Architecture and Fleet Upstream Decoupling"
tags: ["adr", "workspace", "monorepo", "uv", "ed-schema", "ed-telemetry", "refactor"]
created_at: "2026-11-08"
last_updated_at: "2026-11-08"
---

# ADR 0006: Workspace-Driven Monorepo Architecture and Fleet Upstream Decoupling

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-08

---

## 1. Context and Problem Statement

`ed-integration-smoke` initially operated as a single-package sandbox repository containing ad-hoc scripts, local raw schemas (`schemas/`), experimental test harnesses, and an embedded mono-package under `src/ed_integration_smoke`.

As the *Elite Dangerous* fleet matured:
1. `ed-schema` (v1.1.0) was established as the authoritative upstream authority for JSON Schemas and OpenAPI contracts, rendering the local raw schemas (`schemas/`) redundant and prone to drift.
2. Independent modular concerns (e.g. ambient telemetry daemons, itinerary copilot tools, contract threshold buses, mock gateways) require high-velocity prototyping and cross-package reusability without coupling into a single monolithic package.
3. Fleet libraries (`ed-schema`, `ed-transport`, `ed-models`, `ed-resolver`, `ed-telemetry`) continuously publish upstream releases that need coordinated verification and modular extension.

We need a repository architecture that supports hosting multiple modular packages side-by-side in `src/` with isolated dependencies, fast iteration cycles, and frictionless extraction into standalone distributions when interfaces stabilize.

---

## 2. Decision Drivers

* **Frictionless Prototyping:** Rapid local iteration across subpackages without requiring package publishing or manual editable installation steps.
* **Component Reusability:** Clear physical package boundaries (`src/<subpackage>/pyproject.toml`) allowing any prototype subpackage or plugin to be moved or extracted into an independent repository.
* **Upstream Authority:** Strict deprecation of duplicated assets (e.g., local `schemas/`) in favor of canonical fleet distributions (`ed-schema`).
* **Zero Overhead Monorepo Tooling:** Native workspace support using existing project tooling (`uv`) without introducing external build frameworks (e.g., Nx, Turborepo, Bazel).

---

## 3. Considered Options

1. **Option 1: Flat Multi-Module Package (`src/ed_integration_smoke/<submodule>`).** Single root `pyproject.toml` with internal submodules. Keeps tooling simple but couples all dependencies and makes independent re-use and extraction difficult.
2. **Option 2: Native Namespace Multi-Distribution (`src/ed/<subpackage>`).** Independent distributions sharing a namespace. Good for publishing, but higher configuration overhead during exploratory prototyping.
3. **Option 3: UV Workspace-Driven Monorepo (`[tool.uv.workspace] members = ["src/*"]`).** The root repository acts as a workspace coordinating modular subpackages located in `src/*`, where each member package manages its own manifest while resolving local peer packages dynamically.

---

## 4. Decision Outcome

Chosen option: **Option 3: UV Workspace-Driven Monorepo**.

### Positive Consequences
* Subpackages, experimental plugins, and harness prototypes are partitioned into isolated member directories under `src/<package_name>/`.
* Upstream fleet packages are coordinated at the workspace level, pinned to verified release tags:
  * `ed-schema`: `v1.1.0`
  * `ed-transport`: `v0.1.0`
  * `ed-models`: `v0.2.1`
  * `ed-resolver`: `v0.2.0`
  * `ed-telemetry`: `v0.9.0`
* Deprecated legacy `schemas/` directory is eradicated; all schema definitions derive directly from `ed-schema`.
* Legacy ad-hoc scripts, tests, and documentation are purged to yield a clean foundation for modular workspace packages.

### Negative Consequences
* Member packages under `src/` must maintain their respective `pyproject.toml` manifests as they are created.
