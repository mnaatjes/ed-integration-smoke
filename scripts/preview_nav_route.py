"""Showcase script displaying the isolated discrete NavigationRouteCard."""

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
from rich.console import Console  # noqa: E402
from textual.app import App, ComposeResult  # noqa: E402
from textual.containers import Center, Middle  # noqa: E402

from dto.navigation import NavigationRouteDto  # noqa: E402
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


def _launch_discrete_widget_preview() -> None:
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

        def on_mount(self) -> None:
            self.register_theme(CASSETTE_FUTURISM_THEME.to_textual_theme())
            self.theme = CASSETTE_FUTURISM_THEME.name

        def compose(self) -> ComposeResult:
            with Center():
                with Middle(id="card-wrapper"):
                    yield NavigationRouteCard(initial_dto=_build_mock_route_dto())

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
) -> None:
    """Preview the discrete NavigationRouteCard widget."""
    console = Console()
    if static_dto:
        dto = _build_mock_route_dto()
        console.print("[bold yellow]Constructed NavigationRouteDto:[/bold yellow]")
        console.print(dto)
    else:
        console.print(
            "[dim]Launching discrete NavigationRouteCard preview... (Ctrl+C to quit)[/dim]"
        )
        _launch_discrete_widget_preview()


if __name__ == "__main__":
    app()
