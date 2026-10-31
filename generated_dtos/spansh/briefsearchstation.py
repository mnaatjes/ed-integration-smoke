"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshBriefSearchStationDTO:
    """Spansh BriefSearchStation contract."""

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
    type: Any | None = None
    services: list[Any] | None = None
    controlling_minor_faction: str | None = None
    controlling_minor_faction_state: str | None = None

__all__ = ('SpanshSpanshBriefSearchStationDTO',)
