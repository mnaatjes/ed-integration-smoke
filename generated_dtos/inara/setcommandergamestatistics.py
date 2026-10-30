"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderGameStatisticsEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderGameStatisticsEventdataDTO."""

    bankAccount: dict[str, Any] | None = None
    combat: dict[str, Any] | None = None
    crime: dict[str, Any] | None = None
    smuggling: dict[str, Any] | None = None
    trading: dict[str, Any] | None = None
    mining: dict[str, Any] | None = None
    exploration: dict[str, Any] | None = None
    passengers: dict[str, Any] | None = None
    searchAndRescue: dict[str, Any] | None = None
    crafting: dict[str, Any] | None = None
    crew: dict[str, Any] | None = None
    multicrew: dict[str, Any] | None = None
    materialTraderStats: dict[str, Any] | None = None
    cqc: dict[str, Any] | None = None
    exobiology: dict[str, Any] | None = None
    thargoid: dict[str, Any] | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderGameStatisticsDTO:
    """Synchronizes complete career game statistics from statistics event."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderGameStatisticsEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderGameStatisticsEventdataDTO', 'InaraInaraSetCommanderGameStatisticsDTO')
