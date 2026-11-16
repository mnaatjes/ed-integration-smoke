"""Showcase script displaying the discrete render_fsd_target_table Rich component."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

# Ensure workspace root is in sys.path when executed directly
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import typer  # noqa: E402
from rich.console import Console  # noqa: E402

from dto.navigation import FsdTargetDto  # noqa: E402
from widgets.fsd_target import render_fsd_target_table  # noqa: E402

app = typer.Typer(help="Render the discrete FSDTarget Rich table component.")


@app.command()
def main(
    unlocked: Annotated[
        bool,
        typer.Option(
            "--unlocked",
            "-u",
            help="Render table in idle / unlocked state (None DTO).",
        ),
    ] = False,
    system: Annotated[
        str,
        typer.Option(
            "--system",
            "-s",
            help="Target star system name.",
        ),
    ] = "Sol",
    star_class: Annotated[
        str,
        typer.Option(
            "--star-class",
            "-c",
            help="Primary star spectral class.",
        ),
    ] = "G (Yellow Dwarf)",
    hops: Annotated[
        int,
        typer.Option(
            "--hops",
            "-j",
            help="Remaining jumps in route.",
        ),
    ] = 2,
    address: Annotated[
        int,
        typer.Option(
            "--address",
            "-a",
            help="System 64-bit address.",
        ),
    ] = 10477373803,
) -> None:
    """Render the discrete FSD Target Lock table."""
    console = Console()
    if unlocked:
        table = render_fsd_target_table(None)
    else:
        dto = FsdTargetDto.create(
            system_name=system,
            star_class=star_class,
            remaining_jumps=hops,
            system_address=address,
        )
        table = render_fsd_target_table(dto)

    console.print(table)


if __name__ == "__main__":
    app()
