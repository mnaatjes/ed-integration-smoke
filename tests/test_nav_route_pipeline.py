"""Unit and pipeline integration tests for the decoupled navigation route pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from ed_fleet_client.core.domain.services.navigation import RouteProgressUpdated
from textual.app import App, ComposeResult

from dto.navigation import NavigationRouteDto, RouteWaypointDto
from use_cases.route_tracking import RouteTrackingUseCase
from widgets.nav_route import NavigationRouteWidget


def test_dto_invariants_and_scoopable_detection() -> None:
    """Verify NavigationRouteDto scoopable classification and distance invariants."""
    dto_scoop = NavigationRouteDto.create(
        destination_system="Sol",
        star_class="G (Yellow Dwarf)",
        remaining_jumps=2,
        jump_distance_ly=15.4,
    )
    assert dto_scoop.is_scoopable is True
    assert dto_scoop.is_route_active is True
    assert dto_scoop.destination_system == "Sol"

    dto_non_scoop = NavigationRouteDto.create(
        destination_system="Wolf 359",
        star_class="T Tauri",
        remaining_jumps=1,
    )
    assert dto_non_scoop.is_scoopable is False
    assert dto_non_scoop.is_route_active is True

    # Completed route
    dto_done = NavigationRouteDto.create(
        destination_system="Sol",
        star_class="G",
        remaining_jumps=0,
    )
    assert dto_done.is_route_active is False


def test_route_tracking_use_case_publishes_dto() -> None:
    """Verify RouteTrackingUseCase receives fleet client events and emits valid DTO."""
    mock_client = MagicMock()
    mock_client.location.star_system = "Shinrarta Dezhra"

    published_dtos: list[NavigationRouteDto] = []

    def _listener(dto: NavigationRouteDto) -> None:
        published_dtos.append(dto)

    use_case = RouteTrackingUseCase(mock_client, on_dto_updated=_listener)
    use_case.attach()

    # Simulate arrival of RouteProgressUpdated event from client bus
    event = RouteProgressUpdated(
        destination_system="Sol",
        star_class="G",
        remaining_jumps=4,
        distance_ly=12.5,
    )
    use_case._handle_route_progress(event)

    assert len(published_dtos) == 1
    dto = published_dtos[0]
    assert dto.destination_system == "Sol"
    assert dto.star_class == "G"
    assert dto.remaining_jumps == 4
    assert dto.current_system == "Shinrarta Dezhra"
    assert dto.is_scoopable is True
    assert dto.is_route_active is True
    assert len(dto.waypoints) == 1
    assert dto.waypoints[0].is_destination is True


@pytest.mark.asyncio
async def test_navigation_route_widget_headless_rendering() -> None:
    """Verify NavigationRouteWidget renders and updates cleanly in headless Textual test harness."""
    initial_dto = NavigationRouteDto.create(
        destination_system="Maia",
        star_class="B",
        remaining_jumps=2,
        jump_distance_ly=34.2,
        waypoints=[
            RouteWaypointDto("Pleiades Sector", "M", 20.0, is_scoopable=True),
            RouteWaypointDto("Maia", "B", 14.2, is_scoopable=True, is_destination=True),
        ],
    )

    class WidgetTestApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.widget = NavigationRouteWidget(initial_dto=initial_dto)

        def compose(self) -> ComposeResult:
            yield self.widget

    app = WidgetTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.widget._dto is not None
        assert app.widget._dto.destination_system == "Maia"
        assert app.widget._nixie_hops.current_value == "2"

        # Update widget with new DTO (hop completed)
        next_dto = NavigationRouteDto.create(
            destination_system="Maia",
            star_class="B",
            remaining_jumps=1,
            jump_distance_ly=14.2,
        )
        app.widget.update_route(next_dto)
        assert app.widget._dto.remaining_jumps == 1
        assert app.widget._nixie_hops.current_value == "1"
