"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderMissionCompletedEventdataCommoditiesItemDTO:
    """Data transfer object for InaraInaraSetCommanderMissionCompletedEventdataCommoditiesItemDTO."""

    name: str
    count: int


@dataclass(frozen=True)
class InaraInaraSetCommanderMissionCompletedEventdataMaterialsItemDTO:
    """Data transfer object for InaraInaraSetCommanderMissionCompletedEventdataMaterialsItemDTO."""

    name: str
    count: int


@dataclass(frozen=True)
class InaraInaraSetCommanderMissionCompletedEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderMissionCompletedEventdataDTO."""

    missionName: str
    missionGameID: int
    reward: int | None = None
    donation: int | None = None
    permits: list[str] | None = None
    commodities: list[InaraInaraSetCommanderMissionCompletedEventdataCommoditiesItemDTO] | None = None
    materials: list[InaraInaraSetCommanderMissionCompletedEventdataMaterialsItemDTO] | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderMissionCompletedDTO:
    """Marks a mission successfully completed."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderMissionCompletedEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderMissionCompletedEventdataCommoditiesItemDTO', 'InaraInaraSetCommanderMissionCompletedEventdataMaterialsItemDTO', 'InaraInaraSetCommanderMissionCompletedEventdataDTO', 'InaraInaraSetCommanderMissionCompletedDTO')
