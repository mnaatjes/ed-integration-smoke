"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderCombatDeathEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderCombatDeathEventdataDTO."""

    starsystemName: str
    opponentName: str | None = None
    wingOpponentNames: list[str] | None = None
    isPvP: bool | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderCombatDeathDTO:
    """Logs player ship destruction."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderCombatDeathEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderCombatDeathEventdataDTO', 'InaraInaraAddCommanderCombatDeathDTO')
