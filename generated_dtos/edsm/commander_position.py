"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmCommanderPositionResponseCoordinatesDTO:
    """Data transfer object for EdsmCommanderPositionResponseCoordinatesDTO."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class EdsmCommanderPositionResponseDTO:
    """Commander position response returned by  {@link  getCommanderPosition }  request."""

    date: Any
    firstDiscover: Any
    system: Any
    coordinates: EdsmCommanderPositionResponseCoordinatesDTO | None = None
    dateDocked: str | None = None
    dateLastActivity: str | None = None
    isDocked: bool | None = None
    shipFuel: Any | None = None
    shipId: float | None = None
    shipType: str | None = None
    station: str | None = None
    stationId: float | None = None
    systemId: float | None = None
    systemId64: Any | None = None
    url: str | None = None

__all__ = ('EdsmCommanderPositionResponseCoordinatesDTO', 'EdsmCommanderPositionResponseDTO')
