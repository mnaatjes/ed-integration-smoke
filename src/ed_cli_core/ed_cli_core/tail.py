"""Structured tail presentation formatters with clear plane, topic, and payload badging."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from rich.console import Console, RenderableType
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


@dataclass(frozen=True)
class TailEventLine:
    """Normalized structured event model ready for terminal tail presentation."""

    topic: str
    event_type: str
    payload: Mapping[str, Any] | str
    timestamp: datetime | None = None
    source: str = "memory-buffer"
    plane: str = "state"
    latency_ms: float | None = None


class TailLineFormatter:
    """Formats event streams into human-identifiable, color-coded terminal lines."""

    PLANE_STYLES: dict[str, str] = {
        "state": "bold cyan on dark_blue",
        "status": "bold yellow on dark_goldenrod",
        "snapshots": "bold magenta on purple4",
        "journal": "bold green on dark_green",
        "system": "bold white on grey23",
        "unknown": "bold red on dark_red",
    }

    TOPIC_STYLES: dict[str, str] = {
        "telemetry.journal": "green",
        "telemetry.status": "yellow",
        "telemetry.snapshot": "magenta",
        "telemetry.audit": "blue",
        "telemetry.system": "white",
    }

    def __init__(self, console: Console | None = None, expand_json: bool = False) -> None:
        self.console = console or Console()
        self.expand_json = expand_json

    def format_badge(self, text: str, style: str) -> Text:
        """Render a rounded text badge."""
        badge = Text()
        badge.append(" ", style=style)
        badge.append(text.upper(), style=style)
        badge.append(" ", style=style)
        return badge

    def format_line(self, event: TailEventLine) -> RenderableType:
        """Renders an easily identifiable single-line tail log entry with inline metadata."""
        ts_str = (event.timestamp or datetime.now(UTC)).strftime("%H:%M:%S.%f")[:-3]

        plane_style = self.PLANE_STYLES.get(event.plane.lower(), "bold white on grey23")
        topic_color = self.TOPIC_STYLES.get(event.topic.lower(), "cyan")

        row = Text()
        row.append(f"[{ts_str}] ", style="bright_black")
        row.append_text(self.format_badge(event.plane[:6], plane_style))
        row.append(" ")
        row.append(f"[{event.topic}]", style=topic_color)
        row.append(" ")
        row.append(f"{event.event_type}", style="bold white")

        if event.latency_ms is not None:
            row.append(f" ({event.latency_ms:.1f}ms)", style="dim green")

        # Inline summary of top attributes if payload is a dict
        if isinstance(event.payload, Mapping):
            summaries: list[str] = []
            for k, v in list(event.payload.items())[:4]:
                if k in ("event", "timestamp"):
                    continue
                summaries.append(f"{k}={v}")
            if summaries:
                row.append(f"  [{', '.join(summaries)}]", style="dim italic")
        elif isinstance(event.payload, str) and event.payload:
            clean_str = event.payload.strip().replace("\n", " ")
            if len(clean_str) > 60:
                clean_str = f"{clean_str[:57]}..."
            row.append(f"  {clean_str}", style="dim")

        if not self.expand_json or not isinstance(event.payload, Mapping):
            return row

        # Expanded JSON syntax layout
        table = Table.grid(padding=(0, 1))
        table.add_row(row)
        json_repr = json.dumps(dict(event.payload), indent=2)
        table.add_row(Syntax(json_repr, "json", theme="monokai", line_numbers=False))
        return table

    def print_event(self, event: TailEventLine) -> None:
        """Directly writes formatted event to the configured Rich console."""
        self.console.print(self.format_line(event))
