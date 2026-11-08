"""Modular single-screen terminal dashboard layout engine built on Rich."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from rich.align import Align
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from .components import render_connection_pill, render_metric_grid


class SingleScreenDashboard:
    """Three-tier terminal dashboard: Header bar, Grouped content panels, and Live stream."""

    def __init__(
        self,
        title: str = "Elite Dangerous Telemetry Live Monitor",
        console: Console | None = None,
    ) -> None:
        self.title = title
        self.console = console or Console()
        self.layout = self._build_base_layout()

    def _build_base_layout(self) -> Layout:
        root = Layout()
        root.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3),
        )
        root["body"].split_row(
            Layout(name="left_pane", ratio=1),
            Layout(name="right_pane", ratio=1),
        )
        return root

    def update_header(
        self,
        host: str,
        port: int,
        is_connected: bool,
        latency_ms: float | None = None,
        subtitle: str = "Real-Time Telemetry & Domain State",
    ) -> None:
        """Update top status bar with connection pill and title."""
        pill = render_connection_pill(host, port, is_connected, latency_ms)

        title_text = Text()
        title_text.append(f" {self.title} ", style="bold bright_white on blue")
        title_text.append(f"  {subtitle}", style="dim")

        header_panel = Panel(
            Align.center(title_text),
            subtitle=f"{pill.plain}",
            border_style="blue",
        )
        self.layout["header"].update(header_panel)

    def set_grouped_metrics(
        self,
        left_title: str,
        left_metrics: Mapping[str, Any],
        right_title: str,
        right_metrics: Mapping[str, Any],
    ) -> None:
        """Populate left and right body panes with grouped metric grids."""
        left_panel = render_metric_grid(left_title, left_metrics, columns=2, border_style="cyan")
        right_panel = render_metric_grid(
            right_title, right_metrics, columns=2, border_style="magenta"
        )
        self.layout["left_pane"].update(left_panel)
        self.layout["right_pane"].update(right_panel)

    def set_content(self, pane_name: str, renderable: RenderableType) -> None:
        """Arbitrary renderable injection into a specific layout pane."""
        target = self.layout.get(pane_name)
        if target is not None:
            target.update(renderable)

    def update_footer(self, message: str = "Press Ctrl+C to terminate monitor") -> None:
        """Update bottom utility instruction line."""
        footer_text = Text(f" {message} ", style="dim italic")
        self.layout["footer"].update(Panel(Align.center(footer_text), border_style="dim"))

    def render(self) -> RenderableType:
        """Return the completed layout structure."""
        return self.layout

    def start_live(self, refresh_per_second: float = 4.0) -> Live:
        """Create a Rich Live context manager driving the dashboard."""
        return Live(
            self.layout,
            console=self.console,
            screen=True,
            auto_refresh=False,
            refresh_per_second=refresh_per_second,
        )
