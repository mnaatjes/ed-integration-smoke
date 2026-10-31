"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchSystemMinorFactionPresencesItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemMinorFactionPresencesItemDTO."""

    name: str
    allegiance: Any | None = None
    government: Any | None = None
    state: Any | None = None
    influence: float | None = None
    active_states: list[Any] | None = None
    pending_states: list[Any] | None = None
    recovering_states: list[Any] | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchSystemPowerConflictProgressItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemPowerConflictProgressItemDTO."""

    power: Any
    progress: float


@dataclass(frozen=True)
class SpanshSpanshSearchSystemSynthesisRecipesItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemSynthesisRecipesItemDTO."""

    name: str
    level: str


@dataclass(frozen=True)
class SpanshSpanshSearchSystemBodiesItemLandmarksItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemBodiesItemLandmarksItemDTO."""

    type: str
    count: int
    value: int
    subtype: str | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchSystemBodiesItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemBodiesItemDTO."""

    id: int
    id64: int
    name: str
    type: str
    is_main_star: Any
    distance_to_arrival: float
    estimated_scan_value: int
    estimated_mapping_value: int
    subtype: Any | None = None
    terraforming_state: str | None = None
    landmarks: list[SpanshSpanshSearchSystemBodiesItemLandmarksItemDTO] | None = None
    landmark_value: int | None = None


@dataclass(frozen=True)
class SpanshSpanshSearchSystemStationsItemDTO:
    """Data transfer object for SpanshSpanshSearchSystemStationsItemDTO."""

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
class SpanshSpanshSearchSystemDTO:
    """Spansh SearchSystem contract."""

    id64: int
    name: str
    x: float
    y: float
    z: float
    population: int
    needs_permit: bool
    known_permit: bool
    nearest_populated_distance: float | None = None
    nearest_populated_id64: int | None = None
    updated_at: str | None = None
    region: str | None = None
    government: Any | None = None
    allegiance: Any | None = None
    state: Any | None = None
    security: str | None = None
    primary_economy: Any | None = None
    secondary_economy: Any | None = None
    controlling_minor_faction: Any | None = None
    controlling_minor_faction_state: Any | None = None
    is_colonised: bool | None = None
    is_being_colonised: bool | None = None
    controlling_power: Any | None = None
    power: list[Any] | None = None
    power_state_control_progress: float | None = None
    power_state_reinforcement: int | None = None
    power_state_undermining: int | None = None
    minor_faction_presences: list[SpanshSpanshSearchSystemMinorFactionPresencesItemDTO] | None = None
    power_conflict_progress: list[SpanshSpanshSearchSystemPowerConflictProgressItemDTO] | None = None
    power_state: Any | None = None
    synthesis_recipes: list[SpanshSpanshSearchSystemSynthesisRecipesItemDTO] | None = None
    body_count: int | None = None
    bodies: list[SpanshSpanshSearchSystemBodiesItemDTO] | None = None
    stations: list[SpanshSpanshSearchSystemStationsItemDTO] | None = None
    thargoid_war_state: Any | None = None
    thargoid_war_failure_state: Any | None = None
    thargoid_war_success_state: Any | None = None
    thargoid_war_success_reached: bool | None = None
    thargoid_war_progress: float | None = None
    thargoid_war_days_remaining: float | None = None
    thargoid_war_ports_remaining: float | None = None
    estimated_scan_value: int | None = None
    estimated_mapping_value: int | None = None
    landmark_value: int | None = None

__all__ = ('SpanshSpanshSearchSystemMinorFactionPresencesItemDTO', 'SpanshSpanshSearchSystemPowerConflictProgressItemDTO', 'SpanshSpanshSearchSystemSynthesisRecipesItemDTO', 'SpanshSpanshSearchSystemBodiesItemLandmarksItemDTO', 'SpanshSpanshSearchSystemBodiesItemDTO', 'SpanshSpanshSearchSystemStationsItemDTO', 'SpanshSpanshSearchSystemDTO')
