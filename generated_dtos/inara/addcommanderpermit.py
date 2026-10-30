"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderPermitEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderPermitEventdataDTO."""

    starsystemName: str


@dataclass(frozen=True)
class InaraInaraAddCommanderPermitDTO:
    """Records star system entry permit acquisition."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderPermitEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderPermitEventdataDTO', 'InaraInaraAddCommanderPermitDTO')
