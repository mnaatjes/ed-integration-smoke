"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshDumpSystemCoordsDTO:
    """Coordinates of the system."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemPowerconflictprogressItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemPowerconflictprogressItemDTO."""

    power: Any
    progress: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemThargoidwarDTO:
    """State of the Thargoid war in this system."""

    currentState: Any | None = None
    successState: Any | None = None
    failureState: Any | None = None
    progress: float | None = None
    daysRemaining: float | None = None
    portsRemaining: float | None = None
    successReached: bool | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemDTO:
    """Spansh DumpSystem contract."""

    id64: int
    name: str
    coords: SpanshSpanshDumpSystemCoordsDTO
    date: str
    bodies: list[Any]
    allegiance: Any | None = None
    government: Any | None = None
    primaryEconomy: Any | None = None
    secondaryEconomy: Any | None = None
    security: Any | None = None
    population: int | None = None
    bodyCount: int | None = None
    stations: list[Any] | None = None
    controllingFaction: Any | None = None
    factions: list[Any] | None = None
    powerState: Any | None = None
    powerConflictProgress: list[SpanshSpanshDumpSystemPowerconflictprogressItemDTO] | None = None
    powers: list[Any] | None = None
    timestamps: Any | None = None
    controllingPower: Any | None = None
    powerStateControlProgress: float | None = None
    powerStateReinforcement: float | None = None
    powerStateUndermining: float | None = None
    thargoidWar: SpanshSpanshDumpSystemThargoidwarDTO | None = None

__all__ = ('SpanshSpanshDumpSystemCoordsDTO', 'SpanshSpanshDumpSystemPowerconflictprogressItemDTO', 'SpanshSpanshDumpSystemThargoidwarDTO', 'SpanshSpanshDumpSystemDTO')
