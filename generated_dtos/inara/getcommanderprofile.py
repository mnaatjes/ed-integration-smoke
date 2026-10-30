"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraGetCommanderProfileEventdataDTO:
    """Data transfer object for InaraInaraGetCommanderProfileEventdataDTO."""

    searchName: str


@dataclass(frozen=True)
class InaraInaraGetCommanderProfileDTO:
    """Returns basic information about commander from Inara like ranks, squadron, etc."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraGetCommanderProfileEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraGetCommanderProfileEventdataDTO', 'InaraInaraGetCommanderProfileDTO')
