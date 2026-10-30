"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderMissionAbandonedEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderMissionAbandonedEventdataDTO."""

    missionName: str
    missionGameID: int
    fine: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderMissionAbandonedDTO:
    """Marks a mission abandoned."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderMissionAbandonedEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderMissionAbandonedEventdataDTO', 'InaraInaraSetCommanderMissionAbandonedDTO')
