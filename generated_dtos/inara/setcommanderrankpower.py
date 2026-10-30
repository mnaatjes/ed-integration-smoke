"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderRankPowerEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderRankPowerEventdataDTO."""

    powerName: str
    rankValue: int | None = None
    timePledged: int | None = None
    merits: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderRankPowerDTO:
    """Updates Powerplay affiliation, rank, and weekly merits."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderRankPowerEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderRankPowerEventdataDTO', 'InaraInaraSetCommanderRankPowerDTO')
