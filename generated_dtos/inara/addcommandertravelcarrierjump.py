"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderTravelCarrierJumpEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderTravelCarrierJumpEventdataDTO."""

    starsystemName: str
    stationName: str | None = None
    marketID: int | None = None
    bodyName: str | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderTravelCarrierJumpDTO:
    """Logs a Fleet Carrier hyperspace jump."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderTravelCarrierJumpEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderTravelCarrierJumpEventdataDTO', 'InaraInaraAddCommanderTravelCarrierJumpDTO')
