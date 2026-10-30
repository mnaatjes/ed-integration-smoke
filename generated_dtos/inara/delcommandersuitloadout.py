"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraDelCommanderSuitLoadoutEventdataDTO:
    """Data transfer object for InaraInaraDelCommanderSuitLoadoutEventdataDTO."""

    suitID: int


@dataclass(frozen=True)
class InaraInaraDelCommanderSuitLoadoutDTO:
    """Deletes a suit loadout."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraDelCommanderSuitLoadoutEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraDelCommanderSuitLoadoutEventdataDTO', 'InaraInaraDelCommanderSuitLoadoutDTO')
