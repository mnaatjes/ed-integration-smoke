"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderMissionFailedEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderMissionFailedEventdataDTO."""

    missionName: str
    missionGameID: int
    fine: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderMissionFailedDTO:
    """Marks a mission failed."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderMissionFailedEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderMissionFailedEventdataDTO', 'InaraInaraSetCommanderMissionFailedDTO')
