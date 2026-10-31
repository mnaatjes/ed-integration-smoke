"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchBodyMaterialsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyMaterialsItemDTO."""

    name: str
    share: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodySynthesisRecipesItemDTO:
    """Data transfer object for SpanshSpanshSearchBodySynthesisRecipesItemDTO."""

    name: str
    level: str


@dataclass(frozen=True)
class SpanshSpanshSearchBodySignalsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodySignalsItemDTO."""

    name: str
    count: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodyGenusesItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyGenusesItemDTO."""

    name: str


@dataclass(frozen=True)
class SpanshSpanshSearchBodySolidCompositionItemDTO:
    """Data transfer object for SpanshSpanshSearchBodySolidCompositionItemDTO."""

    name: str
    share: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodyAtmosphereCompositionItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyAtmosphereCompositionItemDTO."""

    name: str
    share: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodyRingsItemSignalsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyRingsItemSignalsItemDTO."""

    name: str
    count: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodyRingsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyRingsItemDTO."""

    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float
    signals: list[SpanshSpanshSearchBodyRingsItemSignalsItemDTO] | None = None
    signal_count: int | None = None
    signals_updated_at: str | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchBodyBeltsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyBeltsItemDTO."""

    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float


@dataclass(frozen=True)
class SpanshSpanshSearchBodyLandmarksItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyLandmarksItemDTO."""

    id: int
    type: str
    latitude: float
    longitude: float
    value: int
    subtype: str | None = None
    variant: str | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchBodyParentsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyParentsItemDTO."""

    type: str
    id64: int
    subtype: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchBodyStationsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyStationsItemDTO."""

    market_id: int
    name: str
    has_large_pad: bool
    body_id64: int | None = None
    body_name: str | None = None
    distance_to_arrival: float | None = None
    has_market: bool | None = None
    has_shipyard: bool | None = None
    has_outfitting: bool | None = None
    is_dssa_carrier: bool | None = None
    large_pads: int | None = None
    medium_pads: int | None = None
    small_pads: int | None = None
    type: str | None = None
    services: list[str] | None = None
    controlling_minor_faction: str | None = None
    controlling_minor_faction_state: str | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchBodyDTO:
    """Spansh SearchBody contract."""

    id64: int
    system_name: str
    system_id64: int
    system_x: float
    system_y: float
    system_z: float
    name: str
    type: str
    distance_to_arrival: float
    atmosphere: Any
    estimated_scan_value: int
    estimated_mapping_value: int
    body_id: int | None = None
    system_region: str | None = None
    updated_at: str | None = None
    system_controlling_power: Any | None = None
    system_power_state: Any | None = None
    subtype: Any | None = None
    terraforming_state: str | None = None
    is_main_star: Any | None = None
    spectral_class: Any | None = None
    luminosity_class: str | None = None
    volcanism_type: str | None = None
    reserve_level: str | None = None
    surface_temperature: float | None = None
    age: int | None = None
    solar_masses: float | None = None
    solar_radius: float | None = None
    earth_masses: float | None = None
    radius: float | None = None
    gravity: float | None = None
    surface_pressure: float | None = None
    orbital_period: float | None = None
    semi_major_axis: float | None = None
    orbital_eccentricity: float | None = None
    orbital_inclination: float | None = None
    arg_of_periapsis: float | None = None
    mean_anomaly: float | None = None
    ascending_node: float | None = None
    rotational_period: float | None = None
    is_rotational_period_tidally_locked: bool | None = None
    axis_tilt: float | None = None
    is_landable: bool | None = None
    orbital_synchronicity: float | None = None
    materials: list[SpanshSpanshSearchBodyMaterialsItemDTO] | None = None
    synthesis_recipes: list[SpanshSpanshSearchBodySynthesisRecipesItemDTO] | None = None
    signals: list[SpanshSpanshSearchBodySignalsItemDTO] | None = None
    signal_count: int | None = None
    signals_updated_at: str | None = None
    genuses: list[SpanshSpanshSearchBodyGenusesItemDTO] | None = None
    solid_composition: list[SpanshSpanshSearchBodySolidCompositionItemDTO] | None = None
    atmosphere_composition: list[SpanshSpanshSearchBodyAtmosphereCompositionItemDTO] | None = None
    rings: list[SpanshSpanshSearchBodyRingsItemDTO] | None = None
    belts: list[SpanshSpanshSearchBodyBeltsItemDTO] | None = None
    landmarks: list[SpanshSpanshSearchBodyLandmarksItemDTO] | None = None
    landmark_value: int | None = None
    parents: list[SpanshSpanshSearchBodyParentsItemDTO] | None = None
    stations: list[SpanshSpanshSearchBodyStationsItemDTO] | None = None

__all__ = ('SpanshSpanshSearchBodyMaterialsItemDTO', 'SpanshSpanshSearchBodySynthesisRecipesItemDTO', 'SpanshSpanshSearchBodySignalsItemDTO', 'SpanshSpanshSearchBodyGenusesItemDTO', 'SpanshSpanshSearchBodySolidCompositionItemDTO', 'SpanshSpanshSearchBodyAtmosphereCompositionItemDTO', 'SpanshSpanshSearchBodyRingsItemSignalsItemDTO', 'SpanshSpanshSearchBodyRingsItemDTO', 'SpanshSpanshSearchBodyBeltsItemDTO', 'SpanshSpanshSearchBodyLandmarksItemDTO', 'SpanshSpanshSearchBodyParentsItemDTO', 'SpanshSpanshSearchBodyStationsItemDTO', 'SpanshSpanshSearchBodyDTO')
