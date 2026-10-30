"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnNavrouteV10HeaderDTO:
    """Data transfer object for EddnNavrouteV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnNavrouteV10MessageRouteItemDTO:
    """Data transfer object for EddnNavrouteV10MessageRouteItemDTO."""

    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    StarClass: str


@dataclass(frozen=True)
class EddnNavrouteV10MessageDTO:
    """Data transfer object for EddnNavrouteV10MessageDTO."""

    timestamp: str
    event: Any
    Route: list[EddnNavrouteV10MessageRouteItemDTO]
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnNavrouteV10DTO:
    """Data transfer object for EddnNavrouteV10DTO."""

    schemaRef: str
    header: EddnNavrouteV10HeaderDTO
    message: EddnNavrouteV10MessageDTO

__all__ = ('EddnNavrouteV10HeaderDTO', 'EddnNavrouteV10MessageRouteItemDTO', 'EddnNavrouteV10MessageDTO', 'EddnNavrouteV10DTO')
