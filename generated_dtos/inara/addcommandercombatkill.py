"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderCombatKillEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderCombatKillEventdataDTO."""

    starsystemName: str
    targetName: str
    targetShip: str | None = None
    targetRank: str | None = None
    reward: int | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderCombatKillDTO:
    """Logs an NPC or PvP combat kill."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderCombatKillEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderCombatKillEventdataDTO', 'InaraInaraAddCommanderCombatKillDTO')
