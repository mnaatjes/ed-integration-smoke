---
title: "ADR 0015: Hexagonal GUI Core and Component Library Architecture (ed_gui_core)"
tags: ["adr", "architecture", "hexagonal", "gui", "tkinter", "ed_gui_core"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0015: Hexagonal GUI Core and Component Library Architecture (`ed_gui_core`)

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-integration-smoke` (`src/ed_gui_core`)

## 1. Context & Problem Statement

Following the research into `EDMarketConnector` (`architecture/research/edmc_ui_architecture.md`) and the articulation of a reusable Tkinter component library (`architecture/research/tkinter_component_library.md`), we need a dedicated GUI prototyping submodule (`ed_gui_core`) in `src/ed_gui_core/`.

The architecture must:
1. Decouple UI-agnostic presentation state and contracts from specific GUI toolkits.
2. Organize components by **tooling** (e.g., `tkinter`, future `pyside6` / `textual` / `web`) and **component library** (e.g., `legacy_edmc`, future `modern_dark`, `minimal_hud`).
3. Allow new toolkits and component libraries to be introduced without modifying domain models or application-level consumers.

## 2. Decision

Adopt a **Hexagonal (Ports & Adapters)** architecture for `ed_gui_core`, organized into three concentric layers:

```text
src/ed_gui_core/
├── pyproject.toml
├── ed_gui_core/
│   ├── __init__.py
│   ├── domain/                  # UI-agnostic state, tokens, and descriptors
│   │   ├── __init__.py
│   │   └── models.py
│   ├── ports/                   # Abstract Protocols (window, theme, bridge, registry)
│   │   ├── __init__.py
│   │   └── ui.py
│   └── adapters/                # Toolkit-specific implementations
│       └── tkinter/
│           └── legacy_edmc/     # Legacy EDMC Tkinter component library
│               ├── __init__.py
│               ├── shell.py     # AppShell, ModalDialog, MenuBar
│               ├── theme.py     # ThemeManager, AlternateWidgetPair
│               ├── telemetry.py # KeyValueGrid, HyperlinkLabel, StatusBar
│               ├── settings.py  # ScrollableNotebook, SettingsTab, ttk form controls
│               └── bridge.py    # TkEventBridge, PluginSlot, PluginSettingsRegistry
└── tests/
```

### 2.1 Layer Responsibilities

- **Domain (`ed_gui_core.domain`):** Pure Python/Pydantic/dataclass models representing theme tokens (`Default`, `Dark`, `Transparent`), telemetry display rows (`cmdr`, `ship`, `suit`, `system`, `station`), and settings tab descriptors. Zero imports from `tkinter` or any GUI framework.
- **Ports (`ed_gui_core.ports`):** `typing.Protocol` interfaces defining `WindowShellPort`, `ThemeEnginePort`, `EventBridgePort`, and `PluginSettingsRegistryPort`.
- **Adapters (`ed_gui_core.adapters.<toolkit>.<library>`):** Concrete implementations grouped by GUI toolkit and component library name. The initial adapter is `ed_gui_core.adapters.tkinter.legacy_edmc`, implementing the `legacy_components` catalog from `tkinter_component_library.md`.

## 3. Consequences

- **Positive:**
  - New toolkits (e.g., `adapters/pyside6/modern_hud/`) or new Tkinter component sets (e.g., `adapters/tkinter/custom_widgets/`) drop in cleanly alongside `adapters/tkinter/legacy_edmc/`.
  - Domain models and port contracts can be unit-tested headlessly without a display server (`DISPLAY`).
  - Consumers import against `ed_gui_core.ports` and `ed_gui_core.domain`, remaining insulated from toolkit-specific widget APIs.
- **Negative / Trade-offs:**
  - Slightly more upfront boilerplate (ports + adapter wrappers) compared to direct `tkinter` usage, which is justified by multi-toolkit flexibility.
