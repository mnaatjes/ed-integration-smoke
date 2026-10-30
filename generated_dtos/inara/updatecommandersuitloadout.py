"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraUpdateCommanderSuitLoadoutEventdataDTO:
    """Data transfer object for InaraInaraUpdateCommanderSuitLoadoutEventdataDTO."""

    suitID: int
    suitName: str | None = None
    suitLoadoutName: str | None = None
    suitModules: list[str] | None = None


@dataclass(frozen=True)
class InaraInaraUpdateCommanderSuitLoadoutDTO:
    """Updates an existing Odyssey suit loadout."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraUpdateCommanderSuitLoadoutEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraUpdateCommanderSuitLoadoutEventdataDTO', 'InaraInaraUpdateCommanderSuitLoadoutDTO')
