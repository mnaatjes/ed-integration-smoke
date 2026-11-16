"""Use case transforming ed-fleet-client telemetry streams into presentation DTOs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ed_fleet_client import EliteDangerousClient
from ed_fleet_client.core.domain.services.navigation import RouteProgressUpdated

from dto.navigation import NavigationRouteDto, RouteWaypointDto


class RouteTrackingUseCase:
    """Orchestrates route telemetry acquisition and maps game state to NavigationRouteDto.

    Decoupled from UI: emits DTOs via a listener callback callable[[NavigationRouteDto], None].
    """

    def __init__(
        self,
        client: EliteDangerousClient,
        on_dto_updated: Callable[[NavigationRouteDto], None] | None = None,
    ) -> None:
        self.client = client
        self._on_dto_updated = on_dto_updated
        self._current_dto: NavigationRouteDto | None = None
        self._subscriptions: list[Any] = []

    @property
    def current_dto(self) -> NavigationRouteDto | None:
        """The latest hydrated presentation DTO."""
        return self._current_dto

    def set_listener(self, on_dto_updated: Callable[[NavigationRouteDto], None]) -> None:
        """Register a callback invoked whenever a new DTO is produced."""
        self._on_dto_updated = on_dto_updated
        if self._current_dto is not None:
            self._on_dto_updated(self._current_dto)

    def attach(self) -> None:
        """Attach listeners to the ed-fleet-client event dispatcher and navigation service."""
        # Ensure underlying navigation service is attached
        self.client.navigation.attach()

        # Subscribe to derived RouteProgressUpdated events
        sub = self.client.subscribe(RouteProgressUpdated, self._handle_route_progress)
        self._subscriptions.append(sub)

        # Build initial projection if target is already locked
        self._refresh_from_state()

    def detach(self) -> None:
        """Unsubscribe from the client event bus."""
        for sub in self._subscriptions:
            self.client.unsubscribe(sub)
        self._subscriptions.clear()

    def _handle_route_progress(self, event: RouteProgressUpdated) -> None:
        """Transform RouteProgressUpdated event into a NavigationRouteDto."""
        current_loc = self.client.location.star_system or "Unknown System"
        dto = NavigationRouteDto.create(
            destination_system=event.destination_system,
            star_class=event.star_class,
            remaining_jumps=event.remaining_jumps,
            current_system=current_loc,
            jump_distance_ly=event.distance_ly,
            waypoints=[
                RouteWaypointDto(
                    system_name=event.destination_system,
                    star_class=event.star_class,
                    distance_ly=event.distance_ly,
                    is_destination=True,
                )
            ],
        )
        self._publish_dto(dto)

    def _refresh_from_state(self) -> None:
        """Poll navigation service state for initial target data."""
        nav = self.client.navigation
        target_sys = getattr(nav, "_fsd_target_system", None)
        if isinstance(target_sys, str) and target_sys:
            raw_remaining = getattr(nav, "_fsd_remaining_jumps", 1)
            remaining = int(raw_remaining) if isinstance(raw_remaining, int) else 1
            star_class = getattr(nav, "_fsd_star_class", "Unknown")
            dto = NavigationRouteDto.create(
                destination_system=target_sys,
                star_class=str(star_class),
                remaining_jumps=remaining,
                current_system=self.client.location.star_system,
            )
            self._publish_dto(dto)

    def _publish_dto(self, dto: NavigationRouteDto) -> None:
        self._current_dto = dto
        if self._on_dto_updated is not None:
            self._on_dto_updated(dto)
