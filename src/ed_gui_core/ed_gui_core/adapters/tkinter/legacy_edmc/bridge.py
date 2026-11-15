"""Event bridge and plugin extensibility primitives for legacy_edmc Tkinter UI."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

from ed_gui_core.domain.models import SettingsTabDescriptor


class TkEventBridge:
    """Marshals background events onto the Tk main loop."""

    def __init__(self, widget: tk.Misc) -> None:
        self._widget = widget

    def emit(self, event_name: str) -> None:
        self._widget.event_generate(event_name, when="tail")

    def subscribe(self, event_name: str, handler: Callable[[Any], None]) -> None:
        self._widget.bind(event_name, handler)


class PluginSlot(tk.Frame):
    """Dedicated grid region for mounting plugin UI frames."""


class PluginSettingsRegistry:
    """Registry collecting plugin settings tab factories."""

    def __init__(self) -> None:
        self._entries: list[tuple[SettingsTabDescriptor, Callable[[Any], Any]]] = []

    def register_tab(
        self,
        descriptor: SettingsTabDescriptor,
        factory: Callable[[Any], Any],
    ) -> None:
        self._entries.append((descriptor, factory))

    def get_tabs(self) -> list[tuple[SettingsTabDescriptor, Callable[[Any], Any]]]:
        return sorted(self._entries, key=lambda item: (item[0].order, item[0].title))
