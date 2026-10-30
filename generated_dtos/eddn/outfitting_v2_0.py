"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnOutfittingV20HeaderDTO:
    """Data transfer object for EddnOutfittingV20HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnOutfittingV20MessageDTO:
    """Data transfer object for EddnOutfittingV20MessageDTO."""

    systemName: str
    stationName: str
    marketId: int
    timestamp: str
    modules: list[str]
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnOutfittingV20DTO:
    """Data transfer object for EddnOutfittingV20DTO."""

    schemaRef: str
    header: EddnOutfittingV20HeaderDTO
    message: EddnOutfittingV20MessageDTO

__all__ = ('EddnOutfittingV20HeaderDTO', 'EddnOutfittingV20MessageDTO', 'EddnOutfittingV20DTO')
