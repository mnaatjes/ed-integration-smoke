"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderInventoryEventdataDTO."""

    itemName: str
    itemCount: int


@dataclass(frozen=True)
class InaraInaraSetCommanderInventoryDTO:
    """Sets general item inventory counts."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderInventoryEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderInventoryEventdataDTO', 'InaraInaraSetCommanderInventoryDTO')
