"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderTravelDockEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderTravelDockEventdataDTO."""

    starsystemName: str
    stationName: str
    marketID: int | None = None
    shipType: str | None = None
    shipGameID: int | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderTravelDockDTO:
    """Logs a docking event at a station, outpost, or carrier."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderTravelDockEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderTravelDockEventdataDTO', 'InaraInaraAddCommanderTravelDockDTO')
