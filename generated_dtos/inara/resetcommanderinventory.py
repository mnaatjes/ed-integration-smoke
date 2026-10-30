"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraResetCommanderInventoryEventdataDTO:
    """Data transfer object for InaraInaraResetCommanderInventoryEventdataDTO."""

    inventoryTypes: list[str] | None = None


@dataclass(frozen=True)
class InaraInaraResetCommanderInventoryDTO:
    """Resets inventory collections prior to clean synchronization."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraResetCommanderInventoryEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraResetCommanderInventoryEventdataDTO', 'InaraInaraResetCommanderInventoryDTO')
