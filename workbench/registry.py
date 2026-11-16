"""Component registration schema and workbench catalog."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from ed_fleet_client import EliteDangerousClient
from rich.console import RenderableType
from textual.widget import Widget


class ComponentKind(StrEnum):
    """Component rendering model."""

    RICH = "rich"
    TEXTUAL = "textual"


@dataclass
class ComponentSlot:
    """Descriptor defining a slotable prototype component in the workbench."""

    name: str
    description: str
    kind: ComponentKind
    mock_factory: Callable[[], Any]
    live_connector: Callable[[EliteDangerousClient, Callable[[Any], None]], Any] | None = None
    rich_renderer: Callable[[Any], RenderableType] | None = None
    widget_factory: Callable[[Any], Widget] | None = None
    tags: list[str] = field(default_factory=list)


_REGISTRY: dict[str, ComponentSlot] = {}


def register_slot(slot: ComponentSlot) -> ComponentSlot:
    """Register a prototype component into the workbench."""
    _REGISTRY[slot.name] = slot
    return slot


def get_slot(name: str) -> ComponentSlot:
    """Retrieve registered slot by name."""
    if name not in _REGISTRY:
        raise KeyError(
            f"Component slot '{name}' not found. Available slots: {list(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]


def list_slots() -> list[ComponentSlot]:
    """Return all registered component slots."""
    return list(_REGISTRY.values())
