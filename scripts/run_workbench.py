"""Unified Workbench CLI runner to inspect and prototype discrete UI components.

Replaces one-off preview scripts: slots components into isolated Rich or Textual harnesses.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

# Ensure workspace root is in sys.path when executed directly
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import typer  # noqa: E402
from ed_fleet_client import StreamMonitorConfig, create_client  # noqa: E402
from ed_fleet_client.adapters.driven.telemetry_http.models import (  # noqa: E402
    TelemetryConnectionConfig,
)
from ed_ui_cli.themes import CASSETTE_FUTURISM_THEME  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402
from textual.app import App, ComposeResult  # noqa: E402
from textual.containers import Center, Middle  # noqa: E402

from workbench import ComponentKind, ComponentSlot, get_slot, list_slots  # noqa: E402

app = typer.Typer(
    help="Unified Workbench CLI: inspect, test, and preview discrete prototype components."
)


@app.command(name="list")
def list_components() -> None:
    """List all prototype components registered in the workbench."""
    console = Console()
    table = Table(
        title="Workbench Component Slots",
        title_style="bold yellow",
        border_style="yellow",
        header_style="bold cyan",
    )
    table.add_column("Slot Name", style="bold yellow", no_wrap=True)
    table.add_column("Kind", style="magenta", no_wrap=True)
    table.add_column("Tags", style="dim", no_wrap=True)
    table.add_column("Description", style="white")

    for slot in list_slots():
        tags_str = ", ".join(slot.tags)
        table.add_row(slot.name, slot.kind.value.upper(), tags_str, slot.description)

    console.print(table)


def _render_rich_slot(slot: ComponentSlot, live: bool, host: str, port: int) -> None:
    """Render a Rich component slot."""
    console = Console()
    if not slot.rich_renderer:
        console.print(f"[bold red]Slot '{slot.name}' has no Rich renderer registered.[/bold red]")
        raise typer.Exit(code=1)

    if not live:
        dto = slot.mock_factory()
        renderable = slot.rich_renderer(dto)
        console.print(renderable)
        return

    # Live Rich mode: query or stream single update
    if not slot.live_connector:
        console.print(f"[bold red]Slot '{slot.name}' does not support live telemetry.[/bold red]")
        raise typer.Exit(code=1)

    import asyncio

    async def _run_live() -> None:
        cfg = TelemetryConnectionConfig(host=host, port=port)
        stream_cfg = StreamMonitorConfig(filter_historical=True)
        client = create_client(cfg, stream_config=stream_cfg)

        console.print(
            f"[dim]Streaming live '{slot.name}' from {host}:{port}... (Ctrl+C to stop)[/dim]"
        )

        def _on_update(dto: Any) -> None:
            if slot.rich_renderer:
                console.print(slot.rich_renderer(dto))

        # Render initial state immediately so terminal does not exit or hang blank
        dto_initial = slot.mock_factory() if slot.name != "fsd-target" else None
        if slot.rich_renderer:
            console.print(slot.rich_renderer(dto_initial))

        assert slot.live_connector is not None
        slot.live_connector(client, _on_update)
        await client.connect()

        # Keep streaming loop alive until interrupted
        while True:
            await asyncio.sleep(0.5)

    try:
        asyncio.run(_run_live())
    except KeyboardInterrupt:
        console.print("\n[dim]Live stream stopped.[/dim]")


def _launch_textual_slot(slot: ComponentSlot, live: bool, host: str, port: int) -> None:
    """Mount a Textual widget slot into an isolated, centered test frame."""
    if not slot.widget_factory:
        print(f"Slot '{slot.name}' has no widget factory registered.")
        raise typer.Exit(code=1)

    class WorkbenchFrameApp(App[None]):
        """Minimal harness displaying ONLY the slotted widget centered in viewport."""

        CSS = """
        Screen {
            align: center middle;
            background: #111417;
        }
        #slot-frame {
            width: 76;
            height: auto;
        }
        """

        def __init__(self) -> None:
            super().__init__()
            initial_dto = None if live else slot.mock_factory()
            if slot.widget_factory:
                self.slotted_widget = slot.widget_factory(initial_dto)
            self._client: Any = None
            self._connector: Any = None

        def on_mount(self) -> None:
            self.register_theme(CASSETTE_FUTURISM_THEME.to_textual_theme())
            self.theme = CASSETTE_FUTURISM_THEME.name

            if live and slot.live_connector:
                self.run_worker(self._connect_live(), exclusive=True)

        async def _connect_live(self) -> None:
            cfg = TelemetryConnectionConfig(host=host, port=port)
            stream_cfg = StreamMonitorConfig(filter_historical=True)
            self._client = create_client(cfg, stream_config=stream_cfg)

            def _on_update(dto: Any) -> None:
                if hasattr(self.slotted_widget, "update_route"):
                    self.call_from_thread(self.slotted_widget.update_route, dto)
                elif hasattr(self.slotted_widget, "update"):
                    self.call_from_thread(self.slotted_widget.update, dto)

            if slot.live_connector:
                self._connector = slot.live_connector(self._client, _on_update)

            try:
                await self._client.connect()
            except Exception as exc:
                self.notify(f"Stream error: {exc}", severity="error")

        def compose(self) -> ComposeResult:
            with Center():
                with Middle(id="slot-frame"):
                    yield self.slotted_widget

    WorkbenchFrameApp().run()


@app.command()
def show(
    name: Annotated[
        str,
        typer.Argument(help="Name of the component slot to display (use 'workbench.py list')."),
    ],
    live: Annotated[
        bool,
        typer.Option(
            "--live",
            "-l",
            help="Stream live telemetry into the component instead of mock fixture.",
        ),
    ] = False,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Telemetry host for live mode.",
        ),
    ] = "192.168.1.214",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Telemetry port for live mode.",
        ),
    ] = 8080,
) -> None:
    """Display a discrete component slot in isolation (Rich or Textual)."""
    slot = get_slot(name)
    if slot.kind == ComponentKind.RICH:
        _render_rich_slot(slot, live=live, host=host, port=port)
    elif slot.kind == ComponentKind.TEXTUAL:
        _launch_textual_slot(slot, live=live, host=host, port=port)


if __name__ == "__main__":
    app()
