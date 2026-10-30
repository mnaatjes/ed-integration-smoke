"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderTravelFSDJumpEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderTravelFSDJumpEventdataDTO."""

    starsystemName: str
    jumpDistance: float | None = None
    fuelUsed: float | None = None
    fuelLevel: float | None = None
    boostUsed: bool | None = None
    shipType: str | None = None
    shipGameID: int | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderTravelFSDJumpDTO:
    """Logs an FSD hyperspace jump event."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderTravelFSDJumpEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderTravelFSDJumpEventdataDTO', 'InaraInaraAddCommanderTravelFSDJumpDTO')
