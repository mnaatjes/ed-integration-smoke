"""Showcase script displaying all ed_ui_cli Cassette Futurism and retro instrumentation widgets.

Demonstrates:
- Amber phosphor CRT palette and heavy hardware casing (`CASSETTE_FUTURISM_THEME`)
- Nixie / segmented numeric readout (`NixieDigitsWidget`)
- Stepped analog LED VU-meter (`AnalogMeterBar`)
- CRT oscilloscope waveform sweep (`OscilloscopeWidget`)
- 2D tactical radar sweep (`RadarSweepWidget`)
- 8-bit wireframe pixel sprite (`SpritePixelWidget`)
- Procedural vector canvas overlay (`CanvasPlotWidget`)
- Physical potentiometer / throttle controls (`ThrottleSliderWidget`)
- Hardware switches, interactive table, and tree components
"""

from __future__ import annotations

import math
from typing import Annotated, Any

import typer
from ed_ui_cli.themes import CASSETTE_FUTURISM_THEME, get_theme
from ed_ui_cli.tui.app import TelemetryConsoleApp
from ed_ui_cli.tui.components import (
    AnalogMeterBar,
    CanvasPlotWidget,
    NixieDigitsWidget,
    OscilloscopeWidget,
    RadarSweepWidget,
    SpritePixelWidget,
    ThrottleSliderWidget,
)
from rich.console import Console
from rich.panel import Panel
from rich_pixels import Pixels

app = typer.Typer(
    help="Showcase all Cassette Futurism and retro instrumentation components from ed-ui-cli."
)


def _render_static_cassette_showcase(console: Console) -> None:
    """Render a static preview of cassette futurism styling tokens to the console."""
    theme = get_theme("cassette_futurism")
    console.print(
        Panel.fit(
            f"[{theme.primary}]C A S S E T T E   F U T U R I S M[/]\n"
            f"[dim]Theme:[/] [bold]{theme.display_name}[/]\n"
            f"[dim]Border style:[/] {theme.border_style}\n"
            f"[dim]Palette:[/] Primary={theme.primary} (Amber), "
            f"Secondary={theme.secondary}, Surface={theme.surface}",
            border_style=theme.primary,
            title="ANALOG INSTRUMENTATION STATION",
        )
    )

    ascii_ship = (
        "      ..##..      \n"
        "     .######.     \n"
        "    .########.    \n"
        "  ..##########..  \n"
        " .##############. \n"
        "##################\n"
        "  ####  ##  ####  \n"
        "   ##        ##   "
    )
    pixels = Pixels.from_ascii(ascii_ship)
    console.print(
        Panel(pixels, title="Vessel Vector Silhouette (rich-pixels)", border_style=theme.primary)
    )


def _launch_cassette_tui_showcase() -> None:
    """Launch full-screen interactive Cassette Futurism instrumentation TUI."""
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll
    from textual.widgets import Footer, Header, Label, TabbedContent, TabPane

    class CassetteFuturismStationApp(TelemetryConsoleApp):
        """Dedicated retro-futuristic flight instrumentation console."""

        CSS = (
            TelemetryConsoleApp.CSS
            + f"""
        #nav-sidebar {{
            width: 38;
            min-width: 32;
            max-width: 48;
            overflow-x: auto;
            border-right: heavy {CASSETTE_FUTURISM_THEME.primary};
        }}
        #controls-sidebar {{
            width: 34;
            min-width: 30;
            max-width: 42;
            border-left: heavy {CASSETTE_FUTURISM_THEME.secondary};
        }}
        .instrument-container {{
            padding: 1;
            height: 1fr;
            overflow-y: auto;
        }}
        .analog-panel {{
            border: heavy {CASSETTE_FUTURISM_THEME.primary};
            padding: 0 1;
            margin-bottom: 1;
            background: {CASSETTE_FUTURISM_THEME.surface};
        }}
        """
        )

        def compose(self):  # type: ignore[no-untyped-def]
            yield Header(show_clock=True)
            with Container(id="console-top-row"):
                yield Label(id="connection-label")
                yield self.fuzzy_search
            with Horizontal(id="console-middle"):
                with Vertical(id="nav-sidebar"):
                    yield Label("ANALOG SENSORS", classes="section-title")
                    yield self.mode_selector
                    yield self.cartography_tree
                with Vertical(id="main-viewport"):
                    with TabbedContent():
                        with TabPane("CRT Scope & Radar", id="tab-scopes"):
                            with VerticalScroll(classes="instrument-container"):
                                yield self.nixie_speed
                                yield self.oscilloscope
                                yield self.radar
                        with TabPane("LED Meters & Vectors", id="tab-meters"):
                            with VerticalScroll(classes="instrument-container"):
                                yield self.meter_reactor
                                yield self.meter_heat
                                yield self.meter_shields
                                yield self.throttle_ctrl
                                yield self.ship_sprite
                                yield self.vector_canvas
                        with TabPane("Event Stream Log", id="tab-events"):
                            yield self.data_table
                        with TabPane("Data Buffer (JSON)", id="tab-inspector"):
                            yield self.json_inspector
                with Vertical(id="controls-sidebar"):
                    yield Label("MAIN POWER", classes="section-title")
                    yield self.stream_switch
                    yield Label("SENSOR CHANNELS", classes="section-title")
                    yield self.filter_nav
                    yield self.filter_combat
                    yield self.filter_status
                    yield Label("COCKPIT TRIGGERS", classes="section-title")
                    yield self.btn_poll
                    yield self.btn_reconnect
                    yield self.btn_clear
            yield Footer()

        def __init__(self) -> None:
            super().__init__(
                title="USCS-9000 Analog Flight Deck (Cassette Futurism)",
                theme=CASSETTE_FUTURISM_THEME,
            )
            # 1. Nixie readout
            self.nixie_speed = NixieDigitsWidget(
                "FSD CRUISE VELOCITY (KM/S)", initial_value="299792"
            )

            # 2. Stepped analog LED meters
            self.meter_reactor = AnalogMeterBar(
                "REACTOR CORE OUTPUT", total=100.0, initial_value=78.4
            )
            self.meter_heat = AnalogMeterBar("THERMAL DISSIPATION", total=100.0, initial_value=42.1)
            self.meter_shields = AnalogMeterBar(
                "FORWARD DEFLECTOR SHIELDS", total=100.0, initial_value=95.0
            )

            # 3. Potentiometer throttle slider
            self.throttle_ctrl = ThrottleSliderWidget("MAIN ENGINE THROTTLE", initial_val=75)

            # 4. CRT oscilloscope & radar sweeps
            self.oscilloscope = OscilloscopeWidget("TELEMETRY FREQUENCY SPECTRUM (CRT)")
            self.radar = RadarSweepWidget("LOCAL TACTICAL RADAR SWEEP")

            # 5. Wireframe pixel sprite
            ascii_ship = (
                "      ..##..      \n"
                "     .######.     \n"
                "    .########.    \n"
                "  ..##########..  \n"
                " .##############. \n"
                "##################\n"
                "  ####  ##  ####  \n"
                "   ##        ##   "
            )
            self.ship_sprite = SpritePixelWidget(
                "VESSEL VECTOR SILHOUETTE",
                pixels=Pixels.from_ascii(ascii_ship),
            )

            # 6. Procedural character canvas
            self.vector_canvas = CanvasPlotWidget(width=40, height=8)

        def on_mount(self) -> None:
            super().on_mount()

            # Populate celestial cartography
            bodies: list[dict[str, Any]] = [
                {"name": "Sol", "type": "G-Class Yellow Dwarf", "distance_ls": 0.0},
                {
                    "name": "Mercury",
                    "type": "Nav Beacon",
                    "distance_ls": 182.4,
                    "parent_body": "Sol",
                },
                {
                    "name": "Earth",
                    "type": "Orbital Station: Abraham Lincoln",
                    "distance_ls": 499.0,
                    "parent_body": "Sol",
                },
                {
                    "name": "Mars",
                    "type": "Shipyard: Olympus Mons",
                    "distance_ls": 764.1,
                    "parent_body": "Sol",
                },
            ]
            self.cartography_tree.populate_celestial_system("Sol System", bodies)

            # Populate mock DTO payload
            payload = {
                "system": "Shinrarta Dezhra",
                "star_class": "A",
                "vessel": "Anaconda (Core Dynamics)",
                "reactor_state": "NOMINAL",
                "fsd_drive": "ENGAGED",
                "sensor_array": "ACTIVE_OMNIDIRECTIONAL",
            }
            self.json_inspector.load_payload("FSD Jump Vector Telemetry", payload)

            # Populate candidates
            self.fuzzy_search.set_candidates(
                ["Sol", "Shinrarta Dezhra", "Achenar", "Alioth", "Colonia", "Lave", "Maia"]
            )

            # Populate event log
            events = [
                ("00:01:10", "nav", "FSDTarget", "Locked destination Shinrarta Dezhra [24.89 ly]"),
                ("00:01:25", "flight", "SupercruiseEntry", "Throttle set to 75% [299,792 km/s]"),
                (
                    "00:02:04",
                    "sensors",
                    "RadarSweep",
                    "Contact detected: hostile FerDeLance [3.2 ls]",
                ),
                ("00:02:40", "station", "DockingRequest", "Jameson Memorial approach approved"),
            ]
            for ts, ch, ev, desc in events:
                self.data_table.append_event_row(ts, ch, ev, desc)

            # Plot oscilloscope waveform
            xs = [i * 0.2 for i in range(40)]
            ys = [math.sin(x) * 2.5 + math.cos(x * 0.5) for x in xs]
            self.oscilloscope.plot_waveform(xs, ys, label="SSE Sensor Harmonic")

            # Plot radar contacts (x, y, type)
            contacts = [
                (0.0, 0.0, "self"),
                (12.5, 8.2, "contact"),
                (-14.1, 15.0, "contact"),
                (5.0, -9.8, "station"),
            ]
            self.radar.plot_contacts(contacts)

            # Update connection state
            self.update_connection_status(is_connected=True, latency_ms=2.4)
            self.stream_switch.value = True

    tui_app = CassetteFuturismStationApp()
    tui_app.run()


@app.command()
def main(
    static_preview: Annotated[
        bool,
        typer.Option(
            "--static",
            "-s",
            help="Render static cassette futurism design tokens to standard console output.",
        ),
    ] = False,
) -> None:
    """Preview all Cassette Futurism themes and retro instrumentation widgets."""
    console = Console()
    if static_preview:
        _render_static_cassette_showcase(console)
    else:
        console.print("[dim]Launching Cassette Futurism Analog Station... (Ctrl+C to quit)[/dim]")
        _launch_cassette_tui_showcase()


if __name__ == "__main__":
    app()
