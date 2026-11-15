---
title: "SDD-004: Hexagonal GUI Core and Legacy EDMC Component Library"
tags: ["sdd", "design", "hexagonal", "gui", "tkinter", "ed_gui_core"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# SDD-004: Hexagonal GUI Core and Legacy EDMC Component Library

- **Status:** Approved for Implementation
- **Governing ADR:** [ADR 0015](../adr/0015_hexagonal_gui_core_and_component_library_architecture.md)
- **Reference Catalog:** [Tkinter Component Library](../research/tkinter_component_library.md)

## 1. Module Topology

```text
src/ed_gui_core/
├── pyproject.toml
├── ed_gui_core/
│   ├── __init__.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── ports/
│   │   ├── __init__.py
│   │   └── ui.py
│   └── adapters/
│       ├── __init__.py
│       └── tkinter/
│           ├── __init__.py
│           └── legacy_edmc/
│               ├── __init__.py
│               ├── shell.py
│               ├── theme.py
│               ├── telemetry.py
│               ├── settings.py
│               └── bridge.py
└── tests/
    └── test_gui_core.py
```

## 2. Domain Layer (`ed_gui_core.domain.models`)

UI-agnostic dataclasses and enums:
- `ThemeMode(StrEnum)`: `DEFAULT = "default"`, `DARK = "dark"`, `TRANSPARENT = "transparent"`.
- `ThemeTokens`: `mode: ThemeMode`, `fg: str`, `bg: str`, `highlight: str`, `font_family: str`, `font_size: int`.
- `TelemetryRow`: `key: str`, `label: str`, `value: str`, `url: str | None = None`, `visible: bool = True`.
- `TelemetryViewState`: `rows: list[TelemetryRow]`, `status_text: str = ""`.
- `SettingsTabDescriptor`: `tab_id: str`, `title: str`, `order: int = 100`.

## 3. Ports Layer (`ed_gui_core.ports.ui`)

`typing.Protocol` interfaces:
- `ThemeEnginePort`: `current_mode -> ThemeMode`, `apply_theme(mode: ThemeMode) -> None`, `register_alternate(primary: Any, alternate: Any) -> None`.
- `WindowShellPort`: `set_title(title: str) -> None`, `set_status(text: str) -> None`, `run() -> None`, `close() -> None`.
- `EventBridgePort`: `emit(event_name: str) -> None`, `subscribe(event_name: str, handler: Callable[[Any], None]) -> None`.
- `PluginSettingsRegistryPort`: `register_tab(descriptor: SettingsTabDescriptor, factory: Callable[[Any], Any]) -> None`, `get_tabs() -> list[tuple[SettingsTabDescriptor, Callable[[Any], Any]]]`.

## 4. Tkinter `legacy_edmc` Adapter (`ed_gui_core.adapters.tkinter.legacy_edmc`)

- `shell.py`: `AppShell` (`tk.Tk` wrapper), `ModalDialog` (`tk.Toplevel` with `OK`/`Cancel` footer), `MenuBar` (`tk.Menu` builder).
- `theme.py`: `ThemeManager` (implements `ThemeEnginePort` with `Default`, `Dark`, `Transparent` token presets), `AlternateWidgetPair`.
- `telemetry.py`: `KeyValueGrid` (2-column responsive `tk.Frame` with dynamic row visibility), `HyperlinkLabel` (`tk.Label` with browser launch & right-click copy), `StatusBar` (`tk.Label` anchored `tk.W`).
- `settings.py`: `ScrollableNotebook` (`ttk.Notebook` with tab-selection menu), `SettingsTab` (`ttk.Frame`), `ThemedLabel`, `EntryWithContextMenu`, `ThemedButton`, `ThemedCheckbutton`, `ThemedRadiobutton`, `ThemedOptionMenu`.
- `bridge.py`: `TkEventBridge` (implements `EventBridgePort` via `event_generate`/`bind`), `PluginSlot` (`tk.Frame`), `PluginSettingsRegistry` (implements `PluginSettingsRegistryPort`).

## 5. Verification

- Unit tests in `src/ed_gui_core/tests/test_gui_core.py` covering domain models, port protocol conformance, and `legacy_edmc` adapter instantiation (gracefully skipping Tk widget instantiation if no `DISPLAY` is available).
- `uv sync`, `.venv/bin/pytest`, and `.venv/bin/ruff check .` must pass.
