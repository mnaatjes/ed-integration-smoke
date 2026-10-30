"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnBlackmarketV10HeaderDTO:
    """Data transfer object for EddnBlackmarketV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnBlackmarketV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    systemName: str
    stationName: str
    timestamp: str
    name: str
    sellPrice: int
    prohibited: bool
    marketId: int | None = None


@dataclass(frozen=True)
class EddnBlackmarketV10DTO:
    """Data transfer object for EddnBlackmarketV10DTO."""

    schemaRef: str
    header: EddnBlackmarketV10HeaderDTO
    message: EddnBlackmarketV10MessageDTO

__all__ = ('EddnBlackmarketV10HeaderDTO', 'EddnBlackmarketV10MessageDTO', 'EddnBlackmarketV10DTO')
