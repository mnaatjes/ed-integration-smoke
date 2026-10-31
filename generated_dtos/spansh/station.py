"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshStationLandingpadsDTO:
    """Breakdown of the number of landing pads of the station."""

    large: int
    medium: int
    small: int


@dataclass(frozen=True)
class SpanshSpanshStationMarketCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshStationMarketCommoditiesItemDTO."""

    name: str
    symbol: str
    category: str
    commodityId: int
    demand: int
    supply: int
    buyPrice: int
    sellPrice: int


@dataclass(frozen=True)
class SpanshSpanshStationMarketDTO:
    """Commodity market information about the station."""

    commodities: list[SpanshSpanshStationMarketCommoditiesItemDTO]
    prohibitedCommodities: list[str]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshStationShipyardShipsItemDTO:
    """Data transfer object for SpanshSpanshStationShipyardShipsItemDTO."""

    name: str
    symbol: str
    shipId: float


@dataclass(frozen=True)
class SpanshSpanshStationShipyardDTO:
    """Shipyard information about the station."""

    ships: list[SpanshSpanshStationShipyardShipsItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshStationOutfittingModulesItemDTO:
    """Data transfer object for SpanshSpanshStationOutfittingModulesItemDTO."""

    name: str
    symbol: str
    moduleId: float
    class_: int
    rating: str
    category: str
    ship: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshStationOutfittingDTO:
    """Outfitting information about the station."""

    modules: list[SpanshSpanshStationOutfittingModulesItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshStationDTO:
    """Spansh Station contract."""

    name: str
    id: int
    updateTime: str
    realName: str | None = None
    carrierName: str | None = None
    controllingFaction: Any | None = None
    controllingFactionState: Any | None = None
    distanceToArrival: float | None = None
    primaryEconomy: Any | None = None
    secondaryEconomy: Any | None = None
    economies: dict[str, Any] | None = None
    allegiance: Any | None = None
    government: Any | None = None
    services: list[str] | None = None
    type: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    landingPads: SpanshSpanshStationLandingpadsDTO | None = None
    carrierDockingAccess: str | None = None
    market: SpanshSpanshStationMarketDTO | None = None
    shipyard: SpanshSpanshStationShipyardDTO | None = None
    outfitting: SpanshSpanshStationOutfittingDTO | None = None

__all__ = ('SpanshSpanshStationLandingpadsDTO', 'SpanshSpanshStationMarketCommoditiesItemDTO', 'SpanshSpanshStationMarketDTO', 'SpanshSpanshStationShipyardShipsItemDTO', 'SpanshSpanshStationShipyardDTO', 'SpanshSpanshStationOutfittingModulesItemDTO', 'SpanshSpanshStationOutfittingDTO', 'SpanshSpanshStationDTO')
