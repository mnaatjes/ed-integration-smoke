"""Discrete Rich table component rendering FSD target lock data."""

from __future__ import annotations

from rich.table import Table

from dto.navigation import FsdTargetDto


def render_fsd_target_table(dto: FsdTargetDto | None = None) -> Table:
    """Render a clean, discrete Rich table displaying FSDTarget parameters.

    Args:
        dto: The FsdTargetDto instance, or None if no target is currently locked.

    Returns:
        A formatted rich.table.Table instance.
    """
    table = Table(
        title="FSD Target Lock",
        title_style="bold yellow",
        border_style="yellow",
        header_style="bold cyan",
        show_header=True,
    )
    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="bold white")

    if dto is None:
        table.add_row("Lock Status", "[dim red]UNLOCKED / NO TARGET[/dim red]")
        table.add_row("System Name", "[dim]--[/dim]")
        table.add_row("Star Class", "[dim]--[/dim]")
        table.add_row("Fuel Scoopable", "[dim]--[/dim]")
        table.add_row("Hops Remaining", "[dim]0[/dim]")
        return table

    scoop_val = (
        "[bold green]YES (KGBFOAM)[/bold green]"
        if dto.is_scoopable
        else "[bold red]NO (NON-SCOOPABLE)[/bold red]"
    )
    addr_str = str(dto.system_address) if dto.system_address is not None else "--"

    table.add_row("Lock Status", "[bold green]LOCKED[/bold green]")
    table.add_row("System Name", f"[bold yellow]{dto.system_name}[/bold yellow]")
    table.add_row("System Address", addr_str)
    table.add_row("Star Class", f"[bold white]{dto.star_class}[/bold white]")
    table.add_row("Fuel Scoopable", scoop_val)
    table.add_row("Hops Remaining", f"[bold cyan]{dto.remaining_jumps}[/bold cyan]")

    return table
