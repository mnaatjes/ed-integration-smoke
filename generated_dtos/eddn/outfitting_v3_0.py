"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnOutfittingV30HeaderDTO:
    """Data transfer object for EddnOutfittingV30HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnOutfittingV30MessageModulesItemDTO:
    """Data transfer object for EddnOutfittingV30MessageModulesItemDTO."""

    id: int
    Name: str
    BuyPrice: int
    BuyMercCoinsPrice: int


@dataclass(frozen=True)
class EddnOutfittingV30MessageDTO:
    """Data transfer object for EddnOutfittingV30MessageDTO."""

    systemName: str
    stationName: str
    marketId: int
    timestamp: str
    modules: list[EddnOutfittingV30MessageModulesItemDTO]
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnOutfittingV30DTO:
    """Data transfer object for EddnOutfittingV30DTO."""

    schemaRef: str
    header: EddnOutfittingV30HeaderDTO
    message: EddnOutfittingV30MessageDTO

__all__ = ('EddnOutfittingV30HeaderDTO', 'EddnOutfittingV30MessageModulesItemDTO', 'EddnOutfittingV30MessageDTO', 'EddnOutfittingV30DTO')
