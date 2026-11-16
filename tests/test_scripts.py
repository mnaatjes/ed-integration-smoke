"""Integration sanity tests for retained smoke scripts and dependencies."""

from __future__ import annotations

import subprocess
import sys


def test_diagnose_telemetry_help() -> None:
    """Verify scripts/diagnose_telemetry.py executes and presents CLI options."""
    res = subprocess.run(
        [sys.executable, "scripts/diagnose_telemetry.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "usage: diagnose_telemetry.py" in res.stdout


def test_tail_endpoint_help() -> None:
    """Verify scripts/tail_endpoint.py executes and presents Typer help."""
    res = subprocess.run(
        [sys.executable, "scripts/tail_endpoint.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "Usage: tail_endpoint.py" in res.stdout


def test_watch_file_deltas_help() -> None:
    """Verify scripts/watch_file_deltas.py executes and presents Typer help."""
    res = subprocess.run(
        [sys.executable, "scripts/watch_file_deltas.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "Usage: watch_file_deltas.py" in res.stdout


def test_preview_ui_elements_help() -> None:
    """Verify scripts/preview_ui_elements.py executes and presents Typer help."""
    res = subprocess.run(
        [sys.executable, "scripts/preview_ui_elements.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "preview_ui_elements.py" in res.stdout


def test_preview_ui_elements_rich_mode() -> None:
    """Verify scripts/preview_ui_elements.py --rich runs without error."""
    res = subprocess.run(
        [sys.executable, "scripts/preview_ui_elements.py", "--rich"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0
    assert "Rich Terminal Component Showcase" in res.stdout

