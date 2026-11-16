"""Showcase script demonstrating the decoupled use_case -> DTO -> widget architecture."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

# Ensure workspace root is in sys.path when executed directly
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import typer  # noqa: E402
from ed_ui_cli.themes import CASSETTE_FUTURISM_THEME  # noqa: E402
from ed_ui_cli.tui.app import TelemetryConsoleApp  # noqa: E402
from rich.console import Console  # noqa: E402

from dto.navigation import NavigationRouteDto, RouteWaypointDto  # noqa: E402
from widgets.nav_route import NavigationRouteWidget  # noqa: E402

app = typer.Typer(help="Showcase the decoupled navigation use-case -> DTO -> widget architecture.")


def _build_mock_route_dto() -> NavigationRouteDto:
    """Construct a mock presentation DTO matching a multi-hop route."""
    waypoints = [
        RouteWaypointDto(
            system_name="Shinrarta Dezhra",
            star_class="A (Blue-White)",
            distance_ly=24.89,
            is_scoopable=True,
            is_destination=False,
        ),
        RouteWaypointDto(
            system_name="LHS 3006",
            star_class="M (Red Dwarf)",
            distance_ly=19.42,
            is_scoopable=True,
            is_destination=False,
        ),
        RouteWaypointDto(
            system_name="Sol",
            star_class="G (Yellow Dwarf)",
            distance_ly=15.11,
            is_scoopable=True,
            is_destination=True,
        ),
    ]

    return NavigationRouteDto.create(
        destination_system="Sol",
        star_class="G",
        remaining_jumps=3,
        current_system="Founders World (Jameson Memorial)",
        jump_distance_ly=24.89,
        total_distance_ly=59.42,
        waypoints=waypoints,
    )


def _launch_nav_tui_showcase() -> None:
    """Launch full-screen Textual application hosting NavigationRouteWidget."""
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll
    from textual.widgets import Footer, Header, Label, TabbedContent, TabPane

    class NavigationShowcaseApp(TelemetryConsoleApp):
        """Application demonstrating the decoupled NavigationRouteWidget."""

        def compose(self):  # type: ignore[no-untyped-def]
            yield Header(show_clock=True)
            with Container(id="console-top-row"):
                yield Label(id="connection-label")
                yield self.fuzzy_search
            with Horizontal(id="console-middle"):
                with Vertical(id="nav-sidebar"):
                    yield Label("TELEMETRY CHANNELS", classes="section-title")
                    yield self.mode_selector
                    yield self.cartography_tree
                with Vertical(id="main-viewport"):
                    with TabbedContent():
                        with TabPane("Route Computer", id="tab-route"):
                            with VerticalScroll():
                                yield self.nav_widget
                        with TabPane("Raw Stream Log", id="tab-stream"):
                            yield self.data_table
                with Vertical(id="controls-sidebar"):
                    yield Label("STREAM POWER", classes="section-title")
                    yield self.stream_switch
                    yield Label("TRIGGERS", classes="section-title")
                    yield self.btn_poll
                    yield self.btn_reconnect
                    yield self.btn_clear
            yield Footer()

        def __init__(self) -> None:
            super().__init__(
                title="Cockpit Navigation Subsystem (Decoupled DTO Architecture)",
                theme=CASSETTE_FUTURISM_THEME,
            )
            mock_dto = _build_mock_route_dto()
            self.nav_widget = NavigationRouteWidget(initial_dto=mock_dto)

        def on_mount(self) -> None:
            super().on_mount()
            self.update_connection_status(is_connected=True, latency_ms=1.8)
            self.stream_switch.value = True

    app_instance = NavigationShowcaseApp()
    app_instance.run()


@app.command()
def main(
    static_dto: Annotated[
        bool,
        typer.Option(
            "--dto",
            "-d",
            help="Print generated mock NavigationRouteDto to console without launching TUI.",
        ),
    ] = False,
) -> None:
    """Preview the decoupled navigation route computer widget."""
    console = Console()
    if static_dto:
        dto = _build_mock_route_dto()
        console.print("[bold yellow]Constructed NavigationRouteDto:[/bold yellow]")
        console.print(dto)
    else:
        console.print("[dim]Launching Cockpit Navigation Computer... (Ctrl+C to quit)[/dim]")
        _launch_nav_tui_showcase()


if __name__ == "__main__":
    app()
