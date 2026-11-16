"""Unit and pipeline integration tests for the discrete NavigationRouteCard."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from ed_fleet_client.core.domain.services.navigation import RouteProgressUpdated
from textual.app import App, ComposeResult

from dto.navigation import NavigationRouteDto
from use_cases.route_tracking import RouteTrackingUseCase
from widgets.nav_route import NavigationRouteCard


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


@pytest.mark.asyncio
async def test_discrete_navigation_route_card_rendering() -> None:
    """Verify isolated NavigationRouteCard renders and updates cleanly in headless Textual pilot."""
    initial_dto = NavigationRouteDto.create(
        destination_system="Maia",
        star_class="B",
        remaining_jumps=2,
        jump_distance_ly=34.2,
        current_system="Pleiades Sector",
    )

    class CardTestApp(App[None]):
        def __init__(self) -> None:
            super().__init__()
            self.card = NavigationRouteCard(initial_dto=initial_dto)

        def compose(self) -> ComposeResult:
            yield self.card

    app = CardTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.card._dto is not None
        assert app.card._dto.destination_system == "Maia"
        assert app.card._nixie_hops.current_value == "2"

        # Update discrete card with single hop remaining
        next_dto = NavigationRouteDto.create(
            destination_system="Maia",
            star_class="B",
            remaining_jumps=1,
            jump_distance_ly=14.2,
            current_system="Merope",
        )
        app.card.update_route(next_dto)
        assert app.card._dto.remaining_jumps == 1
        assert app.card._nixie_hops.current_value == "1"

        # Update discrete card with route completed
        done_dto = NavigationRouteDto.create(
            destination_system="Maia",
            star_class="B",
            remaining_jumps=0,
            current_system="Maia",
        )
        app.card.update_route(done_dto)
        assert app.card._dto.remaining_jumps == 0
        assert app.card._nixie_hops.current_value == "0"


def test_render_fsd_target_table() -> None:
    """Verify render_fsd_target_table formats Rich table correctly for states."""
    from dto.navigation import FsdTargetDto
    from widgets.fsd_target import render_fsd_target_table

    # 1. Unlocked state
    table_unlocked = render_fsd_target_table(None)
    assert table_unlocked.title == "FSD Target Lock"
    assert len(table_unlocked.columns) == 2

    # 2. Locked scoopable state
    dto = FsdTargetDto.create(
        system_name="Shinrarta Dezhra",
        star_class="A",
        remaining_jumps=3,
        system_address=3932277478106,
    )
    table_locked = render_fsd_target_table(dto)
    assert table_locked.title == "FSD Target Lock"
    assert dto.is_scoopable is True
