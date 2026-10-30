"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFcmaterialsCapiV10HeaderDTO:
    """Data transfer object for EddnFcmaterialsCapiV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFcmaterialsCapiV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    MarketID: int
    CarrierID: str
    Items: Any
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnFcmaterialsCapiV10DTO:
    """Data transfer object for EddnFcmaterialsCapiV10DTO."""

    schemaRef: str
    header: EddnFcmaterialsCapiV10HeaderDTO
    message: EddnFcmaterialsCapiV10MessageDTO

__all__ = ('EddnFcmaterialsCapiV10HeaderDTO', 'EddnFcmaterialsCapiV10MessageDTO', 'EddnFcmaterialsCapiV10DTO')
