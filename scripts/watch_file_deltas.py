#!/usr/bin/env python3
"""CLI utility to stream and monitor real-time file-delta push notifications via SSE."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from ed_cli_core import (
    ApiKeyOption,
    HostOption,
    PortOption,
    render_connection_pill,
)
from ed_stream_monitor import TelemetryStreamMonitor
from ed_telemetry_client import TelemetryConnectionConfig, TelemetryHttpClient

app = typer.Typer(
    name="watch-file-deltas",
    help="Monitor real-time telemetry.file_delta notifications across /api/v1/stream.",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def main(
    targets: Annotated[
        list[str] | None,
        typer.Argument(
            help="Optional file targets to filter on (e.g. ModulesInfo, Cargo, Status). "
            "Leave empty to monitor all file deltas.",
        ),
    ] = None,
    host: HostOption = "192.168.1.214",
    port: PortOption = 8080,
    api_key: ApiKeyOption = None,
) -> None:
    """Stream live SSE file deltas and display notifications in the terminal."""
    config = TelemetryConnectionConfig(host=host, port=port, api_key=api_key)
    client = TelemetryHttpClient(config=config)

    try:
        health_resp = client.get_system_health()
        is_online = health_resp.metadata.status_code == 200
        latency_ms = health_resp.metadata.latency_ms
    except Exception:
        is_online = False
        latency_ms = None

    console.print(render_connection_pill(host, port, is_online, latency_ms))
    console.print()

    if not is_online:
        err_console.print(f"[bold red]Error:[/bold red] Cannot reach ed-telemetry at {host}:{port}")
        raise typer.Exit(code=1)

    filter_set = set(targets) if targets else None
    filter_label = ", ".join(targets) if targets else "ALL companion files"
    console.print(f"[bold cyan]Listening for file deltas on {filter_label}...[/bold cyan]")
    console.print("[dim]Press Ctrl+C to terminate monitor.[/dim]\n")

    monitor = TelemetryStreamMonitor(config=config)

    try:
        for delta in monitor.listen_deltas(filter_targets=filter_set):
            line = Text()
            line.append(f"[{delta.timestamp.strftime('%H:%M:%S.%f')[:-3]}] ", style="dim")
            line.append(" DELTA ", style="bold black on bright_yellow")
            line.append(f" {delta.target:22} ", style="bold white")
            line.append(f"({delta.action}) ", style="cyan")
            line.append(f"hash={delta.raw_hash[:16]}", style="dim green")
            console.print(line)
    except KeyboardInterrupt:
        console.print("\n[yellow]Terminated stream monitor.[/yellow]")
        sys.exit(0)
    except Exception as exc:
        err_console.print(f"[bold red]Stream disconnected:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
