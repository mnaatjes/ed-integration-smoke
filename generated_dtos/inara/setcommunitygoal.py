"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommunityGoalEventdataDTO:
    """Data transfer object for InaraInaraSetCommunityGoalEventdataDTO."""

    communitygoalGameID: int
    communitygoalName: str
    starsystemName: str | None = None
    stationName: str | None = None
    goalExpiry: str | None = None
    tierReached: int | None = None
    tierMax: int | None = None
    contributorsNum: int | None = None
    contributionsTotal: int | None = None
    isCompleted: bool | None = None


@dataclass(frozen=True)
class InaraInaraSetCommunityGoalDTO:
    """Synchronizes community goal state."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommunityGoalEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommunityGoalEventdataDTO', 'InaraInaraSetCommunityGoalDTO')
