"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryMaterialsEventdataMaterialsItemDTO:
    """Data transfer object for InaraInaraSetCommanderInventoryMaterialsEventdataMaterialsItemDTO."""

    itemName: str
    itemCount: int


@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryMaterialsEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderInventoryMaterialsEventdataDTO."""

    materials: list[InaraInaraSetCommanderInventoryMaterialsEventdataMaterialsItemDTO]


@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryMaterialsDTO:
    """Synchronizes complete manufactured, raw, and encoded material stocks."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderInventoryMaterialsEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderInventoryMaterialsEventdataMaterialsItemDTO', 'InaraInaraSetCommanderInventoryMaterialsEventdataDTO', 'InaraInaraSetCommanderInventoryMaterialsDTO')
