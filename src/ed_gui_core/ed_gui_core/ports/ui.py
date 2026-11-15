"""Abstract Protocol interfaces (ports) for GUI toolkits."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from ed_gui_core.domain.models import SettingsTabDescriptor, ThemeMode


@runtime_checkable
class ThemeEnginePort(Protocol):
    """Port for applying themes and managing alternate widget pairs."""

    @property
    def current_mode(self) -> ThemeMode: ...

    def apply_theme(self, mode: ThemeMode) -> None: ...

    def register_alternate(self, primary: Any, alternate: Any) -> None: ...


@runtime_checkable
class WindowShellPort(Protocol):
    """Port for the main application window shell."""

    def set_title(self, title: str) -> None: ...

    def set_status(self, text: str) -> None: ...

    def run(self) -> None: ...

    def close(self) -> None: ...


@runtime_checkable
class EventBridgePort(Protocol):
    """Port for marshaling background events onto the UI thread."""

    def emit(self, event_name: str) -> None: ...

    def subscribe(self, event_name: str, handler: Callable[[Any], None]) -> None: ...


@runtime_checkable
class PluginSettingsRegistryPort(Protocol):
    """Port for registering and retrieving plugin settings tabs."""

    def register_tab(
        self,
        descriptor: SettingsTabDescriptor,
        factory: Callable[[Any], Any],
    ) -> None: ...

    def get_tabs(self) -> list[tuple[SettingsTabDescriptor, Callable[[Any], Any]]]: ...
