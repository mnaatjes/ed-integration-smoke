#!/usr/bin/env python3
"""Rich TUI dashboard runner for live Elite Dangerous telemetry ingestion and coverage audit."""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from ed_integration_smoke.daemon import (
    TelemetryIngressClient,
    TelemetryPipeline,
    TelemetryStorageEngine,
    build_all_targets,
)

console = Console()


def create_header(
    connected: bool,
    base_url: str,
    db_path: Path,
    summary: dict[str, Any],
    processed_count: int,
) -> Panel:
    """Render top metrics banner with connection indicator."""
    status_dot = (
        Text("● CONNECTED", style="bold green")
        if connected
        else Text("○ DISCONNECTED", style="bold red")
    )

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    grid.add_row(
        Text.assemble(("Endpoint: ", "bold"), (base_url, "cyan")),
        Text.assemble(("Status: ", "bold"), status_dot),
        Text.assemble(("Envelopes: ", "bold"), (f"{processed_count:,}", "yellow")),
    )
    ach, tot, pct = summary["achieved_targets"], summary["total_targets"], summary["percentage"]
    cov_str = f"{ach}/{tot} ({pct:.2f}%)"
    grid.add_row(
        Text.assemble(("Database: ", "bold"), (str(db_path), "dim")),
        Text.assemble(("Coverage: ", "bold"), (cov_str, "bold magenta")),
        Text.assemble(("Total Hits: ", "bold"), (f"{summary['total_hits']:,}", "green")),
    )

    return Panel(
        grid,
        title="[bold white]Elite Dangerous Fleet Telemetry Audit[/bold white]",
        border_style="blue",
    )


def create_chapter_table(summary: dict[str, Any]) -> Panel:
    """Render table of all 13 chapters with progress bars."""
    table = Table(box=None, expand=True, pad_edge=False)
    table.add_column("Chapter", style="bold cyan", width=14)
    table.add_column("Progress", ratio=1)
    table.add_column("Done / Total", justify="right", width=14)
    table.add_column("Pct", justify="right", style="bold magenta", width=8)

    for ch, stats in sorted(summary["by_chapter"].items()):
        pct = stats["percentage"]
        ach = stats["achieved"]
        tot = stats["total"]
        bar = ProgressBar(total=tot, completed=ach, width=None)
        table.add_row(ch, bar, f"{ach} / {tot}", f"{pct:5.1f}%")

    return Panel(
        table,
        title="[bold white]Frontier Chapters & Bitflags Breakdown[/bold white]",
        border_style="cyan",
    )


def create_events_panel(events_log: deque[tuple[str, str, str]]) -> Panel:
    """Render bounded ring buffer of recent achievements, events, and mismatches."""
    table = Table(box=None, expand=True, show_header=False)
    table.add_column("Timestamp", style="dim", width=10)
    table.add_column("Level", width=10)
    table.add_column("Message", ratio=1)

    for ts, lvl, msg in reversed(events_log):
        if lvl == "ACHIEVED":
            style_lvl = Text("ACHIEVED", style="bold green")
        elif lvl == "EVENT":
            style_lvl = Text("EVENT", style="bold cyan")
        elif lvl == "MISMATCH":
            style_lvl = Text("MISMATCH", style="bold red")
        elif lvl == "AUDIT":
            style_lvl = Text("AUDIT", style="bold yellow")
        else:
            style_lvl = Text("INFO", style="dim")
        table.add_row(ts, style_lvl, msg)

    return Panel(
        table,
        title="[bold white]Live Notifications & Achievements[/bold white]",
        border_style="green",
        height=12,
    )


def generate_dashboard(
    connected: bool,
    base_url: str,
    db_path: Path,
    summary: dict[str, Any],
    processed_count: int,
    events_log: deque[tuple[str, str, str]],
) -> Layout:
    """Compose full dashboard layout."""
    layout = Layout()
    layout.split_column(
        Layout(create_header(connected, base_url, db_path, summary, processed_count), size=4),
        Layout(create_chapter_table(summary), ratio=1),
        Layout(create_events_panel(events_log), size=13),
    )
    return layout


async def run_harness(
    host: str,
    port: int,
    db_path: Path,
    mismatches_path: Path,
    poll_interval: float,
) -> None:
    """Run async ingestion loop updating rich Live dashboard in place."""
    base_url = f"http://{host}:{port}"
    storage = TelemetryStorageEngine(db_path, mismatches_path=mismatches_path)
    storage.seed_targets(build_all_targets())
    pipeline = TelemetryPipeline(storage=storage)
    client = TelemetryIngressClient(base_url=base_url)

    stop_event = asyncio.Event()

    def handle_signal() -> None:
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            pass

    processed_count = 0
    last_event_id = 0
    is_connected = False
    events_log: deque[tuple[str, str, str]] = deque(maxlen=12)

    # Initial summary
    summary = storage.get_coverage_summary()
    events_log.append(
        (
            datetime.now(UTC).strftime("%H:%M:%S"),
            "INFO",
            f"Initialized harness with {summary['total_targets']} targets seeded in {db_path.name}",
        )
    )

    with Live(
        generate_dashboard(is_connected, base_url, db_path, summary, processed_count, events_log),
        refresh_per_second=4,
        screen=True,
    ) as live:
        try:
            while not stop_event.is_set():
                now_str = datetime.now(UTC).strftime("%H:%M:%S")
                summary_before = summary

                # 1. Ingest Cockpit Telemetry
                status = await client.fetch_game_status()
                if status is not None:
                    is_connected = True
                    res = pipeline.process_envelope(status)
                    processed_count += 1
                    if res.is_mismatch:
                        events_log.append(
                            (now_str, "MISMATCH", f"Telemetry mismatch: {res.error_message}")
                        )
                else:
                    is_connected = False

                # 2. Ingest New Journal Events
                event_tuples = await client.fetch_recent_events(since_id=last_event_id)
                for item_id, event_payload in event_tuples:
                    is_connected = True
                    last_event_id = max(last_event_id, item_id)
                    res = pipeline.process_envelope(event_payload)
                    processed_count += 1

                    if res.is_audit:
                        events_log.append(
                            (now_str, "AUDIT", f"{res.target_id}: {res.error_message}")
                        )
                    elif res.is_mismatch:
                        events_log.append(
                            (now_str, "MISMATCH", f"{res.target_id}: {res.error_message}")
                        )
                    elif res.success:
                        # Extract concise event summary detail
                        ev_name = event_payload.get("event", "Event")
                        detail = ""
                        if "StarSystem" in event_payload:
                            detail = f"-> {event_payload['StarSystem']}"
                        elif "BodyName" in event_payload:
                            detail = f"-> {event_payload['BodyName']}"
                        elif "MusicTrack" in event_payload:
                            detail = f"({event_payload['MusicTrack']})"
                        elif "StationName" in event_payload:
                            detail = f"at {event_payload['StationName']}"

                        event_msg = f"{ev_name} {detail}".strip()
                        events_log.append((now_str, "EVENT", event_msg))

                # Check if new targets achieved
                summary = storage.get_coverage_summary()
                if summary["achieved_targets"] > summary_before["achieved_targets"]:
                    diff = summary["achieved_targets"] - summary_before["achieved_targets"]
                    achieved_msg = (
                        f"+{diff} target(s) completed! "
                        f"Total: {summary['achieved_targets']}/{summary['total_targets']} "
                        f"({summary['percentage']:.2f}%)"
                    )
                    events_log.append((now_str, "ACHIEVED", achieved_msg))

                # Refresh in-place layout
                live.update(
                    generate_dashboard(
                        is_connected, base_url, db_path, summary, processed_count, events_log
                    )
                )

                await asyncio.sleep(poll_interval)
        finally:
            await client.aclose()


def print_cli_summary(storage: TelemetryStorageEngine) -> None:
    """Print static summary table to stdout."""
    summary = storage.get_coverage_summary()
    console.print(create_header(False, "Offline", storage.db_path, summary, summary["total_hits"]))
    console.print(create_chapter_table(summary))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elite Dangerous Live Telemetry Ingestion and Coverage Audit Dashboard",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Remote host or IP address of the gaming machine running ed-telemetry",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port of the remote ed-telemetry service",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/fleet_telemetry_smoke.db"),
        help="Path to local SQLite persistence database",
    )
    parser.add_argument(
        "--mismatches-file",
        type=Path,
        default=Path("data/domain_mismatches.jsonl"),
        help="Path to JSON Lines file recording domain mismatches for later investigation",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Cadence in seconds for polling status endpoint",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print existing target coverage summary and exit immediately",
    )

    args = parser.parse_args()

    if args.summary:
        storage = TelemetryStorageEngine(args.db, mismatches_path=args.mismatches_file)
        storage.seed_targets(build_all_targets())
        print_cli_summary(storage)
        sys.exit(0)

    try:
        asyncio.run(
            run_harness(
                host=args.host,
                port=args.port,
                db_path=args.db,
                mismatches_path=args.mismatches_file,
                poll_interval=args.poll_interval,
            )
        )
    except KeyboardInterrupt:
        console.print("[yellow]Harness stopped by operator.[/yellow]")


if __name__ == "__main__":
    main()
