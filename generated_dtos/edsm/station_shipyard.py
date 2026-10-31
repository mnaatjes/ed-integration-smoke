"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmStationShipyardResponseShipsItemDTO:
    """Data transfer object for EdsmStationShipyardResponseShipsItemDTO."""

    id: float
    name: str


@dataclass(frozen=True)
class EdsmStationShipyardResponseDTO:
    """Response structure of the EDSM system stations shipyard request."""

    id: float
    id64: Any
    marketId: float
    name: str
    sId: float
    sName: str
    ships: list[EdsmStationShipyardResponseShipsItemDTO]
    url: str

__all__ = ('EdsmStationShipyardResponseShipsItemDTO', 'EdsmStationShipyardResponseDTO')
