"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderStorageModulesEventdataModulesItemDTO:
    """Data transfer object for InaraInaraSetCommanderStorageModulesEventdataModulesItemDTO."""

    itemName: str
    itemValue: int | None = None
    itemHot: bool | None = None
    starsystemName: str | None = None
    stationName: str | None = None
    marketID: int | None = None
    storageSlot: int | None = None
    inTransit: bool | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderStorageModulesEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderStorageModulesEventdataDTO."""

    modules: list[InaraInaraSetCommanderStorageModulesEventdataModulesItemDTO]


@dataclass(frozen=True)
class InaraInaraSetCommanderStorageModulesDTO:
    """Updates inventory of stored outfitting modules."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderStorageModulesEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderStorageModulesEventdataModulesItemDTO', 'InaraInaraSetCommanderStorageModulesEventdataDTO', 'InaraInaraSetCommanderStorageModulesDTO')
