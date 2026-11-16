"""Discrete cockpit navigation route card consuming NavigationRouteDto.

A bounded, self-contained composite widget with no external app chrome, tables, or sidebars.
Receives immutable NavigationRouteDto view-models via `update_route(dto)`.
"""

from __future__ import annotations

from ed_ui_cli.tui.components import AnalogMeterBar, NixieDigitsWidget
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label

from dto.navigation import NavigationRouteDto


class NavigationRouteCard(Widget):
    """Self-contained discrete cockpit card displaying active hyperspace route telemetry."""

    DEFAULT_CSS = """
    NavigationRouteCard {
        width: 100%;
        height: auto;
        border: heavy $primary;
        padding: 1;
        background: $surface;
    }
    .card-header {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    .info-col {
        width: 1fr;
    }
    .hops-col {
        width: 32;
        margin-left: 1;
    }
    .field-label {
        color: $secondary;
        text-style: bold;
    }
    .field-val {
        color: $primary;
        text-style: bold;
    }
    .scoop-yes {
        color: $success;
        text-style: bold;
    }
    .scoop-no {
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

        # Discrete child widgets
        self._lbl_origin_dest = Label("ROUTE: IDLE / UNLOCKED", classes="field-val")
        self._lbl_next_hop = Label("NEXT HOP: --", classes="field-val")
        self._lbl_scoop = Label("SCOOPABLE: N/A", classes="field-val")
        self._meter_progress = AnalogMeterBar("ROUTE COMPLETION", total=100.0, initial_value=0.0)

        initial_hops = str(initial_dto.remaining_jumps) if initial_dto else "0"
        self._nixie_hops = NixieDigitsWidget("REMAINING HOPS", initial_value=initial_hops)

    def compose(self) -> ComposeResult:
        yield Label("═══ FSD NAVIGATION ROUTE CARD ═══", classes="card-header")
        with Horizontal():
            with Vertical(classes="info-col"):
                yield self._lbl_origin_dest
                yield self._lbl_next_hop
                yield self._lbl_scoop
                yield self._meter_progress
            with Vertical(classes="hops-col"):
                yield self._nixie_hops

    def on_mount(self) -> None:
        if self._dto is not None:
            self.update_route(self._dto)

    def update_route(self, dto: NavigationRouteDto) -> None:
        """Passive update method receiving an immutable presentation DTO."""
        self._dto = dto

        if not dto.is_route_active or dto.remaining_jumps == 0:
            self._lbl_origin_dest.update("ROUTE: DESTINATION REACHED / IDLE")
            self._lbl_next_hop.update(f"CURRENT SYSTEM: {dto.destination_system}")
            self._lbl_scoop.update("SCOOPABLE: --")
            self._meter_progress.set_level(100.0)
            self._nixie_hops.update_value("0")
            return

        origin = dto.current_system or "Current"
        self._lbl_origin_dest.update(
            f"ROUTE: [dim]{origin}[/dim] ──► [bold]{dto.destination_system}[/bold]"
        )

        dist_str = f" [{dto.jump_distance_ly:.2f} ly]" if dto.jump_distance_ly else ""
        self._lbl_next_hop.update(
            f"NEXT HOP: {dto.destination_system} (Class {dto.star_class}){dist_str}"
        )

        scoop_badge = (
            "[scoop-yes]YES (KGBFOAM)[/scoop-yes]"
            if dto.is_scoopable
            else "[scoop-no]NO (CAUTION)[/scoop-no]"
        )
        self._lbl_scoop.update(f"SCOOPABLE: {scoop_badge}")

        # Route meter level and nixie hops
        pct = 100.0 / (dto.remaining_jumps + 1)
        self._meter_progress.set_level(pct)
        self._nixie_hops.update_value(str(dto.remaining_jumps))
