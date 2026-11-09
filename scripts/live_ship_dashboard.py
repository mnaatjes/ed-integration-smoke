#!/usr/bin/env python3
"""Live terminal ship dashboard powered by ed_cli_core and ed_fleet_client.

Renders real-time cockpit annunciators, power distribution, fuel, spatial navigation,
and rolling event notifications using Rich SingleScreenDashboard.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from datetime import datetime

from ed_cli_core.dashboard import SingleScreenDashboard
from ed_models import JournalEvent, StatusFlags, StatusFlags2, StatusTelemetry
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ed_fleet_client import EliteDangerousClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Live terminal ship dashboard for Elite Dangerous."
    )
    parser.add_argument(
        "--endpoint",
        default="http://192.168.1.214:8080",
        help="Base URL of ed-telemetry service (default: http://192.168.1.214:8080)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=4.0,
        help="Dashboard refresh rate in frames per second (default: 4.0)",
    )
    return parser.parse_args()


class LiveShipDashboardApp:
    """Orchestrates live telemetry ingestion into the ed_cli_core SingleScreenDashboard."""

    def __init__(self, endpoint: str, refresh_fps: float = 4.0) -> None:
        self.endpoint = endpoint
        self.refresh_fps = refresh_fps
        self.dashboard = SingleScreenDashboard(title="Elite Dangerous Ship Cockpit Live Monitor")

        # Custom split: body has top half (systems + nav) and bottom half (activity feed)
        self._configure_layout()

        self.client = EliteDangerousClient(
            endpoint=self.endpoint,
            auto_poll_status_interval=1.0,
        )
        self.recent_events: deque[str] = deque(maxlen=6)
        self._register_listeners()

    def _configure_layout(self) -> None:
        """Configures dashboard body into cockpit systems, flight navigation, and event feed."""
        body: Layout = self.dashboard.layout["body"]
        body.split(
            Layout(name="metrics_row", ratio=2),
            Layout(name="activity_feed", ratio=1),
        )
        body["metrics_row"].split_row(
            Layout(name="cockpit_pane", ratio=1),
            Layout(name="flight_pane", ratio=1),
        )

    def _register_listeners(self) -> None:
        """Subscribes to wildcards and specific game events for rolling event stream."""

        def on_journal_event(event: JournalEvent) -> None:
            ev_name = getattr(event, "event", event.__class__.__name__)
            ts = datetime.now().strftime("%H:%M:%S")

            # Extract informative contextual summary
            detail = ""
            if hasattr(event, "StarSystem"):
                detail = f"System: {getattr(event, 'StarSystem', '')}"
            elif hasattr(event, "StationName"):
                detail = f"Station: {getattr(event, 'StationName', '')}"
            elif hasattr(event, "MusicTrack"):
                detail = f"Track: {getattr(event, 'MusicTrack', '')}"
            elif hasattr(event, "Message"):
                sender = getattr(event, "From", "Comms")
                msg = str(getattr(event, "Message", ""))[:30]
                detail = f"{sender}: {msg}"
            elif hasattr(event, "Target"):
                detail = f"Target: {getattr(event, 'Target', '')}"

            entry = f"[{ts}] {ev_name:<20} {detail}"
            self.recent_events.append(entry)

        self.client.subscribe(JournalEvent, on_journal_event)

    def _build_cockpit_panel(self, telemetry: StatusTelemetry | None) -> Panel:
        """Constructs cockpit annunciators, pips, and fuel meters."""
        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        if not telemetry:
            table.add_row(Text("Waiting for cockpit telemetry...", style="dim italic"))
            return Panel(table, title="Cockpit Systems & Hardware", border_style="cyan")

        flags = telemetry.flags
        flags2 = telemetry.flags2

        # 1. Power Distribution (Pips)
        pips = telemetry.pips
        sys_p = pips[0] / 2.0 if len(pips) >= 1 else 0.0
        eng_p = pips[1] / 2.0 if len(pips) >= 2 else 0.0
        wep_p = pips[2] / 2.0 if len(pips) >= 3 else 0.0
        pips_text = Text()
        pips_text.append("SYS: ", style="dim")
        pips_text.append(f"{sys_p:.1f} ", style="bold cyan")
        pips_text.append("ENG: ", style="dim")
        pips_text.append(f"{eng_p:.1f} ", style="bold green")
        pips_text.append("WEP: ", style="dim")
        pips_text.append(f"{wep_p:.1f}", style="bold red")

        # 2. Fuel & Cargo
        fuel_text = Text()
        fuel_text.append(f"{telemetry.fuel_main:.2f}t ", style="bold yellow")
        fuel_text.append(f"(Res: {telemetry.fuel_reservoir:.2f}t)", style="dim")

        table.add_row(Text("Power Pips: ", style="bold"), pips_text)
        table.add_row(Text("Main Fuel: ", style="bold"), fuel_text)
        table.add_row(
            Text("Cargo Count: ", style="bold"),
            Text(str(telemetry.cargo), style="bold white"),
        )
        table.add_row(
            Text("Legal Status: ", style="bold"),
            Text(
                telemetry.legal_state,
                style="bold green" if telemetry.legal_state == "Clean" else "bold red",
            ),
        )
        table.add_row(Text(""), Text(""))

        # 3. Annunciator Grid
        def ann(label: str, active: bool, active_style: str = "bold green") -> Text:
            t = Text()
            t.append(f"{label}: ", style="dim")
            if active:
                t.append("ACTIVE", style=active_style)
            else:
                t.append("OFF", style="dim")
            return t

        c1 = ann("Cargo Scoop", StatusFlags.CARGO_SCOOP_DEPLOYED in flags, "bold yellow")
        c2 = ann("Landing Gear", StatusFlags.LANDING_GEAR_DOWN in flags, "bold cyan")
        table.add_row(c1, c2)

        c3 = ann("Shields", StatusFlags.SHIELDS_UP in flags, "bold bright_cyan")
        c4 = ann("Lights", StatusFlags.LIGHTS_ON in flags, "bold bright_white")
        table.add_row(c3, c4)

        c5 = ann("Hardpoints", StatusFlags.HARDPOINTS_DEPLOYED in flags, "bold bright_red")
        c6 = ann("Flight Assist", StatusFlags.FLIGHT_ASSIST_OFF not in flags, "bold green")
        table.add_row(c5, c6)

        c7 = ann("Supercruise", StatusFlags.SUPERCRUISE in flags, "bold bright_magenta")
        c8 = ann("Mass Lock", StatusFlags.FSD_MASS_LOCKED in flags, "bold bright_yellow")
        table.add_row(c7, c8)

        c9 = ann("In Danger", StatusFlags.IS_IN_DANGER in flags, "bold white on red")
        c10 = ann("Glide Mode", StatusFlags2.GLIDE_MODE in flags2, "bold bright_blue")
        table.add_row(c9, c10)

        return Panel(table, title="Cockpit Systems & Hardware", border_style="cyan")

    def _build_flight_panel(self) -> Panel:
        """Constructs location and ship profile status."""
        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        state = self.client.state
        loc = state.location
        ship = state.ship
        sess = state.session

        table.add_row(
            Text("Commander: ", style="bold"),
            Text(sess.commander_name, style="bold bright_white"),
        )
        table.add_row(
            Text("Credits: ", style="bold"),
            Text(f"{sess.credits:,} CR", style="bold green"),
        )
        table.add_row(Text(""), Text(""))

        table.add_row(
            Text("Star System: ", style="bold"),
            Text(loc.star_system, style="bold bright_yellow"),
        )
        table.add_row(
            Text("Body: ", style="bold"),
            Text(loc.body or "Deep Space", style="bold white"),
        )

        dock_status = Text()
        if loc.docked:
            dock_status.append(
                f"DOCKED ({loc.station_name or 'Station'})", style="bold bright_green"
            )
        elif loc.in_supercruise:
            dock_status.append("SUPERCRUISE", style="bold bright_blue")
        else:
            dock_status.append("NORMAL SPACE", style="dim")
        table.add_row(Text("Flight Regime: ", style="bold"), dock_status)

        if loc.population > 0:
            table.add_row(
                Text("Population: ", style="bold"),
                Text(f"{loc.population:,}", style="dim"),
            )
        if loc.security:
            table.add_row(Text("Security: ", style="bold"), Text(loc.security, style="dim"))
        table.add_row(Text(""), Text(""))

        # Ship Attributes
        ship_name = ship.ship_name or ship.ship_type or "Active Vessel"
        ident = f" [{ship.ship_ident}]" if ship.ship_ident else ""
        table.add_row(Text("Ship: ", style="bold"), Text(f"{ship_name}{ident}", style="bold cyan"))
        if ship.cargo_capacity > 0:
            table.add_row(
                Text("Cargo Capacity: ", style="bold"),
                Text(f"{ship.cargo_capacity} T", style="dim"),
            )

        # Reactive Navigation Service Telemetry (Pattern 1 Pull)
        dest_name = self.client.nav.target_name
        bearing = self.client.nav.bearing_to_target()
        dist_km = self.client.nav.distance_to_target_km()
        if dest_name and (bearing is not None or dist_km is not None):
            table.add_row(Text(""), Text(""))
            table.add_row(
                Text("Nav Target: ", style="bold bright_cyan"),
                Text(dest_name, style="bold bright_white"),
            )
            if bearing is not None:
                hdg = ship.telemetry.heading if ship.telemetry else None
                deflection_str = ""
                if hdg is not None:
                    deflection = (bearing - hdg + 540.0) % 360.0 - 180.0
                    turn_dir = "R" if deflection > 0 else "L"
                    deflection_str = f" (Δ {abs(deflection):.0f}° {turn_dir})"
                table.add_row(
                    Text("Target Bearing: ", style="bold bright_cyan"),
                    Text(f"{bearing:.1f}°{deflection_str}", style="bold yellow"),
                )
            if dist_km is not None:
                dist_fmt = f"{dist_km:.1f} km" if dist_km < 1000 else f"{dist_km:,.0f} km"
                table.add_row(
                    Text("Target Distance: ", style="bold bright_cyan"),
                    Text(dist_fmt, style="bold green"),
                )

        return Panel(table, title="Spatial Navigation & Vessel Profile", border_style="magenta")

    def _build_activity_panel(self) -> Panel:
        """Constructs the rolling live event feed."""
        table = Table.grid(padding=(0, 1), expand=True)
        table.add_column(ratio=1)

        if not self.recent_events:
            table.add_row(Text("Listening for live telemetry event stream...", style="dim italic"))
        else:
            for ev in self.recent_events:
                table.add_row(Text(ev, style="bright_white"))

        return Panel(
            table,
            title="Live Telemetry Event Log (Reactivity Feed)",
            border_style="yellow",
        )

    def run(self) -> int:
        """Starts background streaming and drives the live terminal dashboard."""
        self.client.start_background()

        # Extract host and port
        host = self.client.endpoint.split("//")[-1].split(":")[0]
        try:
            port = int(self.client.endpoint.split(":")[-1])
        except ValueError:
            port = 8080

        with self.dashboard.start_live(refresh_per_second=self.refresh_fps) as live:
            try:
                while True:
                    # Update header bar
                    cmd_label = self.client.state.session.commander_name
                    self.dashboard.update_header(
                        host=host,
                        port=port,
                        is_connected=True,
                        subtitle=f"CMDR {cmd_label} | Real-Time Telemetry & Domain State",
                    )

                    # Update Cockpit & Navigation Panels
                    status = self.client.state.ship.telemetry
                    cockpit_panel = self._build_cockpit_panel(status)
                    flight_panel = self._build_flight_panel()
                    activity_panel = self._build_activity_panel()

                    self.dashboard.layout["cockpit_pane"].update(cockpit_panel)
                    self.dashboard.layout["flight_pane"].update(flight_panel)
                    self.dashboard.layout["activity_feed"].update(activity_panel)

                    # Footer
                    seq = self.client.state.sequence_number
                    footer_msg = f"Seq: #{seq} | Streaming: {self.client.endpoint} | Ctrl+C to quit"
                    self.dashboard.update_footer(footer_msg)

                    live.refresh()
                    time.sleep(1.0 / self.refresh_fps)

            except KeyboardInterrupt:
                pass
            finally:
                self.client.stop()

        return 0


def main() -> int:
    args = parse_args()
    app = LiveShipDashboardApp(endpoint=args.endpoint, refresh_fps=args.fps)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
