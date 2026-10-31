"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshDumpFactionSystemsItemCoordsDTO:
    """Coordinates of the system."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SpanshSpanshDumpFactionSystemsItemDTO:
    """Data transfer object for SpanshSpanshDumpFactionSystemsItemDTO."""

    systemName: str
    systemId64: int
    coords: SpanshSpanshDumpFactionSystemsItemCoordsDTO
    isControllingFaction: bool | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpFactionDTO:
    """Spansh DumpFaction contract."""

    name: str
    systems: list[SpanshSpanshDumpFactionSystemsItemDTO]
    allegiance: Any | None = None
    government: Any | None = None

__all__ = ('SpanshSpanshDumpFactionSystemsItemCoordsDTO', 'SpanshSpanshDumpFactionSystemsItemDTO', 'SpanshSpanshDumpFactionDTO')
