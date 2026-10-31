"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemLandingpadsDTO:
    """Breakdown of the number of landing pads of the station."""

    large: int
    medium: int
    small: int


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemMarketCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshBodyStationsItemMarketCommoditiesItemDTO."""

    name: str
    symbol: str
    category: str
    commodityId: int
    demand: int
    supply: int
    buyPrice: int
    sellPrice: int


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemMarketDTO:
    """Commodity market information about the station."""

    commodities: list[SpanshSpanshBodyStationsItemMarketCommoditiesItemDTO]
    prohibitedCommodities: list[str]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemShipyardShipsItemDTO:
    """Data transfer object for SpanshSpanshBodyStationsItemShipyardShipsItemDTO."""

    name: str
    symbol: str
    shipId: float


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemShipyardDTO:
    """Shipyard information about the station."""

    ships: list[SpanshSpanshBodyStationsItemShipyardShipsItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemOutfittingModulesItemDTO:
    """Data transfer object for SpanshSpanshBodyStationsItemOutfittingModulesItemDTO."""

    name: str
    symbol: str
    moduleId: float
    class_: int
    rating: str
    category: str
    ship: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemOutfittingDTO:
    """Outfitting information about the station."""

    modules: list[SpanshSpanshBodyStationsItemOutfittingModulesItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBodyStationsItemDTO:
    """Data transfer object for SpanshSpanshBodyStationsItemDTO."""

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
    landingPads: SpanshSpanshBodyStationsItemLandingpadsDTO | None = None
    carrierDockingAccess: str | None = None
    market: SpanshSpanshBodyStationsItemMarketDTO | None = None
    shipyard: SpanshSpanshBodyStationsItemShipyardDTO | None = None
    outfitting: SpanshSpanshBodyStationsItemOutfittingDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshBodySignalsDTO:
    """Planets only.  The signals that can be found on the planet."""

    signals: dict[str, Any] | None = None
    updateTime: str | None = None
    genuses: list[str] | None = None


@dataclass(frozen=True)
class SpanshSpanshBodyRingsItemSignalsDTO:
    """The signals that can be found within the belt or ring."""

    signals: dict[str, Any]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBodyRingsItemDTO:
    """Data transfer object for SpanshSpanshBodyRingsItemDTO."""

    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float
    id64: int | None = None
    signals: SpanshSpanshBodyRingsItemSignalsDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshBodyBeltsItemSignalsDTO:
    """The signals that can be found within the belt or ring."""

    signals: dict[str, Any]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBodyBeltsItemDTO:
    """Data transfer object for SpanshSpanshBodyBeltsItemDTO."""

    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float
    id64: int | None = None
    signals: SpanshSpanshBodyBeltsItemSignalsDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshBodyDTO:
    """Spansh Body contract."""

    id64: int
    bodyId: int
    name: str
    updateTime: str
    orbitalPeriod: float | None = None
    semiMajorAxis: float | None = None
    orbitalEccentricity: float | None = None
    orbitalInclination: float | None = None
    argOfPeriapsis: float | None = None
    meanAnomaly: float | None = None
    ascendingNode: float | None = None
    timestamps: dict[str, Any] | None = None
    stations: list[SpanshSpanshBodyStationsItemDTO] | None = None
    type: str | None = None
    subType: Any | None = None
    distanceToArrival: float | None = None
    mainStar: bool | None = None
    age: int | None = None
    spectralClass: Any | None = None
    luminosity: str | None = None
    absoluteMagnitude: float | None = None
    solarMasses: float | None = None
    solarRadius: float | None = None
    surfaceTemperature: float | None = None
    rotationalPeriod: float | None = None
    rotationalPeriodTidallyLocked: bool | None = None
    axialTilt: float | None = None
    parents: list[dict[str, Any]] | None = None
    isLandable: bool | None = None
    gravity: float | None = None
    earthMasses: float | None = None
    radius: float | None = None
    surfacePressure: float | None = None
    volcanismType: str | None = None
    atmosphereType: Any | None = None
    atmosphereComposition: dict[str, Any] | None = None
    solidComposition: dict[str, Any] | None = None
    terraformingState: str | None = None
    materials: dict[str, Any] | None = None
    signals: SpanshSpanshBodySignalsDTO | None = None
    reserveLevel: str | None = None
    rings: list[SpanshSpanshBodyRingsItemDTO] | None = None
    belts: list[SpanshSpanshBodyBeltsItemDTO] | None = None

__all__ = ('SpanshSpanshBodyStationsItemLandingpadsDTO', 'SpanshSpanshBodyStationsItemMarketCommoditiesItemDTO', 'SpanshSpanshBodyStationsItemMarketDTO', 'SpanshSpanshBodyStationsItemShipyardShipsItemDTO', 'SpanshSpanshBodyStationsItemShipyardDTO', 'SpanshSpanshBodyStationsItemOutfittingModulesItemDTO', 'SpanshSpanshBodyStationsItemOutfittingDTO', 'SpanshSpanshBodyStationsItemDTO', 'SpanshSpanshBodySignalsDTO', 'SpanshSpanshBodyRingsItemSignalsDTO', 'SpanshSpanshBodyRingsItemDTO', 'SpanshSpanshBodyBeltsItemSignalsDTO', 'SpanshSpanshBodyBeltsItemDTO', 'SpanshSpanshBodyDTO')
