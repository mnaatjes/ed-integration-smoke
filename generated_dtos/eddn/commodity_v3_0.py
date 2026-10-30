"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnCommodityV30HeaderDTO:
    """Data transfer object for EddnCommodityV30HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnCommodityV30MessageCommoditiesItemDTO:
    """Data transfer object for EddnCommodityV30MessageCommoditiesItemDTO."""

    name: str
    meanPrice: int
    buyPrice: int
    stock: int
    stockBracket: Any
    sellPrice: int
    demand: int
    demandBracket: Any
    statusFlags: list[str] | None = None
    Producer: Any | None = None
    Rare: Any | None = None
    id: Any | None = None


@dataclass(frozen=True)
class EddnCommodityV30MessageEconomiesItemDTO:
    """Data transfer object for EddnCommodityV30MessageEconomiesItemDTO."""

    name: str
    proportion: float


@dataclass(frozen=True)
class EddnCommodityV30MessageDTO:
    """Data transfer object for EddnCommodityV30MessageDTO."""

    systemName: str
    stationName: str
    marketId: int
    timestamp: str
    commodities: list[EddnCommodityV30MessageCommoditiesItemDTO]
    stationType: str | None = None
    carrierDockingAccess: str | None = None
    horizons: bool | None = None
    odyssey: bool | None = None
    economies: list[EddnCommodityV30MessageEconomiesItemDTO] | None = None
    prohibited: list[str] | None = None


@dataclass(frozen=True)
class EddnCommodityV30DTO:
    """Data transfer object for EddnCommodityV30DTO."""

    schemaRef: str
    header: EddnCommodityV30HeaderDTO
    message: EddnCommodityV30MessageDTO

__all__ = ('EddnCommodityV30HeaderDTO', 'EddnCommodityV30MessageCommoditiesItemDTO', 'EddnCommodityV30MessageEconomiesItemDTO', 'EddnCommodityV30MessageDTO', 'EddnCommodityV30DTO')
