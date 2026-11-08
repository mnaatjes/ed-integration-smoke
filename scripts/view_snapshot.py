#!/usr/bin/env python3
"""CLI utility to query and display tabular Elite Dangerous snapshot data using Rich."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from ed_cli_core import (
    ApiKeyOption,
    HostOption,
    PortOption,
    SnapshotTarget,
    VerboseOption,
    render_connection_pill,
    render_snapshot_tables,
)
from ed_telemetry_client import TelemetryConnectionConfig, TelemetryHttpClient

app = typer.Typer(
    name="view-snapshot",
    help="Query and display Frontier Developments snapshot tables via ed-telemetry.",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def main(
    target: Annotated[
        SnapshotTarget,
        typer.Argument(
            help="Snapshot file target to inspect (e.g. ModulesInfo, ShipLocker, Cargo, Market).",
        ),
    ] = SnapshotTarget.MODULES_INFO,
    host: HostOption = "192.168.1.214",
    port: PortOption = 8080,
    api_key: ApiKeyOption = None,
    verbose: VerboseOption = False,
) -> None:
    """Fetch live or cached snapshot JSON and render formatted Rich tables."""
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

    try:
        if target == SnapshotTarget.ALL:
            response = client.get_snapshots()
            if not isinstance(response.data, dict):
                err_console.print(
                    f"[bold red]Unexpected response payload:[/bold red] {response.data}"
                )
                raise typer.Exit(code=1)

            total = len(response.data)
            console.print(f"[bold green]Aggregated Snapshots ({total} targets):[/bold green]\n")
            for name, meta in response.data.items():
                if isinstance(meta, dict) and "raw_payload" in meta:
                    raw_payload = meta["raw_payload"]
                    for tbl in render_snapshot_tables(name, raw_payload):
                        console.print(tbl)
                        console.print()
        else:
            response = client.get_snapshot(target.value)
            raw_payload = (
                response.data.get("raw_payload", "{}")
                if isinstance(response.data, dict)
                else "{}"
            )
            tables = render_snapshot_tables(target.value, raw_payload)
            for tbl in tables:
                console.print(tbl)
                console.print()

    except Exception as exc:
        if verbose:
            err_console.print_exception()
        else:
            err_console.print(f"[bold red]Failed to fetch snapshot:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
