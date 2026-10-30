"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderShipTransferEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderShipTransferEventdataDTO."""

    shipType: str
    shipGameID: int
    starsystemName: str
    stationName: str | None = None
    marketID: int | None = None
    transferTime: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderShipTransferDTO:
    """Sets ship in-transit transfer status."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderShipTransferEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderShipTransferEventdataDTO', 'InaraInaraSetCommanderShipTransferDTO')
