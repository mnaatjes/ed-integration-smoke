#!/usr/bin/env python3
"""CLI utility to tail and pretty-print hydrated ed-models domain objects across any endpoint."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Annotated, Any

import typer
from ed_models import StatusTelemetry
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

from ed_cli_core import (
    ApiKeyOption,
    HostOption,
    IntervalOption,
    PortOption,
    VerboseOption,
    render_connection_pill,
)
from ed_hydrator import (
    HydratedEventRecord,
    HydratedTelemetryState,
    TelemetryDomainHydrator,
)
from ed_telemetry_client import TelemetryConnectionConfig, TelemetryHttpClient

app = typer.Typer(
    name="tail-hydrated-state",
    help="Tail any ed-telemetry endpoint and pretty-print hydrated ed-models domain objects.",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _normalize_endpoint(endpoint: str) -> str:
    """Normalize endpoint path ensuring /api/v1 prefix."""
    clean = endpoint.strip()
    if not clean.startswith("/"):
        clean = f"/{clean}"

    if clean.startswith("/api/v1/"):
        return clean
    if clean.startswith("/v1/"):
        return f"/api{clean}"
    if clean.startswith("/api/"):
        return clean
    return f"/api/v1{clean}"


def _render_hydrated_dashboard(
    hydrated: Any,
    raw_dict: dict[str, Any] | None,
    latency_ms: float | None,
    endpoint_path: str,
) -> Panel:
    """Renders source metadata, raw hashes, and pretty-printed ed-models domain entities."""
    # 1. State Plane (GET /api/v1/state)
    if isinstance(hydrated, HydratedTelemetryState):
        meta_table = Table(box=None, expand=True, show_header=True)
        meta_table.add_column("Property", style="bold cyan", width=18)
        meta_table.add_column("Value")

        source_journal = hydrated.active_journal or "[dim]None[/dim]"
        meta_table.add_row("Source Journal", str(source_journal))

        raw_ev = raw_dict.get("latest_journal_event") if raw_dict else None
        event_id = (
            raw_ev.get("event_id", "[dim]None[/dim]")
            if isinstance(raw_ev, dict)
            else "[dim]None[/dim]"
        )
        meta_table.add_row("Event ID", str(event_id))

        event_hash = raw_ev.get("raw_hash") if isinstance(raw_ev, dict) else None
        meta_table.add_row(
            "Journal Event Hash",
            f"[green]{event_hash}[/green]" if event_hash else "[dim]None[/dim]",
        )

        raw_st = raw_dict.get("game_status") if raw_dict else None
        status_hash = raw_st.get("raw_hash") if isinstance(raw_st, dict) else None
        meta_table.add_row(
            "Status Hash",
            f"[green]{status_hash}[/green]" if status_hash else "[dim]None[/dim]",
        )

        meta_table.add_row(
            "State Sequence",
            f"[bold yellow]{hydrated.state_sequence}[/bold yellow]",
        )
        if latency_ms is not None:
            meta_table.add_row("HTTP Latency", f"{latency_ms:.2f} ms")

        # Event
        if hydrated.latest_event is not None:
            ev_name = type(hydrated.latest_event).__name__
            event_renderable: Group | Pretty | Text = Group(
                Text(f"ed_models.JournalEvent ({ev_name}):", style="bold magenta"),
                Pretty(hydrated.latest_event, expand_all=True),
            )
        else:
            event_renderable = Text("No journal event parsed into ed-models.", style="dim")

        # Status
        if hydrated.status is not None:
            status_renderable: Group | Pretty | Text = Group(
                Text("ed_models.StatusTelemetry (Cockpit Hardware & Flags):", style="bold blue"),
                Pretty(hydrated.status, expand_all=True),
            )
        else:
            status_renderable = Text("No Status.json data parsed into ed-models.", style="dim")

        # Snapshots
        snap_table = Table(box=None, expand=True, show_header=True)
        snap_table.add_column("Snapshot File", style="bold green", width=20)
        snap_table.add_column("Live Session", width=14)
        snap_table.add_column("Raw Hash")

        if hydrated.raw_snapshots:
            for name, snap in sorted(hydrated.raw_snapshots.items()):
                live_badge = "[green]LIVE[/green]" if snap.is_live_session else "[dim]COLD[/dim]"
                h_val = snap.raw_hash
                hash_display = f"[cyan]{h_val}[/cyan]" if h_val else "[dim]None[/dim]"
                snap_table.add_row(name, live_badge, hash_display)
        else:
            snap_table.add_row("[dim]None[/dim]", "", "")

        event_panel = Panel(
            event_renderable,
            title="[bold magenta]Hydrated ed-models Journal Event[/bold magenta]",
            border_style="magenta",
        )
        status_panel = Panel(
            status_renderable,
            title="[bold blue]Hydrated ed-models Status Telemetry[/bold blue]",
            border_style="blue",
        )
        snap_panel = Panel(
            snap_table,
            title="[bold green]Auxiliary Snapshots Registry[/bold green]",
            border_style="green",
        )

        sub_str = f"Sequence: {hydrated.state_sequence} | Active Journal: {source_journal}"
        return Panel(
            Group(meta_table, Text("─" * 70, style="dim"), event_panel, status_panel, snap_panel),
            title=f"[bold cyan]Elite Dangerous State Inspector ({endpoint_path})[/bold cyan]",
            subtitle=f"[dim]{sub_str}[/dim]",
            border_style="cyan",
        )


    # 2. Individual Event Record (GET /api/v1/journal/latest or single event)
    if isinstance(hydrated, HydratedEventRecord):
        ev_name = type(hydrated.event).__name__
        ev_id_str = str(hydrated.event_id) if hydrated.event_id else "[dim]None[/dim]"
        hash_str = f"[green]{hydrated.raw_hash}[/green]" if hydrated.raw_hash else "[dim]None[/dim]"
        subtitle = f"Event ID: {ev_id_str} | Hash: {hash_str}"

        return Panel(
            Pretty(hydrated.event, expand_all=True),
            title=f"[bold magenta]Hydrated ed-models Journal Event ({ev_name})[/bold magenta]",
            subtitle=f"[dim]{subtitle}[/dim]",
            border_style="magenta",
        )

    # 3. Status Telemetry Record (GET /api/v1/status)
    if isinstance(hydrated, StatusTelemetry):
        st_hash = raw_dict.get("raw_hash") if raw_dict else None
        hash_str = f"[green]{st_hash}[/green]" if st_hash else "[dim]None[/dim]"
        return Panel(
            Pretty(hydrated, expand_all=True),
            title="[bold blue]Hydrated ed-models Status Telemetry[/bold blue]",
            subtitle=f"[dim]Hash: {hash_str}[/dim]",
            border_style="blue",
        )

    # 4. List / Sequence of Events (GET /api/v1/journal/events or /api/v1/events/query)
    if isinstance(hydrated, (tuple, list)):
        event_panels = []
        for rec in hydrated:
            if isinstance(rec, HydratedEventRecord):
                ev_name = type(rec.event).__name__
                event_panels.append(
                    Panel(
                        Pretty(rec.event, expand_all=True),
                        title=f"[bold magenta]{ev_name}[/bold magenta] (ID: {rec.event_id})",
                        border_style="magenta",
                    )
                )
        title_str = f"Hydrated Events ({len(event_panels)} records from {endpoint_path})"
        return Panel(
            Group(*event_panels),
            title=f"[bold cyan]{title_str}[/bold cyan]",
            border_style="cyan",
        )

    # Fallback for unhydrated endpoints
    return Panel(
        Pretty(raw_dict or hydrated, expand_all=True),
        title=f"[bold yellow]Payload ({endpoint_path})[/bold yellow]",
        border_style="yellow",
    )


@app.command()
def main(
    endpoint: Annotated[
        str,
        typer.Argument(
            help="Target endpoint to tail and hydrate (default: /api/v1/state).",
        ),
    ] = "/api/v1/state",
    host: HostOption = "192.168.1.214",
    port: PortOption = 8080,
    api_key: ApiKeyOption = None,
    interval: IntervalOption = 1.0,
    live_mode: Annotated[
        bool,
        typer.Option(
            "--live",
            "-l",
            help="Render as an in-place, auto-refreshing dashboard.",
        ),
    ] = False,
    verbose: VerboseOption = False,
) -> None:
    """Continuously poll any ed-telemetry endpoint, hydrate entities, and pretty-print ed-models."""
    normalized_path = _normalize_endpoint(endpoint)
    config = TelemetryConnectionConfig(host=host, port=port, api_key=api_key)
    client = TelemetryHttpClient(config=config)
    hydrator = TelemetryDomainHydrator()

    last_sequence: int = -1
    last_etag: str | None = None
    last_hash: str | None = None

    try:
        if live_mode:
            with Live(auto_refresh=False, console=console) as live:
                while True:
                    try:
                        start_time = time.perf_counter()
                        resp = client.request(normalized_path, if_none_match=last_etag)
                        lat_ms = (time.perf_counter() - start_time) * 1000.0

                        if resp.metadata.status_code == 200:
                            last_etag = resp.metadata.etag
                            raw_dict = resp.data if isinstance(resp.data, dict) else None
                            computed = (
                                str(raw_dict.get("raw_hash"))
                                if raw_dict and raw_dict.get("raw_hash")
                                else str(hash(str(resp.data)))
                            )
                            current_hash = resp.metadata.etag or computed

                            if current_hash != last_hash:
                                last_hash = current_hash
                                hydrated_res = hydrator.hydrate_response(resp)
                                dashboard = _render_hydrated_dashboard(
                                    hydrated_res,
                                    raw_dict,
                                    lat_ms,
                                    normalized_path,
                                )
                                live.update(dashboard, refresh=True)
                        elif resp.metadata.status_code == 304:
                            pass
                    except Exception:
                        if verbose:
                            console.print_exception()
                    time.sleep(interval)
        else:
            # Scrolling event log mode
            pill = render_connection_pill(host, port, is_connected=True)
            console.print(pill)
            console.print(
                f"[dim]Tailing and hydrating '{normalized_path}' (Ctrl+C to quit)...[/dim]\n"
            )


            while True:
                try:
                    start_time = time.perf_counter()
                    resp = client.request(normalized_path, if_none_match=last_etag)
                    lat_ms = (time.perf_counter() - start_time) * 1000.0

                    if resp.metadata.status_code == 200:
                        last_etag = resp.metadata.etag
                        raw_dict = resp.data if isinstance(resp.data, dict) else None
                        current_seq = (
                            int(raw_dict.get("state_sequence", 0))
                            if raw_dict and "state_sequence" in raw_dict
                            else None
                        )
                        current_hash = (
                            resp.metadata.etag
                            or (raw_dict.get("raw_hash") if raw_dict else None)
                            or str(hash(str(resp.data)))
                        )

                        is_new = (
                            (current_seq != last_sequence)
                            if current_seq is not None
                            else (current_hash != last_hash)
                        )

                        if is_new:
                            if current_seq is not None:
                                last_sequence = current_seq
                            last_hash = current_hash

                            hydrated_res = hydrator.hydrate_response(resp)
                            now_str = datetime.now(UTC).strftime("%H:%M:%S")
                            header_str = (
                                f"State Sequence {current_seq}"
                                if current_seq is not None
                                else normalized_path
                            )
                            console.print(f"[bold cyan][{now_str}][/bold cyan] {header_str}:")
                            dashboard = _render_hydrated_dashboard(
                                hydrated_res,
                                raw_dict,
                                lat_ms,
                                normalized_path,
                            )
                            console.print(dashboard)
                            console.print()
                    elif resp.metadata.status_code == 304:
                        pass
                except Exception as exc:
                    if verbose:
                        console.print_exception()
                    else:
                        err_console.print(f"[bold red]Connection Error:[/bold red] {exc}")
                time.sleep(interval)

    except KeyboardInterrupt:
        console.print("\n[dim]Stopped state tailer.[/dim]")


if __name__ == "__main__":
    app()
