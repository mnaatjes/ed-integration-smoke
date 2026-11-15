"""UI-agnostic domain models and presentation state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ThemeMode(StrEnum):
    """Supported visual theme modes."""

    DEFAULT = "default"
    DARK = "dark"
    TRANSPARENT = "transparent"


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    """Color and typography tokens for a theme."""

    mode: ThemeMode
    fg: str
    bg: str
    highlight: str
    font_family: str = "TkDefaultFont"
    font_size: int = 10


@dataclass(slots=True)
class TelemetryRow:
    """A single key-value telemetry row for display."""

    key: str
    label: str
    value: str = ""
    url: str | None = None
    visible: bool = True


@dataclass(slots=True)
class TelemetryViewState:
    """Presentation state for the main telemetry window."""

    rows: list[TelemetryRow] = field(default_factory=list)
    status_text: str = ""


@dataclass(frozen=True, slots=True)
class SettingsTabDescriptor:
    """Metadata describing a settings tab."""

    tab_id: str
    title: str
    order: int = 100
