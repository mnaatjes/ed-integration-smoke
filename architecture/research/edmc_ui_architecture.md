---
title: "EDMarketConnector (EDMC) User Interface Architecture Research"
tags: ["research", "edmc", "tkinter", "ui", "architecture"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# EDMarketConnector (EDMC) User Interface Architecture Research

## 1. Overview & UI Frameworks

EDMarketConnector (EDMC) is built on **Python's standard `tkinter` and `tkinter.ttk` (Themed Tk)** libraries, augmented by custom wrapper widgets and a centralized theming engine.

- **Core Toolkit:** `tkinter` (`tk`) and `tkinter.ttk` (`ttk`).
- **Custom Widget Layer:**
  - `myNotebook.py`: Custom `ttk` wrapper widgets (`Notebook`, `ScrollableNotebook`, `Frame`, `Label`, `EntryMenu`, `Button`, `Checkbutton`, `Radiobutton`, `OptionMenu`) used primarily in the Settings/Preferences dialog and plugin settings tabs.
  - `ttkHyperlinkLabel.py`: `HyperlinkLabel` widget for clickable URLs (Shipyard, System, Station) with right-click copy support.
- **Theming Engine:** `theme.py` (`_Theme` singleton) manages Default (OS-native), Dark, and Transparent themes, including custom title-bar/minimize/close controls when running borderless/transparent.
- **System Tray (Windows):** `simplesystray.SysTrayIcon` in `EDMarketConnector.py` (when `sys.platform == 'win32'` and `no_systray` is not set).

---

## 2. Main Window (Market Connector UI)

- **Entry Class:** `AppWindow` in `EDMarketConnector.py` (initialized with `master: tk.Tk`).
- **Root Layout:** Single `tk.Frame` (`name=appname.lower()`) gridded with `sticky=tk.NSEW` and `columnconfigure(1, weight=1)`.
- **Core Telemetry / Status Grid (Rows 1–5):**
  - `cmdr_label` (`tk.Label`) / `cmdr` (`tk.Label`)
  - `ship_label` (`tk.Label`) / `ship` (`HyperlinkLabel` -> `self.shipyard_url`)
  - `suit_label` (`tk.Label`) / `suit` (`tk.Label`, dynamically shown/hidden via `suit_grid_row` / `suit_shown`)
  - `system_label` (`tk.Label`) / `system` (`HyperlinkLabel` -> `self.system_url`, updated by provider plugins such as EDSM/Inara)
  - `station_label` (`tk.Label`) / `station` (`HyperlinkLabel` -> `self.station_url`, updated by provider plugins)
- **Plugin UI Region:**
  - `_config_plugins(frame, ui_row)` inserts plugin-provided `tk.Frame` / `ttk.Frame` widgets directly into the main window's grid below the core telemetry rows.
- **Action Controls & Status Bar:**
  - **Update Button:** `ttk.Button` (`name='update_button'`) paired with a themed `tk.Label` (`name='themed_update_button'`) registered via `theme.register_alternate(...)` to support Dark/Transparent themes; bound to `self.capi_request_data`.
  - **Status Line:** `tk.Label` (`name='status'`, `anchor=tk.W`) spanning 2 columns at the bottom of the main frame.
- **Menu Bar (`tk.Menu`):**
  - `file_menu` (Stats, Save Raw Data, Settings -> `prefs.PreferencesDialog`, Exit)
  - `edit_menu` (Copy `Ctrl+C`)
  - `help_menu` (About, Bug Report, System Profiler, etc.)
- **Async Event Bridge:** Uses `companion.session.set_tk_master(self.w)` and virtual Tk events (`<<CAPIResponse>>`) to marshal background CAPI responses back onto the Tk main thread.

---

## 3. Settings / Preferences UI

- **Entry Class:** `PreferencesDialog(tk.Toplevel, plugin_browser.PluginBrowserMixIn)` in `prefs.py`.
- **Window Behavior:** Modal/transient `tk.Toplevel` positioned over the parent `tk.Tk` window, resizable (`tk.TRUE, tk.TRUE`), with `-toolwindow` attribute on Windows.
- **Tabbed Container:** `myNotebook.ScrollableNotebook` (`tabmenu=True`, `on_tab_change=self.tabchanged`), which extends `ttk.Notebook` with scrollable tab headers and a tab-selection menu for handling many plugin tabs.
- **Built-in Settings Tabs (in `prefs.py` & `plugin_browser.py`):**
  1. **Output** (`__setup_output_tab`): Market/shipyard/outfitting export formats and output directory settings.
  2. **Configuration** (`__setup_config_tab`): Journal directory, CAPI/hotkey/proxy/update configuration.
  3. **Privacy** (`__setup_privacy_tab`): Commander/data sharing and telemetry privacy toggles.
  4. **Appearance** (`__setup_appearance_tab`): Theme selection (Default, Dark, Transparent), transparency/alpha, font/UI scaling, and language (`L10n`) selection.
  5. **Plugins** (`__setup_plugin_tab`): Installed plugin list, enable/disable toggles, and plugin folder access.
  6. **Plugin Browser** (`PluginBrowserMixIn.setup_browser_tab` in `plugin_browser.py`): Discover/browse/install third-party plugins.
- **Plugin Settings Tabs:**
  - `__setup_plugin_tabs(notebook)` iterates loaded plugins and calls each plugin's `plugin_prefs(parent, cmdr, is_beta)` hook, adding the returned `myNotebook.Frame` to the `ScrollableNotebook` under `plugin.name`.
- **Dialog Footer:** `buttonframe` (`ttk.Frame`) containing `OK` / `Cancel` buttons.
