"""Unit tests for ed_gui_core domain, ports, and legacy_edmc Tkinter adapter."""

from __future__ import annotations

import tkinter as tk

import pytest
from ed_gui_core.adapters.tkinter.legacy_edmc import (
    AppShell,
    PluginSettingsRegistry,
    ThemeManager,
    TkEventBridge,
)
from ed_gui_core.domain.models import (
    SettingsTabDescriptor,
    TelemetryRow,
    TelemetryViewState,
    ThemeMode,
)
from ed_gui_core.ports.ui import (
    EventBridgePort,
    PluginSettingsRegistryPort,
    ThemeEnginePort,
    WindowShellPort,
)


def test_domain_models_defaults() -> None:
    row = TelemetryRow(key="cmdr", label="Cmdr", value="Jameson")
    state = TelemetryViewState(rows=[row], status_text="Ready")
    assert state.rows[0].visible is True
    assert state.status_text == "Ready"


def test_plugin_settings_registry_orders_tabs() -> None:
    registry = PluginSettingsRegistry()
    assert isinstance(registry, PluginSettingsRegistryPort)

    registry.register_tab(SettingsTabDescriptor("b", "Beta", order=20), lambda p: p)
    registry.register_tab(SettingsTabDescriptor("a", "Alpha", order=10), lambda p: p)

    tabs = registry.get_tabs()
    assert [desc.tab_id for desc, _ in tabs] == ["a", "b"]


def test_theme_manager_port_conformance() -> None:
    manager = ThemeManager()
    assert isinstance(manager, ThemeEnginePort)
    assert manager.current_mode == ThemeMode.DEFAULT

    manager.apply_theme(ThemeMode.DARK)
    assert manager.current_mode == ThemeMode.DARK
    assert manager.tokens.fg == "#ff8000"


def test_tk_app_shell_and_event_bridge() -> None:
    try:
        shell = AppShell()
    except tk.TclError:
        pytest.skip("No display available for Tk root window")

    try:
        assert isinstance(shell, WindowShellPort)
        shell.set_status("Connected")
        assert shell.status_bar.cget("text") == "Connected"

        bridge = TkEventBridge(shell.root)
        assert isinstance(bridge, EventBridgePort)
    finally:
        shell.close()
