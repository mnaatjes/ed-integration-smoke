"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchStationServicesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationServicesItemDTO."""

    name: str


@dataclass(frozen=True)
class SpanshSpanshSearchStationEconomiesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationEconomiesItemDTO."""

    name: Any
    share: float


@dataclass(frozen=True)
class SpanshSpanshSearchStationExportCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationExportCommoditiesItemDTO."""

    name: str


@dataclass(frozen=True)
class SpanshSpanshSearchStationProhibitedCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationProhibitedCommoditiesItemDTO."""

    name: str


@dataclass(frozen=True)
class SpanshSpanshSearchStationImportCommoditiesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationImportCommoditiesItemDTO."""

    name: str


@dataclass(frozen=True)
class SpanshSpanshSearchStationShipsItemDTO:
    """Data transfer object for SpanshSpanshSearchStationShipsItemDTO."""

    name: str
    symbol: str
    price: int | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchStationModulesItemDTO:
    """Data transfer object for SpanshSpanshSearchStationModulesItemDTO."""

    name: str
    category: str
    class_: int
    rating: str
    ed_symbol: str
    mass: int | None = None
    power: int | None = None
    price: int | None = None
    weapon_mode: str | None = None
    ship: str | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchStationMarketItemDTO:
    """Data transfer object for SpanshSpanshSearchStationMarketItemDTO."""

    commodity: str
    category: str
    supply: int
    demand: int
    buy_price: int
    sell_price: int
    is_rare: bool | None = None
    is_home_station: bool | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchStationDTO:
    """Spansh SearchStation contract."""

    market_id: int
    system_name: str
    system_id64: int
    system_x: float
    system_y: float
    system_z: float
    is_planetary: bool
    name: str
    has_large_pad: bool
    system_is_colonised: bool | None = None
    system_is_being_colonised: bool | None = None
    system_power: list[Any] | None = None
    system_controlling_power: Any | None = None
    system_power_state: Any | None = None
    system_primary_economy: Any | None = None
    system_secondary_economy: Any | None = None
    system_population: int | None = None
    updated_at: str | None = None
    body_id64: int | None = None
    body_name: str | None = None
    body_type: str | None = None
    body_subtype: Any | None = None
    body_gravity: float | None = None
    body_has_atmosphere: bool | None = None
    body_has_rings: bool | None = None
    carrier_name: str | None = None
    real_name: str | None = None
    allegiance: Any | None = None
    government: Any | None = None
    services: list[SpanshSpanshSearchStationServicesItemDTO] | None = None
    has_market: bool | None = None
    has_shipyard: bool | None = None
    has_outfitting: bool | None = None
    is_dssa_carrier: bool | None = None
    large_pads: int | None = None
    medium_pads: int | None = None
    small_pads: int | None = None
    type: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_to_arrival: float | None = None
    controlling_minor_faction: str | None = None
    controlling_minor_faction_state: str | None = None
    controlling_minor_faction_influence: float | None = None
    carrier_docking_access: str | None = None
    primary_economy: Any | None = None
    secondary_economy: Any | None = None
    economies: list[SpanshSpanshSearchStationEconomiesItemDTO] | None = None
    export_commodities: list[SpanshSpanshSearchStationExportCommoditiesItemDTO] | None = None
    prohibited_commodities: list[SpanshSpanshSearchStationProhibitedCommoditiesItemDTO] | None = None
    import_commodities: list[SpanshSpanshSearchStationImportCommoditiesItemDTO] | None = None
    shipyard_updated_at: str | None = None
    ships: list[SpanshSpanshSearchStationShipsItemDTO] | None = None
    outfitting_updated_at: str | None = None
    modules: list[SpanshSpanshSearchStationModulesItemDTO] | None = None
    market_updated_at: str | None = None
    market: list[SpanshSpanshSearchStationMarketItemDTO] | None = None
    material_trader: Any | None = None
    technology_broker: Any | None = None

__all__ = ('SpanshSpanshSearchStationServicesItemDTO', 'SpanshSpanshSearchStationEconomiesItemDTO', 'SpanshSpanshSearchStationExportCommoditiesItemDTO', 'SpanshSpanshSearchStationProhibitedCommoditiesItemDTO', 'SpanshSpanshSearchStationImportCommoditiesItemDTO', 'SpanshSpanshSearchStationShipsItemDTO', 'SpanshSpanshSearchStationModulesItemDTO', 'SpanshSpanshSearchStationMarketItemDTO', 'SpanshSpanshSearchStationDTO')
