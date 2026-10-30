"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderShipEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderShipEventdataDTO."""

    shipType: str
    shipGameID: int
    shipName: str | None = None
    shipIdent: str | None = None
    shipHullValue: int | None = None
    shipModulesValue: int | None = None
    isCurrentShip: bool | None = None
    isHot: bool | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderShipDTO:
    """Registers a newly purchased ship in the commander's fleet."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderShipEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderShipEventdataDTO', 'InaraInaraAddCommanderShipDTO')
