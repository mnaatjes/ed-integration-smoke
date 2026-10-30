"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderTravelLocationEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderTravelLocationEventdataDTO."""

    starsystemName: str
    stationName: str | None = None
    marketID: int | None = None
    bodyName: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    shipType: str | None = None
    shipGameID: int | None = None
    isTaxiDropShip: bool | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderTravelLocationDTO:
    """Updates commander's current star system and station."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderTravelLocationEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderTravelLocationEventdataDTO', 'InaraInaraSetCommanderTravelLocationDTO')
