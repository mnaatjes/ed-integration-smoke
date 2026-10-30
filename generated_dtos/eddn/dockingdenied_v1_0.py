"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnDockingdeniedV10HeaderDTO:
    """Data transfer object for EddnDockingdeniedV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnDockingdeniedV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    MarketID: int
    StationName: str
    Reason: str
    horizons: bool | None = None
    odyssey: bool | None = None
    StationType: str | None = None


@dataclass(frozen=True)
class EddnDockingdeniedV10DTO:
    """Data transfer object for EddnDockingdeniedV10DTO."""

    schemaRef: str
    header: EddnDockingdeniedV10HeaderDTO
    message: EddnDockingdeniedV10MessageDTO

__all__ = ('EddnDockingdeniedV10HeaderDTO', 'EddnDockingdeniedV10MessageDTO', 'EddnDockingdeniedV10DTO')
