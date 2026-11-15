#!/usr/bin/env python3
"""CLI utility to stream and monitor real-time file-delta push notifications via SSE."""

from __future__ import annotations

import sys
from typing import Annotated, Any

import typer
from ed_fleet_client.adapters.driven.telemetry_http import (
    TelemetryConnectionConfig,
    TelemetryHttpClient,
)
from ed_fleet_client.adapters.driving.stream import StreamMonitor, StreamMonitorConfig
from ed_ui_cli.components import render_connection_pill
from ed_ui_cli.options import (
    ApiKeyOption,
    HostOption,
    PortOption,
)
from rich.console import Console
from rich.text import Text

app = typer.Typer(
    name="watch-file-deltas",
    help="Monitor real-time telemetry.file_delta notifications across /api/v1/events/stream.",
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
        health_resp = client.request("/api/v1/health")
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

    import asyncio
    from datetime import datetime

    async def _stream_loop() -> None:
        monitor = StreamMonitor(transport=client, config=StreamMonitorConfig())

        def _on_frame(frame: dict[str, Any]) -> None:
            target = frame.get("target") or frame.get("name") or "stream"
            if filter_set and target not in filter_set:
                return
            now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            line = Text()
            line.append(f"[{now_str}] ", style="dim")
            topic = frame.get("topic", "event")
            line.append(f" {topic.upper():<16} ", style="bold black on bright_yellow")
            line.append(f" {target:24} ", style="bold white")
            console.print(line)

        monitor.on_event(_on_frame)
        await monitor.start()
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            await monitor.stop()

    try:
        asyncio.run(_stream_loop())
    except KeyboardInterrupt:
        console.print("\n[yellow]Terminated stream monitor.[/yellow]")
        sys.exit(0)
    except Exception as exc:
        err_console.print(f"[bold red]Stream disconnected:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
