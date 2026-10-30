"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderFriendEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderFriendEventdataDTO."""

    commanderName: str
    gamePlatform: str


@dataclass(frozen=True)
class InaraInaraAddCommanderFriendDTO:
    """Adds a friend request to the target commander on Inara."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderFriendEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderFriendEventdataDTO', 'InaraInaraAddCommanderFriendDTO')
