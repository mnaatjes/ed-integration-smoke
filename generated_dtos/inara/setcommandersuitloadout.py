"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderSuitLoadoutEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderSuitLoadoutEventdataDTO."""

    suitID: int
    suitName: str
    suitLoadoutName: str | None = None
    suitModules: list[str] | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderSuitLoadoutDTO:
    """Registers an Odyssey on-foot suit loadout."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderSuitLoadoutEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderSuitLoadoutEventdataDTO', 'InaraInaraSetCommanderSuitLoadoutDTO')
