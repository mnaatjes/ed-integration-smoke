"""Workbench harness package exports and auto-discovery."""

from __future__ import annotations

# Import slot definitions to register them automatically
from workbench.slots import fsd_target, nav_route

from .registry import ComponentKind, ComponentSlot, get_slot, list_slots, register_slot

__all__ = [
    "ComponentKind",
    "ComponentSlot",
    "fsd_target",
    "get_slot",
    "list_slots",
    "nav_route",
    "register_slot",
]
