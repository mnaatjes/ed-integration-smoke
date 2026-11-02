#!/usr/bin/env python3
"""Standalone real-time telemetry graphing and flight instrument dashboard."""

from __future__ import annotations

import argparse
import asyncio
import signal
import time
from collections import deque
from datetime import UTC, datetime
from typing import Any

import plotext as plt
from rich.ansi import AnsiDecoder
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from ed_integration_smoke.daemon import TelemetryIngressClient

console = Console()
decoder = AnsiDecoder()


class TelemetryDashboardState:
    """Encapsulates real-time telemetry state and historical buffers for graphing."""

    def __init__(self, history_len: int = 60) -> None:
        self.history_len = history_len
        self.connected = False
        self.total_envelopes = 0

        # Ingress throughput tracking (1-second buckets)
        self.current_sec_count = 0
        self.last_sec_timestamp = int(time.time())
        self.throughput_history: deque[float] = deque([0.0] * history_len, maxlen=history_len)

        # Cockpit telemetry state
        self.flags = 0
        self.flags2 = 0
        self.gui_focus = 0
        self.pips = (4, 4, 4)  # sys, eng, wep (half-pips, 0..8)
        self.fuel_main = 0.0
        self.fuel_reservoir = 0.0
        self.fuel_history: deque[float] = deque([0.0] * history_len, maxlen=history_len)
        self.cargo = 0
        self.legal_state = "Clean"
        self.firegroup = 0

        # Event feeds
        self.flight_events: deque[tuple[str, str, str]] = deque(maxlen=20)

    def record_envelope(self, payload: dict[str, Any]) -> None:
        """Update metrics and buffers from incoming envelope."""
        self.total_envelopes += 1
        self.current_sec_count += 1
        now_sec = int(time.time())

        # Tick 1-second throughput buckets
        if now_sec > self.last_sec_timestamp:
            elapsed = now_sec - self.last_sec_timestamp
            rate = self.current_sec_count / max(1, elapsed)
            for _ in range(min(elapsed, self.history_len)):
                self.throughput_history.append(rate)
            self.current_sec_count = 0
            self.last_sec_timestamp = now_sec

        # Status telemetry snapshot
        if "Flags" in payload or "Pips" in payload:
            self.flags = int(payload.get("Flags", self.flags))
            self.flags2 = int(payload.get("Flags2", self.flags2))
            self.gui_focus = int(payload.get("GuiFocus", self.gui_focus))
            pips_raw = payload.get("Pips", [self.pips[0], self.pips[1], self.pips[2]])
            if isinstance(pips_raw, (list, tuple)) and len(pips_raw) >= 3:
                self.pips = (int(pips_raw[0]), int(pips_raw[1]), int(pips_raw[2]))

            fuel_dict = payload.get("Fuel")
            if isinstance(fuel_dict, dict):
                self.fuel_main = float(fuel_dict.get("FuelMain", self.fuel_main))
                self.fuel_reservoir = float(fuel_dict.get("FuelReservoir", self.fuel_reservoir))
                self.fuel_history.append(self.fuel_main)

            self.cargo = int(payload.get("Cargo", self.cargo))
            self.legal_state = str(payload.get("LegalState", self.legal_state))
            self.firegroup = int(payload.get("FireGroup", self.firegroup))

        # Discrete journal events
        event_name = payload.get("event")
        if event_name and isinstance(event_name, str):
            ts = payload.get("timestamp", datetime.now(UTC).strftime("%H:%M:%S"))
            short_ts = ts.split("T")[-1].rstrip("Z") if "T" in ts else ts
            detail = self._extract_event_detail(event_name, payload)
            self.flight_events.appendleft((short_ts, event_name, detail))

    @staticmethod
    def _extract_event_detail(event_name: str, payload: dict[str, Any]) -> str:
        if event_name == "FSDJump":
            return f"Jumped to {payload.get('StarSystem')} ({payload.get('JumpDist', 0):.1f} ly)"
        if event_name == "Location":
            return f"At {payload.get('StarSystem')}"
        if event_name == "Docked":
            return f"Docked at {payload.get('StationName')} ({payload.get('StationType')})"
        if event_name == "Undocked":
            return f"Undocked from {payload.get('StationName')}"
        if event_name == "Scan":
            body_type = payload.get("PlanetClass") or payload.get("StarType") or "Body"
            return f"Scanned {payload.get('BodyName')} ({body_type})"
        if event_name == "FSSSignalDiscovered":
            return f"Discovered {payload.get('SignalName')}"
        if event_name == "ReceiveText":
            return f"From {payload.get('From', 'NPC')}: {payload.get('Message', '')[:40]}"
        items_str = ", ".join(
            f"{k}={v}" for k, v in list(payload.items())[:3] if k not in ("event", "timestamp")
        )
        return items_str


def create_header(state: TelemetryDashboardState, base_url: str) -> Panel:
    status_dot = (
        Text("● STREAMING", style="bold green")
        if state.connected
        else Text("○ CONNECTING", style="bold red")
    )
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    grid.add_row(
        Text.assemble(("Feed: ", "bold"), (base_url, "cyan")),
        Text.assemble(("Connection: ", "bold"), status_dot),
        Text.assemble(("Envelopes Ingested: ", "bold"), (f"{state.total_envelopes:,}", "yellow")),
    )
    return Panel(
        grid,
        title="[bold white]Elite Dangerous Flight Deck & Telemetry Metrics[/bold white]",
        border_style="blue",
    )


def create_annunciator_panel(state: TelemetryDashboardState) -> Panel:
    """Render cockpit annunciator indicator lights."""
    # StatusFlags bitmasks
    f = state.flags
    lights = [
        ("SHIELDS", bool(f & (1 << 3)), "green"),
        ("GEAR", bool(f & (1 << 0)), "yellow"),
        ("HARDPOINTS", bool(f & (1 << 6)), "red"),
        ("SCOOP", bool(f & (1 << 9)), "yellow"),
        ("FA OFF", not bool(f & (1 << 5)), "red"),
        ("LIGHTS", bool(f & (1 << 8)), "cyan"),
        ("NIGHT VIS", bool(f & (1 << 28)), "cyan"),
        ("SILENT RUN", bool(f & (1 << 10)), "magenta"),
        ("SUPERCRUISE", bool(f & (1 << 4)), "blue"),
        ("DOCKED", bool(f & (1 << 1)), "yellow"),
        ("LANDED", bool(f & (1 << 2)), "yellow"),
        ("HYPERSPACE", bool(f & (1 << 27)), "magenta"),
    ]

    table = Table(box=None, expand=True, show_header=False, pad_edge=False)
    for _ in range(4):
        table.add_column(ratio=1, justify="center")

    for i in range(0, len(lights), 4):
        row_widgets = []
        for label, active, color in lights[i : i + 4]:
            if active:
                row_widgets.append(Text(f"[ {label} ]", style=f"bold {color} on grey15"))
            else:
                row_widgets.append(Text(f"  {label}  ", style="dim grey37"))
        table.add_row(*row_widgets)

    return Panel(
        table,
        title="[bold white]Cockpit Annunciators[/bold white]",
        border_style="cyan",
    )


def create_pips_panel(state: TelemetryDashboardState) -> Panel:
    """Render power distributor SYS / ENG / WEP gauges."""
    sys_pips, eng_pips, wep_pips = state.pips

    grid = Table(box=None, expand=True, show_header=False)
    grid.add_column("Subsystem", style="bold", width=6)
    grid.add_column("Level", width=12)
    grid.add_column("Bar", ratio=1)

    subsystems = [
        ("SYS", sys_pips, "cyan"),
        ("ENG", eng_pips, "yellow"),
        ("WEP", wep_pips, "red"),
    ]

    for name, half_pips, _color in subsystems:
        full_pips = half_pips / 2.0
        bar = ProgressBar(total=4.0, completed=full_pips, width=None)
        grid.add_row(name, f"{full_pips:.1f} / 4.0", bar)

    return Panel(
        grid,
        title="[bold white]Power Distributor (Pips)[/bold white]",
        border_style="magenta",
    )


def create_fuel_panel(state: TelemetryDashboardState) -> Panel:
    """Render fuel tank and cargo levels."""
    grid = Table(box=None, expand=True, show_header=False)
    grid.add_column("Metric", style="bold", width=12)
    grid.add_column("Value", width=14)
    grid.add_column("Gauge", ratio=1)

    main_bar = ProgressBar(total=32.0, completed=min(32.0, state.fuel_main), width=None)
    res_bar = ProgressBar(total=1.0, completed=min(1.0, state.fuel_reservoir), width=None)
    cargo_blocks = Text("■" * min(30, state.cargo), style="yellow")
    legal_style = "bold green" if state.legal_state == "Clean" else "bold red"
    legal_text = Text(state.legal_state, style=legal_style)

    grid.add_row("Main Tank", f"{state.fuel_main:.2f} / 32.0 T", main_bar)
    grid.add_row("Reservoir", f"{state.fuel_reservoir:.2f} / 1.0 T", res_bar)
    grid.add_row("Cargo Hold", f"{state.cargo} T", cargo_blocks)
    grid.add_row("Legal State", state.legal_state, legal_text)

    return Panel(
        grid,
        title="[bold white]Fuel & Consumables[/bold white]",
        border_style="green",
    )


def create_throughput_chart(state: TelemetryDashboardState, width: int, height: int) -> Panel:
    """Generate braille line graph of ingress throughput using plotext."""
    y = list(state.throughput_history)
    x = list(range(len(y)))

    plt.clf()
    plt.plotsize(max(30, width - 4), max(6, height - 4))
    plt.theme("clear")
    plt.plot(x, y, color="cyan", marker="braille")
    plt.title("Ingress Throughput (Envelopes / sec)")
    plt.xlabel("Past 60 Seconds")
    plt.ylabel("Rate")

    plot_str = str(plt.build())
    rich_text = Text.from_ansi(plot_str)

    return Panel(
        rich_text,
        title="[bold white]Live Ingress Velocity[/bold white]",
        border_style="yellow",
    )


def create_flight_events_panel(state: TelemetryDashboardState) -> Panel:
    """Render recent flight events feed."""
    table = Table(box=None, expand=True, show_header=False)
    table.add_column("Time", style="dim", width=9)
    table.add_column("Event", style="bold cyan", width=18)
    table.add_column("Detail", ratio=1)

    for ts, ev, detail in list(state.flight_events)[:12]:
        table.add_row(ts, ev, detail)

    return Panel(
        table,
        title="[bold white]Recent Flight Operations[/bold white]",
        border_style="blue",
    )


def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="upper", size=10),
        Layout(name="lower", ratio=1),
    )
    layout["upper"].split_row(
        Layout(name="annunciator", ratio=1),
        Layout(name="pips", ratio=1),
        Layout(name="fuel", ratio=1),
    )
    layout["lower"].split_row(
        Layout(name="graph", ratio=3),
        Layout(name="events", ratio=2),
    )
    return layout


async def run_dashboard(base_url: str) -> None:
    state = TelemetryDashboardState(history_len=60)
    layout = make_layout()
    client = TelemetryIngressClient(base_url=base_url)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _sig_handler() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _sig_handler)
        except NotImplementedError:
            pass

    async def ingest_worker() -> None:
        last_event_id = 0
        while not stop_event.is_set():
            try:
                # 1. Fetch Cockpit Telemetry
                status = await client.fetch_game_status()
                if status is not None:
                    state.connected = True
                    state.record_envelope(status)
                else:
                    state.connected = False

                # 2. Fetch Recent Journal Events
                events = await client.fetch_recent_events(since_id=last_event_id)
                for item_id, payload in events:
                    state.connected = True
                    last_event_id = max(last_event_id, item_id)
                    state.record_envelope(payload)

                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                state.connected = False
                await asyncio.sleep(2.0)

    ingest_task = asyncio.create_task(ingest_worker())

    with Live(layout, refresh_per_second=4, screen=True, console=console):
        try:
            while not stop_event.is_set():
                layout["header"].update(create_header(state, base_url))
                layout["annunciator"].update(create_annunciator_panel(state))
                layout["pips"].update(create_pips_panel(state))
                layout["fuel"].update(create_fuel_panel(state))

                term_w = console.width
                graph_w = max(35, int(term_w * 0.6))
                layout["graph"].update(create_throughput_chart(state, width=graph_w, height=12))
                layout["events"].update(create_flight_events_panel(state))

                await asyncio.sleep(0.25)
        finally:
            stop_event.set()
            ingest_task.cancel()
            await asyncio.gather(ingest_task, return_exceptions=True)
            await client.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elite Dangerous Flight Deck & Telemetry Metrics Visualizer.",
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
        "--url",
        default=None,
        help="Override base URL of ed-telemetry daemon (e.g. http://127.0.0.1:8080)",
    )
    args = parser.parse_args()

    base_url = args.url if args.url else f"http://{args.host}:{args.port}"

    try:
        asyncio.run(run_dashboard(base_url=base_url))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
