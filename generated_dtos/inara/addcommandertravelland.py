"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderTravelLandEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderTravelLandEventdataDTO."""

    starsystemName: str
    bodyName: str
    latitude: float | None = None
    longitude: float | None = None
    shipType: str | None = None
    shipGameID: int | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderTravelLandDTO:
    """Logs a planetary touchdown."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderTravelLandEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderTravelLandEventdataDTO', 'InaraInaraAddCommanderTravelLandDTO')
