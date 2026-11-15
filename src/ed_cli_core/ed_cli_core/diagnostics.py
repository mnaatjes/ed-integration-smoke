"""Reusable Rich diagnostic reporting components for ed_cli_core."""

from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass(slots=True)
class DiagnosticCheckResult:
    """Result of a single diagnostic probe."""

    name: str
    endpoint: str
    passed: bool
    latency_ms: float
    detail: str = ""


class DiagnosticReporter:
    """Streams live diagnostic check results and renders a summary table."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self.results: list[DiagnosticCheckResult] = []

    def report_live(self, result: DiagnosticCheckResult) -> None:
        """Print a single check result immediately as it completes."""
        self.results.append(result)
        badge = "[bold green]PASS[/bold green]" if result.passed else "[bold red]FAIL[/bold red]"
        self.console.print(
            f"  {badge}  {result.name:<28} {result.endpoint:<28} "
            f"[cyan]{result.latency_ms:6.1f} ms[/cyan]  {result.detail}"
        )

    def print_summary(self) -> int:
        """Render final summary table and return POSIX exit code (0 if all passed)."""
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        latencies = [r.latency_ms for r in self.results]
        avg_ms = sum(latencies) / len(latencies) if latencies else 0.0
        min_ms = min(latencies) if latencies else 0.0
        max_ms = max(latencies) if latencies else 0.0

        table = Table(title="Diagnostic Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        table.add_row("Total Checks", str(len(self.results)))
        table.add_row("Passed", f"[green]{passed}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]" if failed else "0")
        table.add_row("Latency (min / avg / max)", f"{min_ms:.1f} / {avg_ms:.1f} / {max_ms:.1f} ms")
        self.console.print()
        self.console.print(table)
        return 0 if failed == 0 else 1
