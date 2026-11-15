"""Presentation-only preview of the EDMC GUI built with ed_gui_core."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ed_gui_core.adapters.tkinter.legacy_edmc import (
    AppShell,
    EntryWithContextMenu,
    ModalDialog,
    ScrollableNotebook,
    SettingsTab,
    ThemedCheckbutton,
    ThemedLabel,
    ThemedOptionMenu,
    ThemeManager,
)
from ed_gui_core.domain.models import TelemetryRow, ThemeMode


def open_settings_dialog(shell: AppShell, theme_manager: ThemeManager) -> None:
    """Open a presentation-only EDMC Settings dialog."""
    selected_theme = tk.StringVar(value=theme_manager.current_mode.value)

    def apply_selected_theme() -> None:
        theme_manager.apply_theme(ThemeMode(selected_theme.get()))

    dialog = ModalDialog(shell.root, title="Settings", on_ok=apply_selected_theme)
    notebook = ScrollableNotebook(dialog.body)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Output tab
    output_tab = SettingsTab(notebook)
    ThemedCheckbutton(output_tab, text="Market data (CSV)").grid(row=0, column=0, sticky=tk.W)
    ThemedCheckbutton(output_tab, text="Shipyard data (CSV)").grid(row=1, column=0, sticky=tk.W)
    ThemedLabel(output_tab, text="Output directory:").grid(
        row=2, column=0, sticky=tk.W, pady=(6, 0)
    )
    EntryWithContextMenu(output_tab, width=36).grid(row=3, column=0, sticky=tk.EW)
    notebook.add(output_tab, text="Output")

    # Configuration tab
    config_tab = SettingsTab(notebook)
    ThemedLabel(config_tab, text="Journal directory:").grid(row=0, column=0, sticky=tk.W)
    EntryWithContextMenu(config_tab, width=36).grid(row=1, column=0, sticky=tk.EW)
    ThemedCheckbutton(config_tab, text="Automatically check for updates").grid(
        row=2, column=0, sticky=tk.W, pady=(6, 0)
    )
    notebook.add(config_tab, text="Configuration")

    # Privacy tab
    privacy_tab = SettingsTab(notebook)
    ThemedCheckbutton(privacy_tab, text="Send station & market data to EDDN").grid(
        row=0, column=0, sticky=tk.W
    )
    notebook.add(privacy_tab, text="Privacy")

    # Appearance tab
    appearance_tab = SettingsTab(notebook)
    ThemedLabel(appearance_tab, text="Theme:").grid(row=0, column=0, sticky=tk.W)
    ThemedOptionMenu(
        appearance_tab,
        selected_theme,
        selected_theme.get(),
        ThemeMode.DEFAULT.value,
        ThemeMode.DARK.value,
        ThemeMode.TRANSPARENT.value,
    ).grid(row=0, column=1, sticky=tk.W, padx=(6, 0))
    notebook.add(appearance_tab, text="Appearance")

    # Plugins tab
    plugins_tab = SettingsTab(notebook)
    ThemedLabel(plugins_tab, text="No plugins loaded (presentation preview).").grid(
        row=0, column=0, sticky=tk.W
    )
    notebook.add(plugins_tab, text="Plugins")


def main() -> None:
    """Launch the presentation-only EDMC GUI preview."""
    shell = AppShell(title="E:D Market Connector (Preview)")
    theme_manager = ThemeManager(shell.root)

    # Core telemetry rows
    rows = [
        TelemetryRow(key="cmdr", label="Cmdr", value="CMDR Jameson"),
        TelemetryRow(
            key="ship",
            label="Ship",
            value="Asp Explorer",
            url="https://coriolis.io/",
        ),
        TelemetryRow(key="suit", label="Suit", value="Artemis Suit", visible=True),
        TelemetryRow(
            key="system",
            label="System",
            value="Shinrarta Dezhra",
            url="https://www.edsm.net/",
        ),
        TelemetryRow(
            key="station",
            label="Station",
            value="Jameson Memorial",
            url="https://inara.cz/",
        ),
    ]
    for row in rows:
        shell.telemetry_grid.set_row(row)

    # Update button (native ttk + themed tk.Label alternate)
    update_btn = ttk.Button(
        shell.frame,
        text="Update",
        command=lambda: shell.set_status("Updated (presentation preview)"),
    )
    update_btn.grid(row=3, column=0, sticky=tk.EW, pady=(6, 2))

    themed_update_btn = tk.Label(shell.frame, text="Update", relief=tk.RAISED, pady=4)
    themed_update_btn.grid(row=3, column=0, sticky=tk.EW, pady=(6, 2))
    themed_update_btn.bind(
        "<Button-1>",
        lambda _e: shell.set_status("Updated (presentation preview)"),
    )
    theme_manager.register_alternate(update_btn, themed_update_btn)

    # Re-grid status bar below Update button
    shell.status_bar.grid(row=4, column=0, sticky=tk.EW, pady=(4, 0))
    shell.set_status("Ready (presentation preview)")

    # Menu bar
    file_menu = shell.menubar.add_submenu("File")
    file_menu.add_command(
        label="Settings",
        command=lambda: open_settings_dialog(shell, theme_manager),
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=shell.close)

    view_menu = shell.menubar.add_submenu("View")
    view_menu.add_command(
        label="Theme: Default",
        command=lambda: theme_manager.apply_theme(ThemeMode.DEFAULT),
    )
    view_menu.add_command(
        label="Theme: Dark",
        command=lambda: theme_manager.apply_theme(ThemeMode.DARK),
    )

    theme_manager.apply_theme(ThemeMode.DEFAULT)
    shell.run()


if __name__ == "__main__":
    main()
