"""Showcase script displaying the isolated discrete NavigationRouteCard."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

# Ensure workspace root is in sys.path when executed directly
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import typer  # noqa: E402
from ed_fleet_client import create_client  # noqa: E402
from ed_fleet_client.adapters.driven.telemetry_http.models import (  # noqa: E402
    TelemetryConnectionConfig,
)
from ed_ui_cli.themes import CASSETTE_FUTURISM_THEME  # noqa: E402
from rich.console import Console  # noqa: E402
from textual.app import App, ComposeResult  # noqa: E402
from textual.containers import Center, Middle  # noqa: E402

from dto.navigation import NavigationRouteDto  # noqa: E402
from use_cases.route_tracking import RouteTrackingUseCase  # noqa: E402
from widgets.nav_route import NavigationRouteCard  # noqa: E402

app = typer.Typer(help="Showcase the discrete NavigationRouteCard widget in isolation.")


def _build_mock_route_dto() -> NavigationRouteDto:
    """Construct a mock presentation DTO for an active 3-hop route."""
    return NavigationRouteDto.create(
        destination_system="Sol",
        star_class="G",
        remaining_jumps=3,
        current_system="Shinrarta Dezhra",
        jump_distance_ly=24.89,
        total_distance_ly=59.42,
    )


def _launch_discrete_widget_preview(
    live: bool = False,
    host: str = "192.168.1.214",
    port: int = 8080,
) -> None:
    """Launch minimal Textual harness hosting only the discrete NavigationRouteCard."""

    class DiscreteCardPreviewApp(App[None]):
        """Minimal harness displaying ONLY the discrete card centered in the viewport."""

        CSS = """
        Screen {
            align: center middle;
            background: #111417;
        }
        #card-wrapper {
            width: 72;
            height: auto;
        }
        """

        def __init__(self) -> None:
            super().__init__()
            initial_dto = None if live else _build_mock_route_dto()
            self.card = NavigationRouteCard(initial_dto=initial_dto)
            self._client: Any = None
            self._use_case: RouteTrackingUseCase | None = None

        def on_mount(self) -> None:
            self.register_theme(CASSETTE_FUTURISM_THEME.to_textual_theme())
            self.theme = CASSETTE_FUTURISM_THEME.name

            if live:
                self.run_worker(self._connect_live_stream(), exclusive=True)

        async def _connect_live_stream(self) -> None:
            """Connect to live ed-telemetry server and stream route updates."""
            cfg = TelemetryConnectionConfig(host=host, port=port)
            self._client = create_client(cfg)

            def _on_update(dto: NavigationRouteDto) -> None:
                self.call_from_thread(self.card.update_route, dto)

            self._use_case = RouteTrackingUseCase(self._client, on_dto_updated=_on_update)
            self._use_case.attach()

            try:
                await self._client.connect()
            except Exception as exc:
                self.notify(f"Stream error: {exc}", severity="error")

        def compose(self) -> ComposeResult:
            with Center():
                with Middle(id="card-wrapper"):
                    yield self.card

    app_instance = DiscreteCardPreviewApp()
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
    live: Annotated[
        bool,
        typer.Option(
            "--live",
            "-l",
            help="Connect to live ed-telemetry server instead of using mock route fixture.",
        ),
    ] = False,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Telemetry server host (when --live is used).",
        ),
    ] = "192.168.1.214",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Telemetry server port (when --live is used).",
        ),
    ] = 8080,
) -> None:
    """Preview the discrete NavigationRouteCard widget."""
    console = Console()
    if static_dto:
        dto = _build_mock_route_dto()
        console.print("[bold yellow]Constructed NavigationRouteDto:[/bold yellow]")
        console.print(dto)
    else:
        mode = f"LIVE ({host}:{port})" if live else "MOCK FIXTURE"
        console.print(
            f"[dim]Launching NavigationRouteCard preview [{mode}]... (Ctrl+C to quit)[/dim]"
        )
        _launch_discrete_widget_preview(live=live, host=host, port=port)


if __name__ == "__main__":
    app()
