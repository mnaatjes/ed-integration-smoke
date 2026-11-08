#!/usr/bin/env python3
"""Tail and stream live telemetry endpoint data using ed-transport and ed-cli-core."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from typing import Annotated

import typer
from rich.console import Console

from ed_cli_core import (
    ApiKeyOption,
    CountOption,
    FormatOption,
    HostOption,
    IntervalOption,
    OutputFormat,
    PortOption,
    TailEventLine,
    TailLineFormatter,
    VerboseOption,
    render_connection_pill,
)
from ed_telemetry_client import TelemetryConnectionConfig, TelemetryHttpClient

app = typer.Typer(
    name="tail_endpoint",
    help="Tails and streams live ed-telemetry endpoints using ed-cli-core formatters.",
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


@app.command()
def main(
    endpoint: Annotated[
        str,
        typer.Argument(
            help="Target endpoint URI path to tail (default: /api/v1/state).",
        ),
    ] = "/api/v1/state",
    host: HostOption = "192.168.1.214",
    port: PortOption = 8080,
    api_key: ApiKeyOption = None,
    interval: IntervalOption = 1.0,
    count: CountOption = None,
    output_format: FormatOption = OutputFormat.RICH,
    expand_json: Annotated[
        bool,
        typer.Option(
            "--expand-json",
            "-e",
            help="Expand and syntax-highlight JSON payloads beneath tail lines.",
        ),
    ] = False,
    follow_deltas_only: Annotated[
        bool,
        typer.Option(
            "--deltas-only/--all-ticks",
            help="Only emit output when ETag or payload hash advances.",
        ),
    ] = True,
    verbose: VerboseOption = False,
) -> None:
    """Connects to ed-telemetry over ed-transport and tails the target endpoint."""
    normalized_path = _normalize_endpoint(endpoint)
    config = TelemetryConnectionConfig(
        host=host,
        port=port,
        api_key=api_key,
        default_path=normalized_path,
        timeout=10.0,
    )

    client = TelemetryHttpClient(config=config)
    formatter = TailLineFormatter(console=console, expand_json=expand_json)

    if output_format == OutputFormat.RICH:
        full_url = config.build_url(normalized_path)
        console.print(f"[bold blue]Starting endpoint tailer:[/bold blue] {full_url}")
        pill = render_connection_pill(host, port, is_connected=True)
        console.print(f"Target: {pill.plain} | Interval: {interval}s")
        console.print("[dim]Press Ctrl+C to terminate tail stream.[/dim]\n")

    last_etag: str | None = None
    last_payload_hash: str | None = None
    processed_count = 0

    try:
        while count is None or processed_count < count:
            try:
                start_time = time.perf_counter()
                if_none_match = last_etag if follow_deltas_only else None
                response_dto = client.request(normalized_path, if_none_match=if_none_match)
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                status_code = response_dto.metadata.status_code
                current_etag = response_dto.metadata.etag
                now_str = datetime.now(UTC).strftime("%H:%M:%S")

                # Handle 304 Not Modified
                if status_code == 304:
                    if not follow_deltas_only and output_format == OutputFormat.RICH:
                        console.print(
                            f"[dim][{now_str}] 304 Not Modified ({latency_ms:.1f}ms)[/dim]"
                        )
                    time.sleep(interval)
                    continue

                if status_code >= 400:
                    err_console.print(
                        f"[bold red]HTTP {status_code}:[/bold red] {response_dto.text}"
                    )
                    time.sleep(interval)
                    continue

                # Check for duplicate payload hash if no ETag
                if isinstance(response_dto.data, dict):
                    content_key = (
                        response_dto.data.get("raw_hash")
                        or response_dto.data.get("event_id")
                        or response_dto.data.get("state_sequence")
                    )
                    if content_key is not None:
                        current_hash = str(content_key)
                    else:
                        stable_dict = {
                            k: v
                            for k, v in response_dto.data.items()
                            if k not in ("created_at", "timestamp")
                        }
                        current_hash = hashlib.sha256(
                            json.dumps(stable_dict, sort_keys=True).encode()
                        ).hexdigest()[:16]
                else:
                    current_hash = hashlib.sha256(response_dto.raw_payload).hexdigest()[:16]

                if follow_deltas_only and last_etag is None and current_hash == last_payload_hash:
                    time.sleep(interval)
                    continue

                last_etag = current_etag
                last_payload_hash = current_hash
                processed_count += 1

                # Formatter dispatch
                if output_format == OutputFormat.JSON:
                    print(json.dumps({
                        "timestamp": datetime.now(UTC).isoformat(),
                        "endpoint": normalized_path,
                        "metadata": {
                            "status_code": status_code,
                            "plane": response_dto.metadata.plane.value,
                            "source": response_dto.metadata.source.value,
                            "etag": current_etag,
                            "latency_ms": latency_ms,
                        },
                        "payload": response_dto.data,
                    }))
                elif output_format == OutputFormat.COMPACT:
                    data_summary = str(response_dto.data)[:80].replace("\n", " ")
                    plane = response_dto.metadata.plane
                    print(f"[{now_str}] {plane} {status_code} ({latency_ms:.1f}ms) {data_summary}")
                else:
                    # OutputFormat.RICH
                    plane_val = response_dto.metadata.plane.value
                    if isinstance(response_dto.data, dict):
                        data_dict = response_dto.data
                    else:
                        data_dict = {"content": response_dto.data}

                    # Extract primary event or resource label
                    event_type = normalized_path.rstrip("/").split("/")[-1]
                    if "event" in data_dict:
                        event_type = str(data_dict["event"])
                    elif "latest_journal_event" in data_dict and isinstance(
                        data_dict["latest_journal_event"], dict
                    ):
                        event_type = f"State [Seq {data_dict.get('state_sequence')}]"

                    tail_event = TailEventLine(
                        topic=f"telemetry.{plane_val}",
                        event_type=event_type,
                        plane=plane_val,
                        source=response_dto.metadata.source.value,
                        payload=data_dict,
                        timestamp=datetime.now(UTC),
                        latency_ms=latency_ms,
                    )
                    formatter.print_event(tail_event)

            except Exception as exc:
                if verbose:
                    console.print_exception()
                else:
                    pill_off = render_connection_pill(host, port, is_connected=False)
                    err_time = datetime.now(UTC).strftime("%H:%M:%S")
                    err_console.print(
                        f"[{err_time}] {pill_off.plain} Error: {exc}"
                    )

            time.sleep(interval)

    except KeyboardInterrupt:
        if output_format == OutputFormat.RICH:
            console.print("\n[dim]Tailer stopped cleanly by operator.[/dim]")


if __name__ == "__main__":
    app()
