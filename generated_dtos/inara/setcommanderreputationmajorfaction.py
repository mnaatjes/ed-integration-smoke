"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderReputationMajorFactionEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderReputationMajorFactionEventdataDTO."""

    majorfactionName: str
    reputationValue: float


@dataclass(frozen=True)
class InaraInaraSetCommanderReputationMajorFactionDTO:
    """Updates major faction reputation percentages (Federation, Empire, Alliance)."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderReputationMajorFactionEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderReputationMajorFactionEventdataDTO', 'InaraInaraSetCommanderReputationMajorFactionDTO')
