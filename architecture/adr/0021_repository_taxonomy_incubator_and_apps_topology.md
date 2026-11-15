---
title: "ADR 0021: Repository Taxonomy, Incubator Subpackages, and Applications Topology"
tags: ["adr", "architecture", "taxonomy", "incubator", "apps", "workspace"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
status: "accepted"
---

# ADR 0021: Repository Taxonomy, Incubator Subpackages, and Applications Topology

## Context and Problem Statement

`ed-integration-smoke` serves as the exploratory integration workbench across the *Elite Dangerous* software fleet (`ed-schema`, `ed-transport`, `ed-models`, `ed-telemetry`, `ed-fleet-client`, and `ed-ui`).

Initially, nine experimental subpackages were incubated inside a root `src/*` workspace directory. As these components matured and were promoted into standalone repositories (`ed-fleet-client` and `ed-ui`), the role of `ed-integration-smoke` evolved from a transitional incubation container into a permanent integration sandbox.

Retaining experimental modules in `src/` introduced several architectural conflicts:
1. Standard Python tooling (PEP 517/PEP 621) assumes `src/` houses the primary canonical distribution package of the repository, not transient prototypes.
2. Single-file CLI scripts, multi-module reusable library prototypes, and full-scale GUI/TUI applications were conflated without clear lifecycle boundaries.
3. Developers could not readily distinguish between throwaway spike solutions, candidate packages targeted for extraction, and end-to-end integration apps.

A clear repository taxonomy is required to govern where new integration code, multi-module library prototypes, and runnable applications reside.

---

## Decision Drivers

* **Lifecycle Disambiguation:** Clear structural boundaries between single-file smoke scripts, multi-package library candidates, and full runnable reference applications.
* **Packaging Tooling Ergonomics:** Clean separation so `uv` workspace declarations (`uv.workspace`) can target incubation modules without polluting the root package metadata.
* **Extraction Readiness:** A standardized directory layout that simplifies promoting an incubated package into an external standalone repository.
* **Preserving `src/` Integrity:** Reserving `src/` exclusively for a canonical `ed_integration_smoke` harness library if the testbench itself ever distributes reusable testing utilities.

---

## Considered Options

1. **Option 1: Retain `src/*` for all future prototypes.**
   * *Drawback:* Conflates canonical code with transient prototypes; causes tooling warnings when building wheels or managing workspaces.
2. **Option 2: Place all non-script code in `scripts/`.**
   * *Drawback:* `scripts/` is intended for lightweight, standalone executable utilities. Placing multi-module packages with internal tests and packaging configurations inside `scripts/` creates messy pathing and breaks import resolution.
3. **Option 3: Establish a Tri-Tier Sandbox Taxonomy (`scripts/`, `incubator/`, `apps/`).**
   * *Benefit:* Strictly categorizes code based on architectural complexity and intended lifecycle.

---

## Decision Outcome

Chosen **Option 3: Establish a Tri-Tier Sandbox Taxonomy (`scripts/`, `incubator/`, `apps/`)**.

### Directory Topology Specifications

```
ed-integration-smoke/
├── scripts/               # Tier 1: Single-file CLI diagnostic utilities & smoke probes
│   ├── diagnose_telemetry.py
│   ├── tail_endpoint.py
│   └── watch_file_deltas.py
│
├── incubator/             # Tier 2: Multi-file library subpackages candidate for promotion
│   ├── README.md          # Governance & promotion checklist
│   └── <candidate_pkg>/   # Self-contained subpackage (pyproject.toml, src/, tests/)
│       ├── pyproject.toml
│       ├── src/<candidate_pkg>/
│       └── tests/
│
├── apps/                  # Tier 3: Complete, multi-component runnable prototype applications
│   ├── README.md          # Application index & execution instructions
│   └── <app_name>/        # Multi-file reference app or prototype service
│       ├── main.py        # Entry point
│       ├── views/         # UI frames or templates
│       └── README.md      # Application runbook
│
├── architecture/          # UP Inception & Elaboration engineering ledgers (ADRs, SDDs)
└── tests/                 # Integration test suite asserting fleet compatibility
```

---

## Taxonomy Definitions & Governance Rules

### 1. `scripts/` (Executable Smoke Utilities)
* **Scope:** Standalone Python scripts executable directly via CLI.
* **Rule:** Must remain single files or depend strictly on installed fleet packages (`ed_fleet_client`, `ed_ui_cli`). Never define internal package hierarchies or submodules inside `scripts/`.
* **Purpose:** Ad-hoc operator diagnostics, endpoint polling, and manual connection verification.

### 2. `incubator/` (Candidate Library Subpackages)
* **Scope:** Multi-file subpackages implementing candidate domain models, derivers, or protocols intended for future extraction into external fleet repositories.
* **Rule:** Each incubated project must be self-contained:
  - Reside in `incubator/<name>/`.
  - Include its own `pyproject.toml` with declared dependencies.
  - Structure source under `src/<name>/` (`src-layout`).
  - Provide dedicated unit tests under `tests/`.
  - Can be added to `[tool.uv.workspace] members = ["incubator/*"]` when active.
* **Exit Gate:** When stable, the subpackage is extracted via `git subtree` or copied into a new standalone repository (following the UP Inception discipline).

### 3. `apps/` (Prototype & Reference Applications)
* **Scope:** Full-fledged interactive applications that compose multiple fleet libraries (e.g. a multi-window Tkinter telemetry station, a complex Textual TUI dashboard, or a mock backend service).
* **Rule:** An application is an end-user runnable target, not a library. It consumes published fleet packages or incubated modules to validate user experience, UI responsiveness, and composition root performance.

---

## Validation & Touchpoints

* Validated through the successful promotion of `ed_cli_core` and `ed_gui_core` into `ed-ui`, and `ed_telemetry_client` / `ed_hydrator` / `ed_stream_monitor` into `ed-fleet-client`.
* Pre-commit and type checker configs configured to lint `scripts/`, `apps/`, and `incubator/` uniformly.
