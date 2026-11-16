"""Tailored navigation route presentation widget consuming NavigationRouteDto.

Decoupled from client logic and game telemetry: accepts pure presentation DTOs
via `update_route(dto: NavigationRouteDto)`.
"""

from __future__ import annotations

from ed_ui_cli.tui.components import AnalogMeterBar, NixieDigitsWidget, TelemetryDataTable
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label, Static

from dto.navigation import NavigationRouteDto


class NavigationRouteWidget(Widget):
    """Cockpit navigation flight computer widget displaying route telemetry."""

    DEFAULT_CSS = """
    NavigationRouteWidget {
        height: auto;
        border: heavy $primary;
        padding: 1;
        background: $surface;
        margin-bottom: 1;
    }
    .nav-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    .status-panel {
        height: auto;
        margin-bottom: 1;
    }
    .field-row {
        height: 1;
        color: $text;
    }
    .field-name {
        color: $secondary;
        width: 20;
    }
    .field-value {
        color: $primary;
        text-style: bold;
    }
    .scoop-badge-on {
        color: $success;
        text-style: bold;
    }
    .scoop-badge-off {
        color: $warning;
        text-style: bold;
    }
    """

    def __init__(
        self,
        initial_dto: NavigationRouteDto | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self._dto = initial_dto

        # 1. Segmented numeric readout for remaining hops
        initial_hops = str(initial_dto.remaining_jumps) if initial_dto else "0"
        self._nixie_hops = NixieDigitsWidget(
            "REMAINING HYPERSPACE HOPS", initial_value=initial_hops
        )

        # 2. Analog progress bar for remaining route
        self._meter_route = AnalogMeterBar("ROUTE COMPLETION", total=100.0, initial_value=0.0)

        # 3. Informational status labels
        self._lbl_dest = Label("DESTINATION: UNLOCKED", classes="field-value")
        self._lbl_star = Label("STAR CLASS: --", classes="field-value")
        self._lbl_scoop = Label("FUEL SCOOP: N/A", classes="field-value")
        self._lbl_dist = Label("DISTANCE: -- ly", classes="field-value")

        # 4. Waypoint sequence data table
        self._table = TelemetryDataTable(
            columns=["#", "System", "Star Class", "Distance", "Scoopable"],
            id=f"{id}-table" if id else None,
        )

    def compose(self) -> ComposeResult:
        yield Label("═══ FSD FLIGHT NAVIGATION COMPUTER ═══", classes="nav-title")
        with Horizontal(classes="status-panel"):
            with Vertical():
                yield self._lbl_dest
                yield self._lbl_star
                yield self._lbl_scoop
                yield self._lbl_dist
            with Vertical():
                yield self._nixie_hops
        yield self._meter_route
        yield Static("[dim]Planned Route Waypoints:[/dim]")
        yield self._table

    def on_mount(self) -> None:
        if self._dto is not None:
            self.update_route(self._dto)

    def update_route(self, dto: NavigationRouteDto) -> None:
        """Passive update method receiving an immutable presentation DTO."""
        self._dto = dto
        self._lbl_dest.update(f"DESTINATION: {dto.destination_system}")
        self._lbl_star.update(f"STAR CLASS: {dto.star_class}")

        scoop_text = "SCOOPABLE (KGBFOAM)" if dto.is_scoopable else "NON-SCOOPABLE (CAUTION)"
        scoop_class = "scoop-badge-on" if dto.is_scoopable else "scoop-badge-off"
        self._lbl_scoop.update(f"FUEL SCOOP: [{scoop_class}]{scoop_text}[/]")

        dist_str = f"{dto.jump_distance_ly:.2f} ly" if dto.jump_distance_ly else "Unknown"
        self._lbl_dist.update(f"NEXT JUMP DISTANCE: {dist_str}")

        # Update nixie and meter
        self._nixie_hops.update_value(str(dto.remaining_jumps))
        if dto.remaining_jumps > 0:
            pct = 100.0 / (dto.remaining_jumps + 1)
            self._meter_route.set_level(pct)
        else:
            self._meter_route.set_level(100.0)

        # Repopulate table
        self._table.clear()
        if dto.waypoints:
            for idx, wp in enumerate(dto.waypoints, start=1):
                scoop_status = "YES" if wp.is_scoopable else "NO"
                dist = f"{wp.distance_ly:.2f} ly" if wp.distance_ly else "--"
                dest_tag = " (DEST)" if wp.is_destination else ""
                self._table.append_event_row(
                    str(idx),
                    wp.system_name + dest_tag,
                    wp.star_class,
                    f"{dist} | Scoop: {scoop_status}",
                )
