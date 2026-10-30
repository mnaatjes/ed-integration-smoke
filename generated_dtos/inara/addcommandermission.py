"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderMissionEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderMissionEventdataDTO."""

    missionName: str
    missionGameID: int
    missionExpiry: str | None = None
    influence: str | None = None
    reputation: str | None = None
    reward: int | None = None
    wing: bool | None = None
    minorfactionName: str | None = None
    starsystemName: str | None = None
    stationName: str | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderMissionDTO:
    """Registers an accepted mission."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderMissionEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderMissionEventdataDTO', 'InaraInaraAddCommanderMissionDTO')
