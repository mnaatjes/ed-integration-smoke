---
title: "CLI & TUI UI Elements Evaluation Ledger"
tags: ["cli", "tui", "ui-elements", "evaluation", "notes"]
created_at: "2026-11-15"
last_updated_at: "2026-11-16"
---

# CLI & TUI UI Elements Evaluation Ledger

This document tracks discovered, evaluated, and preferred command-line interface (CLI) and terminal user interface (TUI) interaction patterns. It serves as the reference ledger when selecting tooling, designing component APIs, and implementing reusable components in `ed-ui-cli` and `ed-sdk`.

---

## 1. Evaluation Taxonomy & Candidate Matrix

| Category | UI Element / Interaction Pattern | Tooling Candidate(s) | Status | Evaluation Notes & Suitability |
| :--- | :--- | :--- | :--- | :--- |
| **Search & Autocomplete** | Fuzzy Dropdown & Command Palette | `textual.command.CommandPalette`, `prompt_toolkit.FuzzyWordCompleter` | **High Preference (Selected)** | Search-as-you-type overlay with real-time aligned items and arrow-key selection. Evaluated in `python -m textual`. |
| **Data Grids & Tables** | Bidirectional Scrollable DataTables | `textual.widgets.DataTable` | **High Preference (Selected)** | Tabular grid with virtualized $X$-axis and $Y$-axis scrolling, pinned header rows/columns, and reactive row/cell selection. |
| **Hierarchical Views** | Collapsible Tree Views | `textual.widgets.Tree` | **High Preference (Selected)** | Accordion-style recursive tree with expandable nodes for star maps, JSON DTO inspection, and directory topologies. |
| **Forms & Actions** | Sliding Switch Toggles | `textual.widgets.Switch` | **High Preference (Selected)** | Animated sliding pill for immediate binary hardware/stream transitions (`ON`/`OFF`) without submit gates. |
| **Forms & Actions** | Large Semantic Buttons | `textual.widgets.Button` | **High Preference (Selected)** | Prominent action triggers with semantic variants (`primary`, `success`, `error`, `warning`). Ideal for cockpit controls. |
| **Forms & Actions** | Radio Button Groups | `textual.widgets.RadioSet`, `textual.widgets.RadioButton` | **High Preference (Selected)** | Mutually exclusive single-choice toggles for connection targets and stream operation modes. |
| **Forms & Actions** | Checkboxes | `textual.widgets.Checkbox`, `questionary.checkbox` | **High Preference (Selected)** | Multi-criteria binary/tri-state filters for telemetry channels and event types. |
| **Input & Prompting** | External `$EDITOR` Handoff | `click.edit` | Candidate | Spawns system editor (`nano`, `vim`) for editing JSON filter queries or configuration payloads. |
| **Input & Prompting** | Confirmation Prompts (`[y/N]`) | `typer.confirm`, `click.confirm` | Candidate | Standard Yes/No gate with default handling for destructive actions or branch switches. |
| **Input & Prompting** | Type-Validated & Masked Inputs | `typer.prompt`, `questionary.text` | Candidate | API key and connection parameter entry with asterisk/hidden masking and format validation. |
| **Full-Screen TUI** | Alternate Screen Buffer Canvas | `textual.app.App`, `curses` | Candidate | Dedicated full-screen rendering context restoring clean terminal history upon exit. |
| **Full-Screen TUI** | Multi-Pane Responsive Grid Layouts | `textual.containers`, `rich.layout` | Candidate | Dynamic split-pane arrangements (annunciator grid, metrics panel, event log) reflowing on resize. |
| **Full-Screen TUI** | Event-Driven Keybindings | `textual.binding.Binding` | Candidate | Global hotkeys (`q` to quit, `/` to filter, `tab` to cycle panes, `space` to pause stream). |
| **Streaming & I/O** | Millisecond-Scale Reactive Streaming | `textual.message`, `rich.live.Live` | Candidate | Thread-safe message marshaling from SSE/WebSocket clients to terminal display widgets. |
| **Streaming & I/O** | Indeterminate Spinners & Progress Bars | `rich.progress.Progress`, `rich.status` | Candidate | Connection handshakes, endpoint discovery, and multi-file journal rehydration tracking. |

---

## 2. Discovered Patterns & Component Evaluations

### 2.1 Search, Autocomplete & Fuzzy Dropdowns

#### Search-as-You-Type Dropdowns
* **Description:** An active text search input field coupled to a dynamic overlay dropdown that displays candidate items aligned with the search term as the operator types, enabling arrow-key navigation to highlight and select entries.
* **Intended Use Case:** Star system / station search, journal event filter selection, and quick-firing diagnostic subcommands.
* **Implementation Paths:**
  1. **Full-Screen TUI (Textual):**
     * Built-in modal: [`textual.command.CommandPalette`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/.venv/lib/python3.13/site-packages/textual/command.py) (`Ctrl+P`) with custom `CommandProvider` implementations.
     * Custom in-view dropdown: Pairing a [`textual.widgets.Input`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/.venv/lib/python3.13/site-packages/textual/widgets/_input.py) with an overlay [`textual.widgets.OptionList`](file:///home/michael/src/github.com/mnaatjes/ed-integration-smoke/.venv/lib/python3.13/site-packages/textual/widgets/_option_list.py), updating choices dynamically on `Input.Changed` events.
  2. **Standard Shell Prompt (CLI):**
     * Powered by `prompt_toolkit.completion.FuzzyWordCompleter` or `questionary.autocomplete`, rendering a floating interactive menu directly beneath the prompt cursor.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual
  ```
  *(Press `Ctrl+P` to test fuzzy command search and arrow-key selection)*

---

### 2.2 Data Grids & Tabular Views

#### Bidirectional Scrollable DataTables (`DataTable`)
* **Description:** A high-performance terminal grid featuring virtualized scrolling across both the $X$-axis (horizontal) and $Y$-axis (vertical), with pinned header rows, pinned identifier columns, and flexible cell/row selection cursors.
* **Intended Use Case:**
  * **Telemetry Event Log Inspector:** Pinned headers (`Timestamp`, `Channel`, `Event`, `Source`, `Payload DTO`) where horizontal scrolling allows inspecting deep nested JSON attributes without line-wrapping distortion, and vertical scrolling traverses historical events.
  * **Cartography & System Celestial Bodies:** Tabular view of planets, stellar classes, orbital distances, and terraformability flags.
  * **Market & Outfitting Exchange:** Dense multi-column commodity pricing, stock levels, and supply/demand deltas.
* **Key Capabilities:**
  * `fixed_rows=1`: Keeps column headers persistently visible during deep vertical scrolling.
  * `fixed_columns=1`: Pins primary keys (e.g. event timestamp or commodity name) during horizontal panning.
  * `cursor_type`: Supports `"row"`, `"cell"`, `"column"`, or `"none"`.
  * Virtualized rendering: Only records intersecting the current terminal viewport are rendered, eliminating latency even with thousands of rows.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
  *(Navigate to the Data Table tab to test mouse and keyboard arrow-key dual-axis panning)*

---

### 2.3 Hierarchical & Nested Data Views

#### Collapsible Tree Views (`Tree`)
* **Description:** An accordion-style hierarchical tree structure allowing nodes to expand and collapse on Enter or mouse click. Nodes support attached payload data (`node.data`), nested sub-trees, and reactive selection events (`Tree.NodeSelected`).
* **Intended Use Cases:**
  * **Star System Celestial Maps:** Root star system expanding into primary stars $\rightarrow$ orbiting planets $\rightarrow$ moons $\rightarrow$ surface settlements, signal sources, and biological signatures.
  * **Emitted JSON DTO Inspector:** Recursive tree view for deep telemetry payloads emitted from REST/SSE endpoints (e.g., clicking on a `Location` or `FSDJump` event to expand object properties and array items interactively).
  * **Workspace & Package Topologies:** Interactive directory tree browsing sandbox layouts (`scripts/`, `incubator/<pkg>/src`, `apps/<app>/`).
* **Key Capabilities:**
  * `node.add()` and `node.add_leaf()`: Differentiate between expandable parent containers and leaf values.
  * `node.data`: Binds raw Python dataclasses, DTO instances, or file paths directly to nodes.
  * `auto_expand=False`: Starts nodes collapsed for clean overview, expanding only on demand.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
  *(Navigate to the Tree tab to test node expansion and selection)*

---

### 2.4 Interactive Forms & Action Controls

#### Sliding Switch Toggles (`Switch`)
* **Description:** An animated sliding pill toggle indicating an immediate boolean transition (`ON` / `OFF`) with visual color fills and reactive event emission (`Switch.Changed`).
* **Intended Use Case:** Immediate system and telemetry state toggles:
  * Master stream connect/disconnect (`Live SSE Stream [ON] / [OFF]`).
  * Live stream vs mock stream source selection.
  * Ship systems: Flight Assist, Silent Running, Hardpoints, Cargo Scoop.
* **Difference from Checkbox:** Checkboxes denote multi-criteria selections or passive form filters; switches denote active hardware or operational state changes that take immediate effect.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
  *(Navigate to the Switch tab to test sliding animation and keyboard/mouse toggling)*

#### Large Styled Buttons (`Button`)
* **Description:** Prominent action buttons with distinctive borders, active click/depression visual states, and semantic variant styles (`primary`, `success`, `warning`, `error`).
* **Intended Use Case:** Cockpit annunciator triggers, manual polling triggers (`POLL NOW`), stream reconnect buttons, and cache purge actions.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
* **Notes & Observations:**
  * Keyboard accessible via Tab and Space/Enter.
  * Sizing can be adapted via Textual CSS classes (`width: 100%`, `height: 3`, `border: heavy`).

#### Radio Button Sets (`RadioSet` + `RadioButton`)
* **Description:** Mutually exclusive single-choice option groups with circular indicators (`(•)` vs `( )`) and arrow-key navigation.
* **Intended Use Case:** Operational mode toggles (e.g., selecting data plane: `Live Journal (SSE)` vs `HTTP Polling` vs `Offline Mock`).
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
* **Notes & Observations:**
  * Emits `RadioSet.Changed` events containing the selected radio button index and label.

#### Checkboxes (`Checkbox`)
* **Description:** Independent binary or tri-state toggle boxes with square indicators (`[X]` vs `[ ]`) toggled via click or Spacebar.
* **Intended Use Case:** Telemetry topic and channel filters (`[X] Navigation`, `[X] Combat`, `[X] Status`, `[ ] Market DTOs`).
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual.widgets
  ```
* **Notes & Observations:**
  * Supports reactive binding: state toggles instantly trigger event bus filter mutations without requiring a separate "Submit" action.

---

### 2.5 Interactive Input & Prompting

#### External `$EDITOR` Spawning
* **Description:** Seamlessly launches `$EDITOR` (or system default) with temporary file contents, captures modifications, and restores the terminal on exit.
* **Intended Use Case:** Editing JSON Schema overrides, fine-tuning complex GraphQL/CAPI queries, or drafting manual log annotations.
* **Preview Command:**
  ```bash
  .venv/bin/python -c 'import click; print(click.edit("# Enter telemetry payload filter\n{\n  \"event\": \"FSDJump\"\n}"))'
  ```
* **Notes & Observations:**
  * Supported directly by `click.edit()` without introducing extra dependencies.
  * Requires verification of terminal clean-up on unexpected editor signals.

---

### 2.6 Full-Screen Terminal User Interfaces (TUIs)

#### Alternate Screen Buffer & Reactive Layouts
* **Description:** Full-screen event-driven canvas completely isolated from the terminal's scrollback buffer.
* **Intended Use Case:** Real-time ship telemetry consoles, system status dashboards, and interactive network monitors.
* **Preview Command:**
  ```bash
  .venv/bin/python -m textual
  ```
* **Notes & Observations:**
  * Clean exit leaves terminal prompt completely undisturbed.
  * Textual CSS handles responsive resizing across arbitrary terminal column/row dimensions.

---

## 3. Decision Log & Implementation Milestones

* **2026-11-15:** Ledger established to record candidate UI interaction patterns.
* **2026-11-15:** Selected **Fuzzy Search Dropdowns / Command Palette** as high-preference pattern for star system/station lookups and event filtering.
* **2026-11-15:** Selected **Large Action Buttons (`Button`)**, **Radio Button Groups (`RadioSet`)**, and **Checkboxes (`Checkbox`)** as high-preference interactive controls for cockpit stations and telemetry configuration.
* **2026-11-16:** Selected **Bidirectional Scrollable DataTables (`DataTable`)** as high-preference component for dense telemetry logs, celestial cartography, and commodity markets.
* **2026-11-16:** Selected **Sliding Switch Toggles (`Switch`)** for active operational and hardware stream transitions.
* **2026-11-16:** Selected **Collapsible Tree Views (`Tree`)** for star-system maps, endpoint JSON DTO inspection, and workspace directory exploration.
* *(Pending)*: Author prototype application in `apps/` integrating selected controls into a cohesive telemetry console.
* *(Pending)*: Author ADR in `ed-ui` or `ed-sdk` standardizing prompt helpers and interactive components.
