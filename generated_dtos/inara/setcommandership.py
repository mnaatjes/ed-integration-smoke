"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderShipEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderShipEventdataDTO."""

    shipType: str
    shipGameID: int
    shipName: str | None = None
    shipIdent: str | None = None
    shipHullValue: int | None = None
    shipModulesValue: int | None = None
    isCurrentShip: bool | None = None
    isHot: bool | None = None
    starsystemName: str | None = None
    stationName: str | None = None
    marketID: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderShipDTO:
    """Updates basic metadata of an existing ship in fleet."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderShipEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderShipEventdataDTO', 'InaraInaraSetCommanderShipDTO')
