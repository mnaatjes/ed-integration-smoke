"""Reusable UI components: connection pills, metric cards, stepped progress bars, and tables."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text


def render_connection_pill(
    host: str,
    port: int,
    is_connected: bool,
    latency_ms: float | None = None,
) -> Text:
    """Render a compact status pill indicating fleet server connectivity."""
    pill = Text()
    if is_connected:
        pill.append(" ONLINE ", style="bold black on bright_green")
        pill.append(f" {host}:{port}", style="bold white")
        if latency_ms is not None:
            pill.append(f" [{latency_ms:.1f}ms]", style="dim green")
    else:
        pill.append(" OFFLINE ", style="bold white on bright_red")
        pill.append(f" {host}:{port}", style="dim white")
    return pill


def render_metric_grid(
    title: str,
    metrics: Mapping[str, Any],
    columns: int = 2,
    border_style: str = "cyan",
) -> Panel:
    """Render a clean grid panel displaying grouped key/value metrics."""
    table = Table.grid(padding=(0, 2), expand=True)
    for _ in range(columns):
        table.add_column(justify="left", ratio=1)

    items = list(metrics.items())
    for i in range(0, len(items), columns):
        row_items: list[Text] = []
        for key, val in items[i : i + columns]:
            cell = Text()
            cell.append(f"{key}: ", style="dim")
            if isinstance(val, bool):
                val_style = "bold green" if val else "bold red"
                cell.append(str(val), style=val_style)
            elif isinstance(val, (int, float)):
                cell.append(str(val), style="bold yellow")
            else:
                cell.append(str(val), style="bold white")
            row_items.append(cell)

        # Pad remaining columns if last row is incomplete
        while len(row_items) < columns:
            row_items.append(Text(""))
        table.add_row(*row_items)

    return Panel(table, title=f"[bold]{title}[/bold]", border_style=border_style)


def create_stepped_progress(spinner_name: str = "dots") -> Progress:
    """Instantiate a standardized Rich Progress bar for stepped workflow execution."""
    return Progress(
        SpinnerColumn(spinner_name),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=False,
    )


def render_key_value_table(
    title: str,
    data: Mapping[str, Any],
    key_header: str = "Parameter",
    val_header: str = "Value",
    border_style: str = "blue",
) -> Table:
    """Render a two-column bordered table for inspecting configs or state payloads."""
    table = Table(title=title, border_style=border_style, show_lines=False)
    table.add_column(key_header, style="cyan", no_wrap=True)
    table.add_column(val_header, style="white")

    for k, v in data.items():
        if isinstance(v, (dict, list)):
            import json

            table.add_row(k, json.dumps(v, default=str))
        else:
            table.add_row(k, str(v))

    return table
