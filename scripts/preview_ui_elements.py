"""Showcase script displaying all ed_ui_cli UI elements with mock/filler data.

Supports both interactive full-screen TUI mode (Textual) and static console
renderables showcase (Rich).
"""

from __future__ import annotations

import datetime
from typing import Annotated

import typer
from ed_ui_cli.components import (
    create_stepped_progress,
    render_connection_pill,
    render_key_value_table,
    render_metric_grid,
)
from ed_ui_cli.diagnostics import DiagnosticCheckResult, DiagnosticReporter
from ed_ui_cli.snapshots import SnapshotTarget, render_snapshot_tables
from ed_ui_cli.tui.app import TelemetryConsoleApp
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="Showcase all Rich and Textual UI elements from ed-ui-cli using filler data."
)


def _render_rich_showcase(console: Console) -> None:
    """Render all static Rich CLI components to the console."""
    console.print(
        Panel.fit(
            "[bold cyan]ed-ui-cli[/bold cyan] "
            "[bold white]Rich Terminal Component Showcase[/bold white]",
            border_style="cyan",
        )
    )

    # 1. Connection Status Pills
    console.print("\n[bold yellow]1. Connection Status Pills[/bold yellow]")
    pill_online = render_connection_pill("192.168.1.214", 8080, is_connected=True, latency_ms=4.2)
    pill_offline = render_connection_pill("192.168.1.214", 8080, is_connected=False)
    console.print(pill_online, pill_offline)

    # 2. Metric Cards & Grids
    console.print("\n[bold yellow]2. Annunciator Metric Grids[/bold yellow]")
    ship_metrics = {
        "Vessel": "Anaconda (Core Dynamics)",
        "Shields Active": True,
        "Hull Integrity": 98.4,
        "SYS Pips": 4.0,
        "ENG Pips": 2.0,
        "WEP Pips": 0.0,
        "FSD Status": "Ready",
        "Cargo Capacity": "128 / 256 T",
    }
    console.print(render_metric_grid("Ship Cockpit Telemetry", ship_metrics))

    # 3. Key-Value Tables
    console.print("\n[bold yellow]3. Structured Key-Value Property Tables[/bold yellow]")
    system_data = {
        "Star System": "Shinrarta Dezhra",
        "Primary Star": "A-Type (Blue-White)",
        "Planetary Bodies": 14,
        "Controlling Faction": "The Pilots Federation",
        "Security Level": "High",
        "Allegiance": "Independent",
        "Economy": "High Tech / Industrial",
    }
    console.print(render_key_value_table("Navigational Waypoint", system_data))

    # 4. Diagnostic Reporter
    console.print("\n[bold yellow]4. Diagnostic Health & Connection Reporter[/bold yellow]")
    reporter = DiagnosticReporter(console=console)
    reporter.report_live(
        DiagnosticCheckResult(
            name="TCP Handshake",
            endpoint="192.168.1.214:8080",
            passed=True,
            latency_ms=2.1,
            detail="Socket connected",
        )
    )
    reporter.report_live(
        DiagnosticCheckResult(
            name="CAPI Authentication",
            endpoint="/api/v1/health",
            passed=True,
            latency_ms=5.4,
            detail="Header authenticated",
        )
    )
    reporter.report_live(
        DiagnosticCheckResult(
            name="SSE Telemetry Stream",
            endpoint="/api/v1/stream",
            passed=True,
            latency_ms=11.2,
            detail="Streaming active",
        )
    )
    reporter.print_summary()

    # 5. Frontier DTO Snapshot Tables
    console.print("\n[bold yellow]5. Snapshot Table Renderers (Frontier DTOs)[/bold yellow]")
    mock_cargo_json = """{
        "Inventory": [
            {"Name": "gold", "Count": 32, "Stolen": 0},
            {"Name": "painite", "Count": 64, "Stolen": 0},
            {"Name": "voidopal", "Count": 16, "Stolen": 0}
        ]
    }"""
    cargo_tables = render_snapshot_tables(SnapshotTarget.CARGO, mock_cargo_json)
    for tbl in cargo_tables:
        console.print(tbl)

    # 6. Stepped Progress Bar
    console.print("\n[bold yellow]6. Stepped Task Progress Bar[/bold yellow]")
    progress = create_stepped_progress()
    with progress:
        task_id = progress.add_task("[cyan]Journal Historical Rehydration[/cyan]", total=5)
        for _ in range(5):
            progress.advance(task_id, 1)


def _launch_tui_showcase() -> None:
    """Launch the interactive full-screen Textual application with populated mock data."""
    mock_bodies = [
        {"name": "Sol", "type": "G-Type Main Sequence Star", "distance_ls": 0.0},
        {
            "name": "Mercury",
            "type": "Metal-Rich Body",
            "distance_ls": 194.2,
            "parent_body": "Sol",
        },
        {
            "name": "Venus",
            "type": "High Metal Content Planet",
            "distance_ls": 362.8,
            "parent_body": "Sol",
        },
        {
            "name": "Earth",
            "type": "Earth-Like World",
            "distance_ls": 501.4,
            "parent_body": "Sol",
        },
        {"name": "Moon", "type": "Rocky Body", "distance_ls": 502.7, "parent_body": "Earth"},
        {
            "name": "Mars",
            "type": "High Metal Content Planet",
            "distance_ls": 764.1,
            "parent_body": "Sol",
        },
        {"name": "Phobos", "type": "Rocky Moonlet", "distance_ls": 764.2, "parent_body": "Mars"},
        {"name": "Deimos", "type": "Rocky Moonlet", "distance_ls": 764.3, "parent_body": "Mars"},
        {
            "name": "Jupiter",
            "type": "Class I Gas Giant",
            "distance_ls": 2605.3,
            "parent_body": "Sol",
        },
    ]

    mock_payload = {
        "event": "FSDJump",
        "Timestamp": datetime.datetime.now().isoformat(),
        "StarSystem": "Shinrarta Dezhra",
        "SystemAddress": 3932277478106,
        "StarPos": [55.71875, 17.59375, 27.15625],
        "FuelUsed": 3.4812,
        "FuelLevel": 28.5188,
        "JumpDist": 24.89,
        "ShipTargeted": {
            "TargetLocked": True,
            "Ship": "FerDeLance",
            "PilotName": "CMDR Jameson",
            "PilotRank": "Elite",
            "ShieldHealth": 84.5,
            "HullHealth": 100.0,
            "Subsystem": "PowerPlant",
        },
        "FactionState": {
            "Faction": "Pilots Federation Local Branch",
            "Government": "Democracy",
            "Allegiance": "Independent",
            "Happiness": "Elated",
        },
    }

    systems = [
        "Sol",
        "Shinrarta Dezhra",
        "Achenar",
        "Alioth",
        "Colonia",
        "Eravate",
        "Lave",
        "Maia",
        "Beagle Point",
        "Sagittarius A*",
    ]

    events = [
        ("00:01:12", "nav", "FSDTarget", "Locked destination Shinrarta Dezhra [24.89 ly]"),
        ("00:01:15", "flight", "StartJump", "Jump type: Hyperspace to Shinrarta Dezhra"),
        ("00:01:28", "nav", "FSDJump", "Arrived at Shinrarta Dezhra (Star Class: A)"),
        ("00:01:40", "discovery", "FSSDiscoveryScan", "Discovered 14 bodies in system"),
        ("00:02:05", "combat", "ShipTargeted", "Scanning FerDeLance (CMDR Jameson)"),
        ("00:02:22", "flight", "SupercruiseExit", "Dropped at Jameson Memorial"),
        ("00:02:45", "station", "DockingGranted", "Pad 42 allocated at Jameson Memorial"),
        ("00:03:10", "station", "Docked", "Touchdown confirmed at Jameson Memorial"),
    ]

    class ShowcaseConsoleApp(TelemetryConsoleApp):
        """Showcase application populating mock data once widgets are mounted."""

        def on_mount(self) -> None:
            super().on_mount()
            self.cartography_tree.populate_celestial_system("Sol System", mock_bodies)
            self.json_inspector.load_payload("FSDJump DTO Payload", mock_payload)
            self.fuzzy_search.set_candidates(systems)
            for ts, channel, event_name, summary in events:
                self.data_table.append_event_row(ts, channel, event_name, summary)
            self.update_connection_status(is_connected=True, latency_ms=3.8)
            self.stream_switch.value = True

    tui_app = ShowcaseConsoleApp(
        title="Elite Dangerous Telemetry Station (UI Showcase)",
        host="192.168.1.214",
        port=8080,
    )
    tui_app.run()


@app.command()
def main(
    rich_only: Annotated[
        bool,
        typer.Option(
            "--rich",
            "-r",
            help="Render static Rich terminal UI elements instead of full-screen TUI.",
        ),
    ] = False,
) -> None:
    """Preview all UI components from ed-ui-cli with filler data."""
    console = Console()
    if rich_only:
        _render_rich_showcase(console)
    else:
        console.print(
            "[dim]Launching full-screen interactive TUI showcase... (Ctrl+C to quit)[/dim]"
        )
        _launch_tui_showcase()


if __name__ == "__main__":
    app()
