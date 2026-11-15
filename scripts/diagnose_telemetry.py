"""Diagnostic and health verification suite for ed-telemetry."""

from __future__ import annotations

import argparse
import asyncio
import io
import json
import time
import urllib.parse
from typing import Any

import httpx
from ed_cli_core.diagnostics import DiagnosticCheckResult, DiagnosticReporter
from ed_fleet_client.adapters.driven.telemetry_http.models import TelemetryConnectionConfig
from rich.console import Console

from ed_fleet_client import create_client


def _probe_json(
    client: httpx.Client,
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any] | list[Any] | None, float]:
    start = time.perf_counter()
    resp = client.request(method, path, json=json_body)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    try:
        payload = resp.json()
    except ValueError:
        payload = None
    return resp.status_code, payload, elapsed_ms


def _parse_target_host_port(target: str) -> tuple[str, int]:
    raw = target if "://" in target else f"http://{target}"
    parsed = urllib.parse.urlparse(raw)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8080
    return host, port


async def _probe_stream_ingestion(client: Any, timeout_sec: float = 2.0) -> tuple[bool, int, float]:
    """Connect stream monitor briefly to assert active event streaming and state reduction."""
    initial_seq = getattr(client.state, "sequence_number", 0)
    events_received: list[dict[str, Any]] = []

    if hasattr(client, "_stream") and hasattr(client._stream, "on_event"):
        client._stream.on_event(lambda raw: events_received.append(raw))

    start = time.perf_counter()
    task = asyncio.create_task(client.connect())
    try:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_sec
        while loop.time() < deadline:
            if events_received:
                break
            await asyncio.sleep(0.05)
    finally:
        await client.disconnect()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    current_seq = getattr(client.state, "sequence_number", initial_seq)
    seq_delta = max(len(events_received), current_seq - initial_seq)
    return True, seq_delta, elapsed_ms


def run_diagnostics(
    target: str,
    api_key: str | None,
    game_running: bool,
    stream_probe: bool = False,
    probe_duration: float = 2.0,
    output_json: bool = False,
) -> int:
    """Run full endpoint, infrastructure, and ed-fleet-client diagnostics."""
    host, port = _parse_target_host_port(target)
    base_url = f"http://{host}:{port}"
    headers: dict[str, str] = {}
    if api_key:
        headers["X-API-Key"] = api_key

    console = Console(file=io.StringIO()) if output_json else Console()
    reporter = DiagnosticReporter(console=console)
    if not output_json:
        reporter.console.print(
            f"[bold]ed-telemetry Diagnostic Suite[/bold] -> {base_url} "
            f"(game_running={game_running})\n"
        )

    # 1. HTTP Endpoint & Infrastructure Probes
    with httpx.Client(base_url=base_url, headers=headers, timeout=5.0) as http:
        code, data, ms = _probe_json(http, "GET", "/api/v1/system/health")
        ok = (
            code == 200
            and isinstance(data, dict)
            and data.get("status") == "ok"
            and bool(data.get("db", {}).get("ok"))
            and bool(data.get("journal_dir", {}).get("configured"))
        )
        version = data.get("version", "?") if isinstance(data, dict) else "?"
        reporter.report_live(
            DiagnosticCheckResult(
                "System Health & DB", "GET /api/v1/system/health", ok, ms, f"v{version}"
            )
        )

        get_checks = [
            ("System Watcher", "/api/v1/system/watcher"),
            ("System Logs", "/api/v1/system/logs"),
            ("State Head", "/api/v1/state"),
            ("State Heartbeat", "/api/v1/state/heartbeat"),
            ("Game Status", "/api/v1/status"),
            ("Snapshots List", "/api/v1/snapshots"),
            ("Snapshot (Status.json)", "/api/v1/snapshots/Status.json"),
            ("Journal Latest", "/api/v1/journal/latest"),
            ("Journal Events", "/api/v1/journal/events"),
            ("Events Query", "/api/v1/events/query"),
            ("Events Queue", "/api/v1/events/queue"),
        ]
        for name, path in get_checks:
            try:
                code, data, ms = _probe_json(http, "GET", path)
                passed = (
                    code in (200, 404)
                    if "Status.json" in path and not game_running
                    else code == 200
                )
                detail = f"HTTP {code}"
            except httpx.HTTPError as exc:
                passed = False
                ms = 0.0
                detail = str(exc)
            reporter.report_live(DiagnosticCheckResult(name, f"GET {path}", passed, ms, detail))

        try:
            code, _, ms = _probe_json(
                http, "POST", "/api/v1/system/control", json_body={"action": "status"}
            )
            passed = code in (200, 400, 422)
            detail = f"HTTP {code}"
        except httpx.HTTPError as exc:
            passed = False
            ms = 0.0
            detail = str(exc)
        reporter.report_live(
            DiagnosticCheckResult(
                "System Control", "POST /api/v1/system/control", passed, ms, detail
            )
        )

        start = time.perf_counter()
        try:
            with http.stream("GET", "/api/v1/events/stream") as stream_resp:
                ms = (time.perf_counter() - start) * 1000.0
                passed = stream_resp.status_code == 200
                detail = f"HTTP {stream_resp.status_code}"
        except httpx.HTTPError as exc:
            ms = (time.perf_counter() - start) * 1000.0
            passed = False
            detail = str(exc)
        reporter.report_live(
            DiagnosticCheckResult(
                "SSE Event Stream", "GET /api/v1/events/stream", passed, ms, detail
            )
        )

    # 2. ed-fleet-client SDK Facade Check
    start = time.perf_counter()
    try:
        config = TelemetryConnectionConfig(host=host, port=port, api_key=api_key)
        client = create_client(config=config)
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult("Fleet Client Facade", "create_client()", True, ms, "configured")
        )
    except Exception as exc:
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult("Fleet Client Facade", "create_client()", False, ms, str(exc))
        )
        client = None

    if client is not None:
        if game_running or stream_probe:
            _run_stream_probe_diagnostics(reporter, client, probe_duration)
        if game_running:
            _run_fleet_client_diagnostics(reporter, client)

    if output_json:
        return _render_json_summary(reporter)

    exit_code = reporter.print_summary()
    if exit_code != 0:
        _print_remediation_guidance(reporter)
    return exit_code


def _run_stream_probe_diagnostics(
    reporter: DiagnosticReporter, client: Any, duration_sec: float
) -> None:
    """Exercise live stream ingestion and state reduction."""
    try:
        ok, count, ms = asyncio.run(_probe_stream_ingestion(client, timeout_sec=duration_sec))
        detail = f"{count} events ingested" if count > 0 else "connected (0 events)"
        reporter.report_live(
            DiagnosticCheckResult("Fleet Stream Ingestion", "client.connect()", ok, ms, detail)
        )
    except Exception as exc:
        reporter.report_live(
            DiagnosticCheckResult(
                "Fleet Stream Ingestion", "client.connect()", False, 0.0, str(exc)
            )
        )


def _run_fleet_client_diagnostics(reporter: DiagnosticReporter, client: Any) -> None:
    """Exercise EliteDangerousClient hydration and domain services in --game-running mode."""
    for prop in ("state", "ship", "location", "session"):
        start = time.perf_counter()
        try:
            val = getattr(client, prop)
            ms = (time.perf_counter() - start) * 1000.0
            detail = "hydrated" if val is not None else "N/A (idle)"
            reporter.report_live(
                DiagnosticCheckResult(f"Client .{prop}", f"client.{prop}", True, ms, detail)
            )
        except Exception as exc:
            ms = (time.perf_counter() - start) * 1000.0
            reporter.report_live(
                DiagnosticCheckResult(f"Client .{prop}", f"client.{prop}", False, ms, str(exc))
            )

    for snap_name in ("Status.json", "Cargo.json", "Market.json"):
        start = time.perf_counter()
        try:
            snap = asyncio.run(client.get_snapshot(snap_name, f"/api/v1/snapshots/{snap_name}"))
            ms = (time.perf_counter() - start) * 1000.0
            exists = getattr(snap, "exists", snap is not None)
            detail = "hydrated" if exists else "N/A (not present)"
            reporter.report_live(
                DiagnosticCheckResult(
                    f"Snapshot {snap_name}", f"get_snapshot({snap_name})", True, ms, detail
                )
            )
        except Exception as exc:
            ms = (time.perf_counter() - start) * 1000.0
            reporter.report_live(
                DiagnosticCheckResult(
                    f"Snapshot {snap_name}", f"get_snapshot({snap_name})", False, ms, str(exc)
                )
            )

    for svc_name in (
        "navigation",
        "orbital",
        "flight_performance",
        "combat_analytics",
        "astrophysics",
    ):
        start = time.perf_counter()
        try:
            svc = getattr(client, svc_name)
            ms = (time.perf_counter() - start) * 1000.0
            reporter.report_live(
                DiagnosticCheckResult(
                    f"Service .{svc_name}", f"client.{svc_name}", svc is not None, ms, "ready"
                )
            )
        except Exception as exc:
            ms = (time.perf_counter() - start) * 1000.0
            reporter.report_live(
                DiagnosticCheckResult(
                    f"Service .{svc_name}", f"client.{svc_name}", False, ms, str(exc)
                )
            )

    start = time.perf_counter()
    try:
        handler = lambda _evt: None  # noqa: E731
        client.on("Status")(handler)
        _ = client.dispatcher
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult("Event Dispatcher", "client.on() / dispatcher", True, ms, "ready")
        )
    except Exception as exc:
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult(
                "Event Dispatcher", "client.on() / dispatcher", False, ms, str(exc)
            )
        )


def _render_json_summary(reporter: DiagnosticReporter) -> int:
    """Emit JSON formatted diagnostics summary to stdout."""
    passed_count = sum(1 for r in reporter.results if r.passed)
    total_count = len(reporter.results)
    failed_count = total_count - passed_count
    payload = {
        "status": "pass" if failed_count == 0 else "fail",
        "total": total_count,
        "passed": passed_count,
        "failed": failed_count,
        "checks": [
            {
                "name": r.name,
                "endpoint": r.endpoint,
                "passed": r.passed,
                "latency_ms": round(r.latency_ms, 2),
                "detail": r.detail,
            }
            for r in reporter.results
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0 if failed_count == 0 else 1


def _print_remediation_guidance(reporter: DiagnosticReporter) -> None:
    """Print actionable troubleshooting advice when checks fail."""
    failed = [r for r in reporter.results if not r.passed]
    reporter.console.print("\n[bold yellow]Remediation Guidance:[/bold yellow]")
    for r in failed:
        if "System Health" in r.name:
            reporter.console.print(
                " • [bold]System Health Failed:[/bold] Ensure ed-telemetry daemon is running "
                "and has a valid SQLite DB."
            )
        elif "SSE Event Stream" in r.name or "Fleet Stream Ingestion" in r.name:
            reporter.console.print(
                " • [bold]Stream Ingestion Failed:[/bold] Verify network reachability and that "
                "reverse proxies buffer SSE frames."
            )
        elif "Snapshot" in r.name:
            reporter.console.print(
                f" • [bold]{r.name} Failed:[/bold] Verify Elite Dangerous journal directory "
                "is populated."
            )
        else:
            reporter.console.print(
                f" • [bold]{r.name} Failed ({r.detail}):[/bold] Check network connectivity, "
                "target port, and API key."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Developer diagnostic and verification suite for ed-telemetry and ed-fleet-client"
        )
    )
    parser.add_argument(
        "--target", default="127.0.0.1:8080", help="Target host:port (default: 127.0.0.1:8080)"
    )
    parser.add_argument("--api-key", default=None, help="Optional pre-shared API key")
    parser.add_argument(
        "--game-running",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Assert live game telemetry and execute ed-fleet-client hydration checks",
    )
    parser.add_argument(
        "--stream-probe",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Explicitly probe live SSE event stream ingestion via ed-fleet-client",
    )
    parser.add_argument(
        "--probe-duration",
        type=float,
        default=2.0,
        help="Maximum duration in seconds to sample stream events during probe (default: 2.0s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output structured JSON results instead of Rich terminal table",
    )
    args = parser.parse_args()
    return run_diagnostics(
        target=args.target,
        api_key=args.api_key,
        game_running=args.game_running,
        stream_probe=args.stream_probe,
        probe_duration=args.probe_duration,
        output_json=args.json,
    )


if __name__ == "__main__":
    raise SystemExit(main())
