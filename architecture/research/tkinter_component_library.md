---
title: "Tkinter Component Library Specification (Derived from EDMC)"
tags: ["research", "tkinter", "component-library", "ui", "architecture"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Tkinter Component Library Specification (Derived from EDMC)

## 1. Purpose

This document articulates a reusable `tkinter` / `tkinter.ttk` component library derived from the UI patterns identified in `EDMarketConnector` (`edmc_ui_architecture.md`). It separates **layout primitives**, **data-display widgets**, **form/settings controls**, **theming**, and **async/event bridging** into a clean, composable architecture.

---

## 2. Component Categories

### 2.1 Window & Shell Primitives

| Component | Base Class | Responsibility |
| :--- | :--- | :--- |
| `AppShell` | `tk.Tk` | Root application window with grid weight configuration, platform icon setup, menu bar, and optional system tray integration. |
| `ModalDialog` | `tk.Toplevel` | Transient dialog positioned over parent, resizable, with `OK` / `Cancel` footer (`buttonframe`) and lifecycle callbacks. |
| `MenuBar` | `tk.Menu` | Declarative menu builder (`File`, `Edit`, `Help`) with keyboard accelerator bindings (`Ctrl+C`, etc.). |

### 2.2 Theming & Visual Alternate Engine

| Component | Base Class | Responsibility |
| :--- | :--- | :--- |
| `ThemeManager` | Singleton | Manages `Default` (OS-native), `Dark`, and `Transparent` themes; applies foreground/background/font tokens recursively. |
| `AlternateWidgetPair` | Adapter | Pairs a native `ttk` widget (e.g., `ttk.Button`) with a custom-styled `tk.Label` fallback for themes where `ttk` styling is constrained. |

### 2.3 Data-Display & Telemetry Widgets

| Component | Base Class | Responsibility |
| :--- | :--- | :--- |
| `KeyValueGrid` | `tk.Frame` | Two-column responsive grid (`column 0`: label, `column 1`: value with `sticky=tk.EW`) supporting dynamic row show/hide (e.g., `suit` row). |
| `HyperlinkLabel` | `tk.Label` / `ttk.Label` | Clickable URL label with hover cursor, external browser launch, and right-click context menu for copying URLs. |
| `StatusBar` | `tk.Label` | Single-line, full-width status indicator anchored west (`tk.W`) at the bottom of the shell. |

### 2.4 Tabbed Settings & Form Controls (`ttk` Wrappers)

| Component | Base Class | Responsibility |
| :--- | :--- | :--- |
| `ScrollableNotebook` | `ttk.Notebook` | Tabbed container with scrollable tab headers and an overflow tab-selection menu for large numbers of tabs. |
| `SettingsTab` | `ttk.Frame` | Standardized padded container (`PADX`, `PADY`, `SEPY`) for configuration sections and plugin-contributed preference panes. |
| `ThemedLabel` | `ttk.Label` | Theme-aware label for settings forms. |
| `EntryWithContextMenu` | `ttk.Entry` | Text input with built-in right-click Cut/Copy/Paste/Select-All context menu. |
| `ThemedButton` | `ttk.Button` | Standardized action button. |
| `ThemedCheckbutton` | `ttk.Checkbutton` | Boolean toggle with consistent left indentation (`BUTTONX`). |
| `ThemedRadiobutton` | `ttk.Radiobutton` | Mutually exclusive option selector. |
| `ThemedOptionMenu` | `ttk.OptionMenu` | Dropdown selector for enumerated configuration values. |

### 2.5 Extensibility & Async Event Bridge

| Component | Base Class | Responsibility |
| :--- | :--- | :--- |
| `PluginSlot` | `tk.Frame` | Dedicated grid region in `AppShell` where external modules/plugins mount custom status frames. |
| `PluginSettingsRegistry` | Registry | Collects `(tab_name, frame_factory)` hooks from plugins and mounts them into `ScrollableNotebook`. |
| `TkEventBridge` | Event Adapter | Marshals background async/thread results onto the Tk main loop via `widget.event_generate('<<EventName>>')`. |
