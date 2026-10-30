"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraDelCommanderShipEventdataDTO:
    """Data transfer object for InaraInaraDelCommanderShipEventdataDTO."""

    shipType: str
    shipGameID: int


@dataclass(frozen=True)
class InaraInaraDelCommanderShipDTO:
    """Deletes/sells a ship from the fleet."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraDelCommanderShipEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraDelCommanderShipEventdataDTO', 'InaraInaraDelCommanderShipDTO')
