"""Reusable Textual-based interactive TUI dashboard application."""

from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Label, RichLog, Static

from ..components import render_connection_pill


class MetricCardWidget(Static):
    """Textual widget displaying a structured metric card."""

    def __init__(
        self,
        title: str,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.card_title = title
        self.metrics: dict[str, Any] = {}

    def update_metrics(self, new_metrics: dict[str, Any]) -> None:
        """Update and re-render metrics."""
        self.metrics.update(new_metrics)
        self.refresh()

    def render(self) -> Text:
        t = Text()
        t.append(f"─── {self.card_title} ───\n", style="bold cyan")
        for k, v in self.metrics.items():
            t.append(f"  {k}: ", style="dim")
            if isinstance(v, bool):
                style = "bold green" if v else "bold red"
                t.append(f"{v}\n", style=style)
            elif isinstance(v, (int, float)):
                t.append(f"{v}\n", style="bold yellow")
            else:
                t.append(f"{v}\n", style="bold white")
        return t


class BaseTelemetryTUIApp(App[None]):
    """Standardized full-screen reactive Textual dashboard for telemetry and diagnostics."""

    CSS = """
    Screen {
        background: $surface;
    }
    #top-bar {
        height: 3;
        dock: top;
        background: $panel;
        padding: 0 1;
        content-align: center middle;
    }
    #body-container {
        height: 1fr;
        padding: 1;
    }
    #cards-row {
        height: 12;
        margin-bottom: 1;
    }
    .metric-card {
        width: 1fr;
        height: 100%;
        border: round $primary;
        padding: 1;
        margin: 0 1;
    }
    #event-log-container {
        height: 1fr;
        border: round $secondary;
        padding: 0 1;
    }
    #event-log {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("c", "clear_log", "Clear Log", show=True),
        Binding("p", "toggle_pause", "Pause/Resume", show=True),
    ]

    def __init__(
        self,
        title: str = "Elite Dangerous Telemetry Live Monitor",
        host: str = "192.168.1.214",
        port: int = 8080,
    ) -> None:
        super().__init__()
        self.title = title
        self.server_host = host
        self.server_port = port
        self.is_connected = False
        self.is_paused = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="top-bar"):
            yield Label(id="connection-label")
        with Container(id="body-container"):
            with Horizontal(id="cards-row"):
                yield MetricCardWidget(
                    "In-Memory State Plane",
                    id="state-card",
                    classes="metric-card",
                )
                yield MetricCardWidget(
                    "Fleet & Domain Health",
                    id="health-card",
                    classes="metric-card",
                )
            with VerticalScroll(id="event-log-container"):
                yield RichLog(id="event-log", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize connection pill upon application mount."""
        self.update_connection_status(is_connected=False)

    def update_connection_status(self, is_connected: bool, latency_ms: float | None = None) -> None:
        """Update top bar connection pill."""
        self.is_connected = is_connected
        pill = render_connection_pill(self.server_host, self.server_port, is_connected, latency_ms)
        lbl = self.query_one("#connection-label", Label)
        lbl.update(pill)

    def log_event(self, event_text: str | Text) -> None:
        """Append line to the reactive event stream viewport."""
        if not self.is_paused:
            log_widget = self.query_one("#event-log", RichLog)
            log_widget.write(event_text)

    def action_clear_log(self) -> None:
        """Clear event log pane."""
        log_widget = self.query_one("#event-log", RichLog)
        log_widget.clear()

    def action_toggle_pause(self) -> None:
        """Toggle stream updates."""
        self.is_paused = not self.is_paused
        status = "PAUSED" if self.is_paused else "RESUMED"
        self.notify(f"Stream is {status}")
