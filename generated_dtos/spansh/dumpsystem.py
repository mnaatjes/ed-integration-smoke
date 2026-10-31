"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshDumpSystemCoordsDTO:
    """Coordinates of the system."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemLandingpadsDTO:
    """Breakdown of the number of landing pads of the station."""

    large: int
    medium: int
    small: int


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemMarketCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemStationsItemMarketCommoditiesItemDTO."""

    name: str
    symbol: str
    category: str
    commodityId: int
    demand: int
    supply: int
    buyPrice: int
    sellPrice: int


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemMarketDTO:
    """Commodity market information about the station."""

    commodities: list[SpanshSpanshDumpSystemBodiesItemStationsItemMarketCommoditiesItemDTO]
    prohibitedCommodities: list[str]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemShipyardShipsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemStationsItemShipyardShipsItemDTO."""

    name: str
    symbol: str
    shipId: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemShipyardDTO:
    """Shipyard information about the station."""

    ships: list[SpanshSpanshDumpSystemBodiesItemStationsItemShipyardShipsItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingModulesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingModulesItemDTO."""

    name: str
    symbol: str
    moduleId: float
    class_: int
    rating: str
    category: str
    ship: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingDTO:
    """Outfitting information about the station."""

    modules: list[SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingModulesItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemStationsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemStationsItemDTO."""

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
    landingPads: SpanshSpanshDumpSystemBodiesItemStationsItemLandingpadsDTO | None = None
    carrierDockingAccess: str | None = None
    market: SpanshSpanshDumpSystemBodiesItemStationsItemMarketDTO | None = None
    shipyard: SpanshSpanshDumpSystemBodiesItemStationsItemShipyardDTO | None = None
    outfitting: SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemSignalsDTO:
    """Planets only.  The signals that can be found on the planet."""

    signals: dict[str, Any] | None = None
    updateTime: str | None = None
    genuses: list[str] | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemRingsItemSignalsDTO:
    """The signals that can be found within the belt or ring."""

    signals: dict[str, Any]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemRingsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemRingsItemDTO."""

    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float
    id64: int | None = None
    signals: SpanshSpanshDumpSystemBodiesItemRingsItemSignalsDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemBeltsItemSignalsDTO:
    """The signals that can be found within the belt or ring."""

    signals: dict[str, Any]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemBeltsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemBeltsItemDTO."""

    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float
    id64: int | None = None
    signals: SpanshSpanshDumpSystemBodiesItemBeltsItemSignalsDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemBodiesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemBodiesItemDTO."""

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
    stations: list[SpanshSpanshDumpSystemBodiesItemStationsItemDTO] | None = None
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
    signals: SpanshSpanshDumpSystemBodiesItemSignalsDTO | None = None
    reserveLevel: str | None = None
    rings: list[SpanshSpanshDumpSystemBodiesItemRingsItemDTO] | None = None
    belts: list[SpanshSpanshDumpSystemBodiesItemBeltsItemDTO] | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemLandingpadsDTO:
    """Breakdown of the number of landing pads of the station."""

    large: int
    medium: int
    small: int


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemMarketCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemStationsItemMarketCommoditiesItemDTO."""

    name: str
    symbol: str
    category: str
    commodityId: int
    demand: int
    supply: int
    buyPrice: int
    sellPrice: int


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemMarketDTO:
    """Commodity market information about the station."""

    commodities: list[SpanshSpanshDumpSystemStationsItemMarketCommoditiesItemDTO]
    prohibitedCommodities: list[str]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemShipyardShipsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemStationsItemShipyardShipsItemDTO."""

    name: str
    symbol: str
    shipId: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemShipyardDTO:
    """Shipyard information about the station."""

    ships: list[SpanshSpanshDumpSystemStationsItemShipyardShipsItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemOutfittingModulesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemStationsItemOutfittingModulesItemDTO."""

    name: str
    symbol: str
    moduleId: float
    class_: int
    rating: str
    category: str
    ship: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemOutfittingDTO:
    """Outfitting information about the station."""

    modules: list[SpanshSpanshDumpSystemStationsItemOutfittingModulesItemDTO]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshDumpSystemStationsItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemStationsItemDTO."""

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
    landingPads: SpanshSpanshDumpSystemStationsItemLandingpadsDTO | None = None
    carrierDockingAccess: str | None = None
    market: SpanshSpanshDumpSystemStationsItemMarketDTO | None = None
    shipyard: SpanshSpanshDumpSystemStationsItemShipyardDTO | None = None
    outfitting: SpanshSpanshDumpSystemStationsItemOutfittingDTO | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemControllingfactionActivestatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemControllingfactionActivestatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemControllingfactionPendingstatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemControllingfactionPendingstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemControllingfactionRecoveringstatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemControllingfactionRecoveringstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemControllingfactionDTO:
    """Full faction state"""

    name: str
    state: Any | None = None
    allegiance: Any | None = None
    government: Any | None = None
    influence: float | None = None
    activeStates: list[SpanshSpanshDumpSystemControllingfactionActivestatesItemDTO] | None = None
    pendingStates: list[SpanshSpanshDumpSystemControllingfactionPendingstatesItemDTO] | None = None
    recoveringStates: list[SpanshSpanshDumpSystemControllingfactionRecoveringstatesItemDTO] | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemFactionsItemActivestatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemFactionsItemActivestatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemFactionsItemPendingstatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemFactionsItemPendingstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemFactionsItemRecoveringstatesItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemFactionsItemRecoveringstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemFactionsItemDTO:
    """Full faction state"""

    name: str
    state: Any | None = None
    allegiance: Any | None = None
    government: Any | None = None
    influence: float | None = None
    activeStates: list[SpanshSpanshDumpSystemFactionsItemActivestatesItemDTO] | None = None
    pendingStates: list[SpanshSpanshDumpSystemFactionsItemPendingstatesItemDTO] | None = None
    recoveringStates: list[SpanshSpanshDumpSystemFactionsItemRecoveringstatesItemDTO] | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemPowerconflictprogressItemDTO:
    """Data transfer object for SpanshSpanshDumpSystemPowerconflictprogressItemDTO."""

    power: Any
    progress: float


@dataclass(frozen=True)
class SpanshSpanshDumpSystemThargoidwarDTO:
    """State of the Thargoid war in this system."""

    currentState: Any | None = None
    successState: Any | None = None
    failureState: Any | None = None
    progress: float | None = None
    daysRemaining: float | None = None
    portsRemaining: float | None = None
    successReached: bool | None = None


@dataclass(frozen=True)
class SpanshSpanshDumpSystemDTO:
    """Spansh DumpSystem contract."""

    id64: int
    name: str
    coords: SpanshSpanshDumpSystemCoordsDTO
    date: str
    bodies: list[SpanshSpanshDumpSystemBodiesItemDTO]
    allegiance: Any | None = None
    government: Any | None = None
    primaryEconomy: Any | None = None
    secondaryEconomy: Any | None = None
    security: str | None = None
    population: int | None = None
    bodyCount: int | None = None
    stations: list[SpanshSpanshDumpSystemStationsItemDTO] | None = None
    controllingFaction: SpanshSpanshDumpSystemControllingfactionDTO | None = None
    factions: list[SpanshSpanshDumpSystemFactionsItemDTO] | None = None
    powerState: Any | None = None
    powerConflictProgress: list[SpanshSpanshDumpSystemPowerconflictprogressItemDTO] | None = None
    powers: list[Any] | None = None
    timestamps: dict[str, Any] | None = None
    controllingPower: Any | None = None
    powerStateControlProgress: Any | None = None
    powerStateReinforcement: Any | None = None
    powerStateUndermining: Any | None = None
    thargoidWar: SpanshSpanshDumpSystemThargoidwarDTO | None = None

__all__ = ('SpanshSpanshDumpSystemCoordsDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemLandingpadsDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemMarketCommoditiesItemDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemMarketDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemShipyardShipsItemDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemShipyardDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingModulesItemDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemOutfittingDTO', 'SpanshSpanshDumpSystemBodiesItemStationsItemDTO', 'SpanshSpanshDumpSystemBodiesItemSignalsDTO', 'SpanshSpanshDumpSystemBodiesItemRingsItemSignalsDTO', 'SpanshSpanshDumpSystemBodiesItemRingsItemDTO', 'SpanshSpanshDumpSystemBodiesItemBeltsItemSignalsDTO', 'SpanshSpanshDumpSystemBodiesItemBeltsItemDTO', 'SpanshSpanshDumpSystemBodiesItemDTO', 'SpanshSpanshDumpSystemStationsItemLandingpadsDTO', 'SpanshSpanshDumpSystemStationsItemMarketCommoditiesItemDTO', 'SpanshSpanshDumpSystemStationsItemMarketDTO', 'SpanshSpanshDumpSystemStationsItemShipyardShipsItemDTO', 'SpanshSpanshDumpSystemStationsItemShipyardDTO', 'SpanshSpanshDumpSystemStationsItemOutfittingModulesItemDTO', 'SpanshSpanshDumpSystemStationsItemOutfittingDTO', 'SpanshSpanshDumpSystemStationsItemDTO', 'SpanshSpanshDumpSystemControllingfactionActivestatesItemDTO', 'SpanshSpanshDumpSystemControllingfactionPendingstatesItemDTO', 'SpanshSpanshDumpSystemControllingfactionRecoveringstatesItemDTO', 'SpanshSpanshDumpSystemControllingfactionDTO', 'SpanshSpanshDumpSystemFactionsItemActivestatesItemDTO', 'SpanshSpanshDumpSystemFactionsItemPendingstatesItemDTO', 'SpanshSpanshDumpSystemFactionsItemRecoveringstatesItemDTO', 'SpanshSpanshDumpSystemFactionsItemDTO', 'SpanshSpanshDumpSystemPowerconflictprogressItemDTO', 'SpanshSpanshDumpSystemThargoidwarDTO', 'SpanshSpanshDumpSystemDTO')
