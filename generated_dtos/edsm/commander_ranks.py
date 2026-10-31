"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmCommanderRanksResponseProgressDTO:
    """Data transfer object for EdsmCommanderRanksResponseProgressDTO."""

    CQC: float
    Combat: float
    Empire: float
    Exobiologist: float
    Explore: float
    Federation: float
    Soldier: float
    Trade: float


@dataclass(frozen=True)
class EdsmCommanderRanksResponseRanksDTO:
    """Data transfer object for EdsmCommanderRanksResponseRanksDTO."""

    CQC: float
    Combat: float
    Empire: float
    Exobiologist: float
    Explore: float
    Federation: float
    Soldier: float
    Trade: float


@dataclass(frozen=True)
class EdsmCommanderRanksResponseRanksverboseDTO:
    """Data transfer object for EdsmCommanderRanksResponseRanksverboseDTO."""

    CQC: str
    Combat: str
    Empire: str
    Exobiologist: str
    Explore: str
    Federation: str
    Soldier: str
    Trade: str


@dataclass(frozen=True)
class EdsmCommanderRanksResponseDTO:
    """Commander ranks response returned by  {@link  getCommanderRanks }  request."""

    progress: EdsmCommanderRanksResponseProgressDTO
    ranks: EdsmCommanderRanksResponseRanksDTO
    ranksVerbose: EdsmCommanderRanksResponseRanksverboseDTO

__all__ = ('EdsmCommanderRanksResponseProgressDTO', 'EdsmCommanderRanksResponseRanksDTO', 'EdsmCommanderRanksResponseRanksverboseDTO', 'EdsmCommanderRanksResponseDTO')
