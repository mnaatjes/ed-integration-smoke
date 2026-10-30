"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryCargoEventdataCargoItemDTO:
    """Data transfer object for InaraInaraSetCommanderInventoryCargoEventdataCargoItemDTO."""

    itemName: str
    itemCount: int
    isStolen: bool | None = None
    isMission: bool | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryCargoEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderInventoryCargoEventdataDTO."""

    cargo: list[InaraInaraSetCommanderInventoryCargoEventdataCargoItemDTO]


@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryCargoDTO:
    """Sets commodity cargo manifest."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderInventoryCargoEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderInventoryCargoEventdataCargoItemDTO', 'InaraInaraSetCommanderInventoryCargoEventdataDTO', 'InaraInaraSetCommanderInventoryCargoDTO')
