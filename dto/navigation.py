"""Presentation Data Transfer Objects (DTOs) for navigation and route planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

# Standard scoopable star spectral classes (KGBFOAM)
SCOOPABLE_STAR_CLASSES = frozenset({"K", "G", "B", "F", "O", "A", "M"})


@dataclass(frozen=True)
class RouteWaypointDto:
    """Represents a single jump hop in an active hyperspace route."""

    system_name: str
    star_class: str
    distance_ly: float | None = None
    is_scoopable: bool = False
    is_destination: bool = False


@dataclass(frozen=True)
class NavigationRouteDto:
    """Pure, immutable presentation DTO consumed by navigation widgets.

    Decoupled from raw journal events, network transport, and client instances.
    """

    destination_system: str
    star_class: str
    remaining_jumps: int
    is_route_active: bool = True
    current_system: str | None = None
    jump_distance_ly: float | None = None
    total_route_distance_ly: float | None = None
    is_scoopable: bool = False
    waypoints: list[RouteWaypointDto] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def create(
        cls,
        destination_system: str,
        star_class: str,
        remaining_jumps: int,
        current_system: str | None = None,
        jump_distance_ly: float | None = None,
        total_distance_ly: float | None = None,
        waypoints: list[RouteWaypointDto] | None = None,
    ) -> NavigationRouteDto:
        """Convenience constructor evaluating scoopability and status invariants."""
        clean_star_class = star_class.strip().upper()
        # Take first char if full name like 'A (Blue-White)'
        primary_spectral = clean_star_class[0] if clean_star_class else ""
        is_scoop = primary_spectral in SCOOPABLE_STAR_CLASSES

        return cls(
            destination_system=destination_system,
            star_class=star_class,
            remaining_jumps=remaining_jumps,
            is_route_active=remaining_jumps > 0,
            current_system=current_system,
            jump_distance_ly=jump_distance_ly,
            total_route_distance_ly=total_distance_ly,
            is_scoopable=is_scoop,
            waypoints=waypoints or [],
        )
