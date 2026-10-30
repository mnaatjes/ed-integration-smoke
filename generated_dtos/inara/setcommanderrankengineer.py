"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderRankEngineerEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderRankEngineerEventdataDTO."""

    engineerName: str
    rankValue: int | None = None
    rankStage: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderRankEngineerDTO:
    """Updates unlocked engineer rank stage/grade."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderRankEngineerEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderRankEngineerEventdataDTO', 'InaraInaraSetCommanderRankEngineerDTO')
