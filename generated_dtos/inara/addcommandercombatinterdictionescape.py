"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictionEscapeEventdataDTO:
    """Data transfer object for InaraInaraAddCommanderCombatInterdictionEscapeEventdataDTO."""

    starsystemName: str
    interdictorName: str


@dataclass(frozen=True)
class InaraInaraAddCommanderCombatInterdictionEscapeDTO:
    """Logs escaping an interdiction vector tether."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraAddCommanderCombatInterdictionEscapeEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraAddCommanderCombatInterdictionEscapeEventdataDTO', 'InaraInaraAddCommanderCombatInterdictionEscapeDTO')
