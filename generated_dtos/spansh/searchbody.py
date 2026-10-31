"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchBodySynthesisRecipesItemDTO:
    """Data transfer object for SpanshSpanshSearchBodySynthesisRecipesItemDTO."""

    name: Any
    level: Any


@dataclass(frozen=True)
class SpanshSpanshSearchBodyLandmarksItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyLandmarksItemDTO."""

    id: int
    type: Any
    latitude: float
    longitude: float
    value: int
    subtype: Any | None = None
    variant: Any | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchBodyParentsItemDTO:
    """Data transfer object for SpanshSpanshSearchBodyParentsItemDTO."""

    type: str
    id64: int
    subtype: Any | None = None


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
    type: Any
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
    terraforming_state: Any | None = None
    is_main_star: bool | None = None
    spectral_class: Any | None = None
    luminosity_class: Any | None = None
    volcanism_type: Any | None = None
    reserve_level: Any | None = None
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
    materials: Any | None = None
    synthesis_recipes: list[SpanshSpanshSearchBodySynthesisRecipesItemDTO] | None = None
    signals: Any | None = None
    signal_count: int | None = None
    signals_updated_at: str | None = None
    genuses: Any | None = None
    solid_composition: Any | None = None
    atmosphere_composition: Any | None = None
    rings: list[Any] | None = None
    belts: list[Any] | None = None
    landmarks: list[SpanshSpanshSearchBodyLandmarksItemDTO] | None = None
    landmark_value: int | None = None
    parents: list[SpanshSpanshSearchBodyParentsItemDTO] | None = None
    stations: list[Any] | None = None

__all__ = ('SpanshSpanshSearchBodySynthesisRecipesItemDTO', 'SpanshSpanshSearchBodyLandmarksItemDTO', 'SpanshSpanshSearchBodyParentsItemDTO', 'SpanshSpanshSearchBodyDTO')
