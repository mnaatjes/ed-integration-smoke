"""Unit tests for the unified component workbench."""

from __future__ import annotations

import subprocess
import sys

from workbench import ComponentKind, get_slot, list_slots


def test_workbench_registry_slots() -> None:
    """Verify slots are discovered and registered correctly."""
    slots = list_slots()
    names = [s.name for s in slots]
    assert "fsd-target" in names
    assert "nav-route" in names

    fsd_slot = get_slot("fsd-target")
    assert fsd_slot.kind == ComponentKind.RICH
    assert fsd_slot.rich_renderer is not None

    nav_slot = get_slot("nav-route")
    assert nav_slot.kind == ComponentKind.TEXTUAL
    assert nav_slot.widget_factory is not None


def test_workbench_cli_list() -> None:
    """Verify scripts/run_workbench.py list displays registered slots."""
    res = subprocess.run(
        [sys.executable, "scripts/run_workbench.py", "list"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "Workbench Component Slots" in res.stdout
    assert "fsd-target" in res.stdout
    assert "nav-route" in res.stdout


def test_workbench_cli_show_rich_mock() -> None:
    """Verify scripts/run_workbench.py show fsd-target renders Rich table."""
    res = subprocess.run(
        [sys.executable, "scripts/run_workbench.py", "show", "fsd-target"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "FSD Target Lock" in res.stdout
    assert "Shinrarta Dezhra" in res.stdout
