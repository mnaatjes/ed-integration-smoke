"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderCreditsEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderCreditsEventdataDTO."""

    commanderCredits: int
    commanderLoan: int | None = None
    commanderAssets: int | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderCreditsDTO:
    """Updates commander's credit balance, assets, and loan debt."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderCreditsEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderCreditsEventdataDTO', 'InaraInaraSetCommanderCreditsDTO')
