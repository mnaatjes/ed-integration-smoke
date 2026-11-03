"""Data models for the in-game mission itinerary and guidance copilot."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WaypointType(StrEnum):
    """Categorization of where an action takes place."""

    CARRIER = "carrier"
    COCKPIT = "cockpit"
    LOCAL_SPACE = "local_space"
    PLANETARY_SURFACE = "planetary_surface"
    STAR_SYSTEM = "star_system"
    STATION = "station"


@dataclass(frozen=True, slots=True)
class PlayerContext:
    """Current player galactic and operational context resolved from telemetry."""

    system: str = "Unknown System"
    station: str = ""
    body: str = ""
    carrier_name: str = ""
    carrier_callsign: str = ""
    ship_type: str = "Unknown Ship"
    ship_name: str = ""
    is_docked: bool = False
    is_landed: bool = False


@dataclass(frozen=True, slots=True)
class ItineraryStep:
    """An individual actionable task guiding the commander to achieve an audit target."""

    target_id: str
    chapter: str
    phase: str
    title: str
    instruction: str
    waypoint_type: WaypointType
    waypoint_name: str
    action_hint: str
    priority: int = 100
