"""Workbench slot definition for FSD Target Lock Rich table."""

from __future__ import annotations

from typing import Any

from ed_fleet_client import EliteDangerousClient
from ed_fleet_client.core.domain.services.navigation import FSDTarget

from dto.navigation import FsdTargetDto
from widgets.fsd_target import render_fsd_target_table
from workbench.registry import ComponentKind, ComponentSlot, register_slot


def _build_mock_fsd_target() -> FsdTargetDto:
    return FsdTargetDto.create(
        system_name="Shinrarta Dezhra",
        star_class="A (Blue-White)",
        remaining_jumps=3,
        system_address=3932277478106,
    )


def _connect_live_fsd_target(
    client: EliteDangerousClient,
    on_update: Any,
) -> Any:
    def _on_target(ev: FSDTarget) -> None:
        dto = FsdTargetDto.create(
            system_name=getattr(ev, "Name", "Unknown"),
            star_class=getattr(ev, "StarClass", "Unknown"),
            remaining_jumps=int(getattr(ev, "RemainingJumpsInRoute", 1)),
            system_address=getattr(ev, "SystemAddress", None),
        )
        on_update(dto)

    sub = client.subscribe(FSDTarget, _on_target)
    return sub


FSD_TARGET_SLOT = ComponentSlot(
    name="fsd-target",
    description="Discrete Rich table rendering locked FSD target, address, star class, and hops.",
    kind=ComponentKind.RICH,
    mock_factory=_build_mock_fsd_target,
    live_connector=_connect_live_fsd_target,
    rich_renderer=render_fsd_target_table,
    tags=["navigation", "rich", "table"],
)

register_slot(FSD_TARGET_SLOT)
