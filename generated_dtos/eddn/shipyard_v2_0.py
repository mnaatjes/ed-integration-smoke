"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnShipyardV20HeaderDTO:
    """Data transfer object for EddnShipyardV20HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnShipyardV20MessageDTO:
    """Data transfer object for EddnShipyardV20MessageDTO."""

    systemName: str
    stationName: str
    marketId: int
    timestamp: str
    ships: list[str]
    horizons: bool | None = None
    odyssey: bool | None = None
    allowCobraMkIV: bool | None = None


@dataclass(frozen=True)
class EddnShipyardV20DTO:
    """Data transfer object for EddnShipyardV20DTO."""

    schemaRef: str
    header: EddnShipyardV20HeaderDTO
    message: EddnShipyardV20MessageDTO

__all__ = ('EddnShipyardV20HeaderDTO', 'EddnShipyardV20MessageDTO', 'EddnShipyardV20DTO')
