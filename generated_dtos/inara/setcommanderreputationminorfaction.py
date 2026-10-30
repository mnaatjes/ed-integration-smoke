"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderReputationMinorFactionEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderReputationMinorFactionEventdataDTO."""

    minorfactionName: str
    reputationValue: float


@dataclass(frozen=True)
class InaraInaraSetCommanderReputationMinorFactionDTO:
    """Updates minor faction reputation value."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderReputationMinorFactionEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderReputationMinorFactionEventdataDTO', 'InaraInaraSetCommanderReputationMinorFactionDTO')
