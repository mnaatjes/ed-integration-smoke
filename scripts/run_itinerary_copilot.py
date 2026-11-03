#!/usr/bin/env python3
"""Interactive Rich TUI In-Game Copilot & Itinerary Navigator."""

from __future__ import annotations

import argparse
import asyncio
import signal
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ed_integration_smoke.daemon.storage import TelemetryStorageEngine
from ed_integration_smoke.itinerary.models import ItineraryStep, PlayerContext
from ed_integration_smoke.itinerary.planner import ItineraryPlanner

console = Console()


def create_header(ctx: PlayerContext, summary: dict[str, Any], total_steps: int) -> Panel:
    """Render top operational banner with live location, vessel, and carrier status."""
    grid = Table.grid(expand=True)
    grid.add_column(ratio=2)
    grid.add_column(ratio=2)
    grid.add_column(ratio=1)

    carrier_str = (
        f"{ctx.carrier_name} ({ctx.carrier_callsign})"
        if ctx.carrier_name
        else "No Carrier Detected"
    )
    grid.add_row(
        Text.assemble(("Location: ", "bold"), (ctx.system, "bold cyan")),
        Text.assemble(("Carrier: ", "bold"), (carrier_str, "yellow")),
        Text.assemble(("Remaining: ", "bold"), (f"{total_steps}", "bold red")),
    )
    vessel_str = f"{ctx.ship_type}" + (f" ({ctx.ship_name})" if ctx.ship_name else "")
    ach, tot, pct = summary["achieved_targets"], summary["total_targets"], summary["percentage"]
    cov_str = f"{ach}/{tot} ({pct:.1f}%)"
    grid.add_row(
        Text.assemble(("Vessel: ", "bold"), (vessel_str, "green")),
        Text.assemble(("Station/Body: ", "bold"), (ctx.station or ctx.body or "Deep Space", "dim")),
        Text.assemble(("Coverage: ", "bold"), (cov_str, "bold magenta")),
    )

    return Panel(
        grid,
        title="[bold white]Elite Dangerous Mission Itinerary & Flight Copilot[/bold white]",
        border_style="blue",
    )


def create_active_objective_panel(step: ItineraryStep | None, step_num: int, total: int) -> Panel:
    """Render high-visibility panel highlighting the single next actionable task."""
    if not step:
        all_done = Text("ALL 305 AUDIT TARGETS COMPLETED! FLEET VERIFICATION 100%", "bold green")
        return Panel(all_done, title="[bold green]Complete[/bold green]", border_style="green")

    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(width=16, style="bold cyan")
    grid.add_column(ratio=1)

    grid.add_row("Mission Phase:", Text(step.phase, style="bold yellow"))
    grid.add_row(
        "Target Objective:",
        Text(f"{step.title}  [{step.target_id}]", style="bold white on blue"),
    )
    grid.add_row("Action / Hint:", Text(step.action_hint, style="bold green"))
    grid.add_row("Instruction:", Text(step.instruction, style="white"))
    grid.add_row(
        "Waypoint:",
        Text(f"[{step.waypoint_type.upper()}]  {step.waypoint_name}", style="bold magenta"),
    )

    title_text = f"[bold yellow]Current Objective ({step_num} of {total})[/bold yellow]"
    return Panel(
        grid,
        title=title_text,
        border_style="yellow",
        padding=(1, 2),
    )


def create_itinerary_queue_table(steps: list[ItineraryStep]) -> Panel:
    """Render rolling queue of upcoming itinerary steps."""
    table = Table(box=None, expand=True, pad_edge=False)
    table.add_column("#", style="dim", width=4)
    table.add_column("Phase", style="cyan", width=26)
    table.add_column("Target", style="bold white", width=22)
    table.add_column("Waypoint", style="magenta", width=26)
    table.add_column("Action Hint", ratio=1, style="dim")

    for i, s in enumerate(steps[1:7], start=2):
        table.add_row(
            str(i),
            s.phase,
            s.title,
            s.waypoint_name[:24],
            s.action_hint,
        )

    return Panel(
        table,
        title="[bold white]Upcoming Itinerary Queue[/bold white]",
        border_style="cyan",
    )


def create_recent_achieved_panel(storage: TelemetryStorageEngine) -> Panel:
    """Render list of most recently completed targets for immediate confirmation."""
    with storage._get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT target_id, chapter, last_seen_at FROM target_coverage
            WHERE hit_count > 0 AND last_seen_at IS NOT NULL
              AND target_id NOT IN ('Status', 'IN_MAIN_SHIP', 'SHIELDS_UP', 'LIGHTS_ON')
            ORDER BY last_seen_at DESC LIMIT 4
            """
        )
        recent = cursor.fetchall()

    table = Table(box=None, expand=True, show_header=False, pad_edge=False)
    table.add_column("Status", width=4)
    table.add_column("Target", style="bold green", width=22)
    table.add_column("Chapter", style="cyan", width=14)
    table.add_column("Time", style="dim", ratio=1)

    for row in recent:
        seen = str(row["last_seen_at"])
        ts = seen.split("T")[-1].split(".")[0] if "T" in seen else ""
        table.add_row("✔", row["target_id"], row["chapter"], ts)

    return Panel(
        table,
        title="[bold green]Recent Target Completions[/bold green]",
        border_style="green",
    )


def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="active_objective", size=9),
        Layout(name="lower", ratio=1),
    )
    layout["lower"].split_row(
        Layout(name="queue", ratio=3),
        Layout(name="recent", ratio=2),
    )
    return layout


async def run_copilot(db_path: Path) -> None:
    storage = TelemetryStorageEngine(db_path)
    planner = ItineraryPlanner(storage)
    layout = make_layout()

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _sig_handler() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _sig_handler)
        except NotImplementedError:
            pass

    with Live(layout, refresh_per_second=2, screen=True, console=console):
        try:
            while not stop_event.is_set():
                ctx = planner.resolve_player_context()
                summary = storage.get_coverage_summary()
                steps = planner.generate_itinerary()

                current_step = steps[0] if steps else None
                total_steps = len(steps)
                step_idx = 1 if current_step else 0

                layout["header"].update(create_header(ctx, summary, total_steps))
                layout["active_objective"].update(
                    create_active_objective_panel(current_step, step_idx, total_steps)
                )
                layout["queue"].update(create_itinerary_queue_table(steps))
                layout["recent"].update(create_recent_achieved_panel(storage))

                await asyncio.sleep(0.5)
        finally:
            stop_event.set()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elite Dangerous Tactical Mission Itinerary & In-Game Copilot."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/fleet_telemetry_smoke.db"),
        help="Path to local SQLite persistence database",
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_copilot(db_path=args.db))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
