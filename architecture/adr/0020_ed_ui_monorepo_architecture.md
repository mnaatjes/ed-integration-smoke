---
title: "ADR 0020: ed-ui Monorepo Architecture and Component-Driven Multi-Package Distribution"
tags: ["adr", "ed-ui", "tkinter", "rich", "vue", "monorepo", "architecture", "ui"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0020: `ed-ui` Monorepo Architecture and Component-Driven Multi-Package Distribution

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-integration-smoke` (`src/ed_cli_core`, `src/ed_gui_core`), `ed-fleet-client`, `ed-sdk`

## 1. Context & Problem Statement

Prototyping across `src/ed_cli_core` and `src/ed_gui_core` has established presentation capabilities across two paradigms:
1. Rich/Textual terminal dashboards, live telemetry tables, and diagnostic suites.
2. Tkinter/EDMC legacy HUD components, power distribution meters, and annunciator grids.

As developer adoption expands, web/electron cockpit companions (Vue 3 / TypeScript) will also be required. 

However, bundling Terminal, Desktop GUI, and Web components into a single monolithic package produces an anti-pattern:
- **Language/Package Ecosystem Mismatch:** Python package managers (`pip`, `uv`) distribute `.whl` files; modern web components require `npm`/`pnpm` publishing `.tgz` bundles with TypeScript definitions (`.d.ts`).
- **Dependency Bloat:** An EDMC plugin running in a memory-constrained Tkinter loop should not pull `textual` or `rich`. A headless terminal daemon should not require Tkinter or system Tcl/Tk binaries.
- **Architecture Mismatch ("The Hexagonal Trap"):** Forcing every UI button, frame, and meter behind strict hexagonal ports and adapters creates excessive indirection and contradicts idiomatic UI development (such as Tkinter widget hierarchies or Vue Single File Components).

## 2. Decision

We establish the **`ed-ui` Monorepo Multi-Package Distribution Architecture**, decoupling presentation adapters while unifying common display logic, design tokens, and CI workflows:

1. **Repository Topology (Hybrid Hexagonal Core + Component-Driven Adapters):**
   ```text
   ed-ui/
   ├── pyproject.toml                         # Root UV Workspace configuration
   ├── package.json                           # Root npm/pnpm Workspace configuration
   ├── README.md
   │
   ├── python/
   │   │
   │   ├── ed_ui_core/                        # 1. HEXAGONAL CORE (Pure Python, Zero UI Frameworks)
   │   │   ├── pyproject.toml                 # Publishes: ed-ui-core (PyPI)
   │   │   └── src/
   │   │       └── ed_ui_core/
   │   │           ├── domain/                # Pure Display View-Models & Value Objects
   │   │           │   ├── models.py          # PipState, NavVector, FuelMetrics, AnnunciatorItem
   │   │           │   ├── theme.py           # Color palettes (Orange HUD, Matrix, Elite Dark)
   │   │           │   └── formatters.py      # Unit formatters (Ls -> Ly, m/s -> km/h, credits)
   │   │           ├── ports/                 # Abstract telemetry-to-UI projection ports
   │   │           │   └── presenter.py       # TelemetryViewPresenter interface
   │   │           └── __init__.py
   │   │
   │   ├── ed_ui_tk/                          # 2. TKINTER / EDMC ADAPTER (Component-Driven)
   │   │   ├── pyproject.toml                 # Publishes: ed-ui-tk (PyPI, depends on ed-ui-core)
   │   │   └── src/
   │   │       └── ed_ui_tk/
   │   │           ├── components/            # Direct Component Library (Standard tk/ttk widgets)
   │   │           │   ├── annunciator.py     # AnnunciatorGrid, StatusLamp (direct import)
   │   │           │   ├── pips.py            # PipMeter, PowerBar (direct import)
   │   │           │   ├── navigation.py      # BearingHeadingCompass, TargetDisplay (direct import)
   │   │           │   └── tables.py          # CargoTable, ModuleList (direct import)
   │   │           ├── themes/                # Native Tkinter styles & ttk theme mappings
   │   │           │   └── tk_theme.py        # TkinterStyleManager (translates ed_ui_core.theme)
   │   │           ├── factories/             # Composition Roots & Pre-Wired Assemblies
   │   │           │   ├── shell.py           # create_edmc_shell() (wires full plugin window)
   │   │           │   └── binder.py          # bind_telemetry_client(widget_tree, client)
   │   │           └── __init__.py            # Exports direct components + composition factories
   │   │
   │   └── ed_ui_cli/                         # 3. TERMINAL / CLI ADAPTER (Component-Driven)
   │       ├── pyproject.toml                 # Publishes: ed-ui-cli (PyPI, depends on ed-ui-core & rich)
   │       └── src/
   │           └── ed_ui_cli/
   │               ├── components/            # Direct Rich Renderables & Textual Widgets
   │               │   ├── annunciator.py     # RichAnnunciatorTable (__rich_console__)
   │               │   ├── meters.py          # RichPipMeter, MassJumpProgress
   │               │   └── diagnostics.py     # DiagnosticReporter, DiagnosticTable
   │               ├── factories/             # Composition Roots & Pre-Wired Assemblies
   │               │   ├── dashboard.py       # create_terminal_dashboard(client)
   │               │   └── runner.py          # run_diagnostic_suite(target)
   │               └── __init__.py            # Exports direct components + dashboard runners
   │
   └── web/
       └── ed-ui-vue/                         # 4. VUE 3 / TYPESCRIPT ADAPTER (Component-Driven)
           ├── package.json                   # Publishes: @ed-fleet/vue (npm)
           ├── vite.config.ts
           └── src/
               ├── tokens/                    # Design tokens & color variables (from ed-ui-core)
               ├── components/                # Direct SFC Components (Standard Vue 3)
               │   ├── PipMeter.vue           # <PipMeter :pips="alloc" />
               │   ├── NavCompass.vue         # <NavCompass :heading="deg" :bearing="deg" />
               │   └── AnnunciatorGrid.vue    # <AnnunciatorGrid :flags="stateFlags" />
               ├── composables/               # Reactive Hooks & Telemetry Wiring
               │   └── useTelemetryStream.ts  # useTelemetryStream(url) -> reactive client state
               └── index.ts                   # Exports individual SFCs + install plugin
   ```

2. **Access Model: Direct Imports vs. Composition Roots:**
   - **Atomic Components (Direct Import):** Developers instantiate and place individual widgets directly using standard layout mechanisms without facade indirection:
     ```python
     import tkinter as tk
     from ed_ui_tk import AnnunciatorGrid, PipMeter

     root = tk.Tk()
     pips = PipMeter(root)
     pips.pack()
     grid = AnnunciatorGrid(root)
     grid.pack()
     ```
   - **Pre-Wired Assemblies (Composition Roots & Factories):** For turnkey HUDs or EDMC plugins, packages provide factory composition roots that bind widget trees directly to `ed-fleet-client`:
     ```python
     from ed_fleet_client import create_client
     from ed_ui_tk import bind_telemetry_client, create_edmc_shell

     client = create_client()
     app = create_edmc_shell(parent=root, client=client, theme="orange_hud")
     bind_telemetry_client(app.widget_tree, client)
     ```
   - **Web Component & Composable Usage:**
     ```vue
     <template>
       <PipMeter :pips="telemetry.pips" />
       <NavCompass :heading="telemetry.heading" :bearing="telemetry.bearing" />
     </template>
     <script setup lang="ts">
     import { NavCompass, PipMeter, useTelemetryStream } from '@ed-fleet/vue'
     const { telemetry } = useTelemetryStream('http://localhost:8080')
     </script>
     ```

3. **Operational Workspace Management:**
   - **Python UV Workspaces:** Root `pyproject.toml` configures `[tool.uv.workspace] members = ["python/*"]`. Local edits in `ed_ui_core` reflect immediately in `ed_ui_tk` and `ed_ui_cli` without reinstallation. Tests run across all packages in parallel via `uv run pytest`.
   - **Web pnpm Workspaces:** Root `package.json` configures pnpm workspaces for `web/ed-ui-vue`, compiling TypeScript types and Vite bundles.
   - **Path-Filtered CI/CD Publishing:** GitHub Actions triggers releases based on path changes:
     - Changes in `python/ed_ui_core/**` $\rightarrow$ publish `ed-ui-core` wheel to PyPI.
     - Changes in `python/ed_ui_tk/**` $\rightarrow$ publish `ed-ui-tk` wheel to PyPI.
     - Changes in `python/ed_ui_cli/**` $\rightarrow$ publish `ed-ui-cli` wheel to PyPI.
     - Changes in `web/ed-ui-vue/**` $\rightarrow$ publish `@ed-fleet/vue` to npm.

4. **Scope & Boundary Enforcement Rules:**
   Rather than applying a single-service hexagonal template across the entire monorepo, enforcement is tiered across the **Repository Level** and the **Package Level**:

   - **Tier 1: Repository-Level Invariants (Hexagonal Boundary Enforcement):**
     - **Rule 1.1 (Core Framework Isolation):** `python/ed_ui_core` is strictly framework-agnostic. It must have zero imports of `tkinter`, `ttk`, `rich`, `textual`, or web frameworks. It imports only Python standard library and pure domain data types. Enforced via AST import analysis in test suite.
     - **Rule 1.2 (Strict Inward Dependency Direction):** Outer presentation packages (`ed-ui-tk`, `ed-ui-cli`, `ed-ui-vue`) may import from `ed-ui-core`. `ed-ui-core` must **never** import from `ed-ui-tk`, `ed-ui-cli`, or `ed-ui-vue`.
     - **Rule 1.3 (Adapter-to-Adapter Isolation):** Concrete UI packages are strictly isolated peers. `ed-ui-tk` must never import `ed-ui-cli`, and `ed-ui-cli` must never import `ed-ui-tk`.
     - **Rule 1.4 (Web Asset Decoupling):** `web/` is strictly isolated from Python runtimes. Python linter tools (`mypy`, `ruff`, `pytest`) must ignore `web/`; npm/pnpm linting (`eslint`, `tsc`) governs `web/`.

   - **Tier 2: Package-Level Invariants (Component-Driven Architecture Enforcement):**
     - **Rule 2.1 (Pure Presentation Components):** In `components/`, UI widgets (`AnnunciatorGrid`, `PipMeter`) must remain pure visual rendering elements. They accept display view-models or raw primitives via props/arguments and must **never** instantiate HTTP transports or talk directly to remote network daemons.
     - **Rule 2.2 (Composition Root Encapsulation):** All external runtime coupling (such as subscribing to `ed-fleet-client` SSE events or binding callbacks) is strictly restricted to `factories/` (`shell.py`, `binder.py`). Component files must never contain composition logic.
     - **Rule 2.3 (Direct Component Export Contract):** Each concrete UI package's `__init__.py` must export both atomic components for custom layouts and composition factory helpers for turnkey assemblies.

   - **Tier 3: Monorepo Quality Gate Runner (`scripts/verify.py`):**
     The workspace verification runner enforces these multi-tier boundaries in pre-commit and CI:
     ```python
     CHECKS = [
         ("Pre-commit hooks", ["pre-commit", "run", "--all-files"]),
         ("Core Isolation Gate", ["pytest", "tests/architecture/test_core_isolation.py"]),
         ("Adapter Peer Isolation Gate", ["pytest", "tests/architecture/test_peer_isolation.py"]),
         ("Python Type Checking", ["mypy", "python/"]),
         ("Python Test Suite", ["pytest", "tests/"]),
         ("Web Typecheck & Build", ["pnpm", "--filter", "@ed-fleet/vue", "build"]),
     ]
     ```

## 3. Consequences

- **Positive:**
  - **Zero Unwanted Dependencies:** Applications only install the presentation adapter they require (`ed-ui-tk` for Tkinter/EDMC, `ed-ui-cli` for terminal, `@ed-fleet/vue` for web).
  - **Single Source of Truth:** Unit conversions, color definitions, and view models are centralized in `ed_ui_core` without duplication.
  - **Idiomatic Developer DX:** UI developers access native widgets directly with standard framework patterns, while retaining turn-key composition roots for full assemblies.
- **Negative / Trade-offs:**
  - Requires maintaining a dual-ecosystem monorepo (Python UV workspace alongside npm/pnpm).
  - Cross-ecosystem design token updates require running a token export script to synchronize CSS/TypeScript variables in `ed-ui-vue` from `ed_ui_core.theme`.
