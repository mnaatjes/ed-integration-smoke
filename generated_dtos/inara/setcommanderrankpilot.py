"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderRankPilotEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderRankPilotEventdataDTO."""

    rankName: str
    rankValue: int
    rankProgress: float | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderRankPilotDTO:
    """Updates commander pilot ranks and progression percentages."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderRankPilotEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderRankPilotEventdataDTO', 'InaraInaraSetCommanderRankPilotDTO')
