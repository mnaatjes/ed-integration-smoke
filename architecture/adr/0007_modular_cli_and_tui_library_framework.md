---
title: "ADR 0007: Modular CLI & TUI Library Framework (Typer, Rich, Textual)"
tags: ["adr", "cli", "tui", "typer", "rich", "textual", "telemetry"]
created_at: "2026-11-08"
last_updated_at: "2026-11-08"
---

# ADR 0007: Modular CLI & TUI Library Framework (Typer, Rich, Textual)

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-08

---

## 1. Context and Problem Statement

Scripts and inspection utilities authored within `ed-integration-smoke` frequently re-implement command-line argument parsing, logging setup, live streaming feeds, connection handling, and terminal output styling in an ad-hoc manner.

To accelerate script generation and ensure uniform UX across all diagnostics, we need a shared workspace package (`src/ed_cli_core`) satisfying four primary use cases:
1. **Clear, Structured Tail Presentation:** Real-time log/event streaming where each line is cleanly identifiable with event topics, timestamps, status indicators, and formatted payloads.
2. **Modular Dashboard Displays:** Single-screen, grouped terminal dashboard components for displaying telemetry state, fleet health, and system snapshots.
3. **Reusable Visual Components:** Connection status widgets, progress bars, metric callouts, and tabular summaries.
4. **Universal Common Options:** Standardized CLI parameters (host, port, API key, output format, log level, dry-run) composable across all Typer-based scripts.

---

## 2. Decision Drivers

* **Ergonomic Script Authoring:** Minimum boilerplate required to spin up a new utility script or diagnostic harness.
* **Component Modularity:** Visual and layout primitives can be composed interchangeably between one-shot CLI commands and interactive full-screen applications.
* **Dual-Mode Presentation:** Clean separation between continuous stdout tailing (pipeable, CI-friendly) and full-screen reactive TUI dashboards (operator-friendly).
* **Strict Type Safety:** Type-annotated interfaces compatible with Python 3.13, MyPy strict mode, and Ruff.

---

## 3. Considered Options

1. **Option 1: Standard Library (`argparse` + `curses`).** Zero external dependencies, but prohibitive boilerplate, poor styling capabilities, and clumsy event loop handling.
2. **Option 2: Standalone `rich` + `click`.** Mature and flexible, but lacks reactive widget layouts for full-screen dashboards and requires significant wiring for interactive viewports.
3. **Option 3: Tri-Tier Stack (`typer` + `rich` + `textual`).**
   * `typer`: High-level declarative command dispatch, argument parsing, and common option composition.
   * `rich`: Headless stream formatting, syntax highlighting, progress bars, tables, and tail log formatters.
   * `textual`: Modern, async reactive TUI widgets, grid/group layouts, and full-screen dashboards.

---

## 4. Decision Outcome

Chosen option: **Option 3: Tri-Tier Stack (`typer` + `rich` + `textual`)**.

### Positive Consequences
* `src/ed_cli_core` provides shared Typer option decorators for seamless fleet server connection (`--host`, `--port`, `--api-key`).
* Tail formatting components render telemetry journal and status frames with distinctive visual badging, color-coded topics, and JSON payload highlighting.
* Modular dashboard widgets provide standardized status cards, metric tables, and connection pills usable in both Rich console layouts and Textual TUI screens.
* Scripts can be constructed with minimal lines of glue code.

### Negative Consequences
* Introduces `typer` and `textual` dependencies into the workspace environment.
