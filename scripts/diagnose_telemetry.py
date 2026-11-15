"""Diagnostic and health verification suite for ed-telemetry."""

from __future__ import annotations

import argparse
import time
from typing import Any

import httpx
from ed_cli_core.diagnostics import DiagnosticCheckResult, DiagnosticReporter

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


def run_diagnostics(target: str, api_key: str | None, game_running: bool) -> int:
    """Run full endpoint, infrastructure, and ed-fleet-client diagnostics."""
    base_url = target if target.startswith(("http://", "https://")) else f"http://{target}"
    headers: dict[str, str] = {}
    if api_key:
        headers["X-API-Key"] = api_key

    reporter = DiagnosticReporter()
    reporter.console.print(
        f"[bold]ed-telemetry Diagnostic Suite[/bold] -> {base_url} (game_running={game_running})\n"
    )

    with httpx.Client(base_url=base_url, headers=headers, timeout=5.0) as http:
        # 1. System Health & Infrastructure
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

        # 2. Remaining GET endpoints
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

        # 3. System Control (POST /api/v1/system/control)
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

        # 4. SSE Stream Connectivity (GET /api/v1/events/stream)
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

    # 5. ed-fleet-client SDK Facade Check
    start = time.perf_counter()
    try:
        client = create_client()
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult("Fleet Client Facade", "create_client()", True, ms, "initialized")
        )
    except Exception as exc:
        ms = (time.perf_counter() - start) * 1000.0
        reporter.report_live(
            DiagnosticCheckResult("Fleet Client Facade", "create_client()", False, ms, str(exc))
        )
        client = None

    if game_running and client is not None:
        _run_fleet_client_diagnostics(reporter, client, base_url)

    return reporter.print_summary()


def _run_fleet_client_diagnostics(
    reporter: DiagnosticReporter, client: Any, base_url: str
) -> None:
    """Exercise EliteDangerousClient hydration and domain services in --game-running mode."""
    # State & projections
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

    # Snapshot hydration
    for snap_name in ("Status.json", "Cargo.json", "Market.json"):
        start = time.perf_counter()
        try:
            snap = client.get_snapshot(base_url, f"/api/v1/snapshots/{snap_name}")
            ms = (time.perf_counter() - start) * 1000.0
            detail = "hydrated" if snap is not None else "N/A (not present)"
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

    # Domain services
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

    # Event subscription & dispatcher
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostic suite for ed-telemetry")
    parser.add_argument(
        "--target", default="127.0.0.1:8080", help="Target host:port (default: 127.0.0.1:8080)"
    )
    parser.add_argument("--api-key", default=None, help="Optional pre-shared API key")
    parser.add_argument(
        "--game-running",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Assert live game telemetry is present",
    )
    args = parser.parse_args()
    return run_diagnostics(target=args.target, api_key=args.api_key, game_running=args.game_running)


if __name__ == "__main__":
    raise SystemExit(main())
