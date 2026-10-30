"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictionEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderCombatInterdictionEventdataDTO."""

    starsystemName: str
    targetName: str
    isSuccess: bool
    isPlayer: bool | None = None


@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictionDTO:
    """Logs player attempting an FSD interdiction on another ship."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderCombatInterdictionEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderCombatInterdictionEventdataDTO', 'InaraInaraAddCommanderCombatInterdictionDTO')
