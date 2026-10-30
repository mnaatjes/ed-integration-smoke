"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderCommunityGoalProgressEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderCommunityGoalProgressEventdataDTO."""

    communitygoalGameID: int
    contribution: int
    percentileBand: float | None = None
    tierPercentile: float | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderCommunityGoalProgressDTO:
    """Synchronizes commander contribution to a community goal."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderCommunityGoalProgressEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderCommunityGoalProgressEventdataDTO', 'InaraInaraSetCommanderCommunityGoalProgressDTO')
