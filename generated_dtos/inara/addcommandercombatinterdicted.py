"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictedEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderCombatInterdictedEventdataDTO."""

    starsystemName: str
    interdictorName: str
    isSubmitted: bool | None = None
    isPlayer: bool | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictedDTO:
    """Logs player being interdicted by another ship."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderCombatInterdictedEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderCombatInterdictedEventdataDTO', 'InaraInaraAddCommanderCombatInterdictedDTO')
