"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnDockinggrantedV10HeaderDTO:
    """Data transfer object for EddnDockinggrantedV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnDockinggrantedV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    MarketID: int
    StationName: str
    horizons: bool | None = None
    odyssey: bool | None = None
    StationType: str | None = None
    LandingPad: int | None = None


@dataclass(frozen=True)
class EddnDockinggrantedV10DTO:
    """Data transfer object for EddnDockinggrantedV10DTO."""

    schemaRef: str
    header: EddnDockinggrantedV10HeaderDTO
    message: EddnDockinggrantedV10MessageDTO

__all__ = ('EddnDockinggrantedV10HeaderDTO', 'EddnDockinggrantedV10MessageDTO', 'EddnDockinggrantedV10DTO')
