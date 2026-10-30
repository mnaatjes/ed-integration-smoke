"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraDelCommanderFriendEventdataDTO:
    """Data transfer object for InaraInaraDelCommanderFriendEventdataDTO."""

    commanderName: str
    gamePlatform: str


@dataclass(frozen=True)
class InaraInaraDelCommanderFriendDTO:
    """Removes a target commander from the friends list on Inara."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraDelCommanderFriendEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraDelCommanderFriendEventdataDTO', 'InaraInaraDelCommanderFriendDTO')
