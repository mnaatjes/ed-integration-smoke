"""Workbench slot definition for NavigationRouteCard discrete Textual component."""

from __future__ import annotations

from typing import Any

from ed_fleet_client import EliteDangerousClient

from dto.navigation import NavigationRouteDto
from use_cases.route_tracking import RouteTrackingUseCase
from widgets.nav_route import NavigationRouteCard
from workbench.registry import ComponentKind, ComponentSlot, register_slot


def _build_mock_nav_route() -> NavigationRouteDto:
    return NavigationRouteDto.create(
        destination_system="Sol",
        star_class="G (Yellow Dwarf)",
        remaining_jumps=2,
        current_system="Shinrarta Dezhra",
        jump_distance_ly=24.89,
        total_distance_ly=48.20,
    )


def _connect_live_nav_route(
    client: EliteDangerousClient,
    on_update: Any,
) -> Any:
    use_case = RouteTrackingUseCase(client, on_dto_updated=on_update)
    use_case.attach()
    return use_case


NAV_ROUTE_SLOT = ComponentSlot(
    name="nav-route",
    description="Discrete Textual card rendering route origin/dest, next hop, and nixie jumps.",
    kind=ComponentKind.TEXTUAL,
    mock_factory=_build_mock_nav_route,
    live_connector=_connect_live_nav_route,
    widget_factory=lambda dto: NavigationRouteCard(initial_dto=dto),
    tags=["navigation", "textual", "cassette-futurism"],
)

register_slot(NAV_ROUTE_SLOT)
