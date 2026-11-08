from datetime import UTC, datetime

from rich.console import Console
from rich.text import Text

from ed_cli_core import (
    OutputFormat,
    SingleScreenDashboard,
    TailEventLine,
    TailLineFormatter,
    TelemetryServerParams,
    create_stepped_progress,
    render_connection_pill,
    render_key_value_table,
    render_metric_grid,
)


def test_telemetry_server_params_resolution(monkeypatch: object) -> None:
    # Default resolution
    params = TelemetryServerParams.from_env_or_defaults()
    assert params.host == "192.168.1.214"
    assert params.port == 8080
    assert params.api_key is None

    # Custom override
    custom = TelemetryServerParams(host="10.0.0.1", port=9090, api_key="secret")
    assert custom.host == "10.0.0.1"
    assert custom.port == 9090
    assert custom.api_key == "secret"


def test_output_format_enum() -> None:
    assert str(OutputFormat.RICH) == "rich"
    assert str(OutputFormat.JSON) == "json"
    assert str(OutputFormat.YAML) == "yaml"
    assert str(OutputFormat.COMPACT) == "compact"


def test_render_connection_pill() -> None:
    online_pill = render_connection_pill("192.168.1.214", 8080, is_connected=True, latency_ms=4.2)
    assert isinstance(online_pill, Text)
    assert "ONLINE" in online_pill.plain
    assert "192.168.1.214:8080" in online_pill.plain
    assert "4.2ms" in online_pill.plain

    offline_pill = render_connection_pill("192.168.1.214", 8080, is_connected=False)
    assert "OFFLINE" in offline_pill.plain


def test_tail_line_formatter_output() -> None:
    console = Console(record=True, width=120)
    formatter = TailLineFormatter(console=console)

    event = TailEventLine(
        topic="telemetry.journal",
        event_type="FSDJump",
        plane="journal",
        payload={"event": "FSDJump", "StarSystem": "Sol", "JumpDist": 15.4},
        timestamp=datetime(2026, 11, 8, 12, 0, 0, tzinfo=UTC),
        latency_ms=3.1,
    )

    rendered = formatter.format_line(event)
    assert isinstance(rendered, Text)
    line_str = rendered.plain
    assert "JOURNA" in line_str
    assert "[telemetry.journal]" in line_str
    assert "FSDJump" in line_str
    assert "StarSystem=Sol" in line_str
    assert "3.1ms" in line_str


def test_metric_grid_and_key_value_table() -> None:
    metrics = {
        "Active Journal": "Journal.01.log",
        "Sequence": 105,
        "Is Live": True,
        "Lat (ms)": 2.4,
    }
    panel = render_metric_grid("Test Metrics", metrics, columns=2)
    assert panel.title is not None
    assert "Test Metrics" in str(panel.title)

    table = render_key_value_table("Config Table", metrics)
    assert table.title == "Config Table"
    assert len(table.rows) == 4


def test_stepped_progress_creation() -> None:
    progress = create_stepped_progress()
    assert progress is not None
    task_id = progress.add_task("Processing telemetry...", total=100)
    assert task_id == 0


def test_single_screen_dashboard_assembly() -> None:
    dashboard = SingleScreenDashboard(title="Fleet Telemetry")
    dashboard.update_header("192.168.1.214", 8080, is_connected=True, latency_ms=1.5)
    dashboard.set_grouped_metrics(
        left_title="Left Metrics",
        left_metrics={"State": "OK"},
        right_title="Right Metrics",
        right_metrics={"Events": 50},
    )
    dashboard.update_footer("Test Footer")

    layout = dashboard.render()
    assert layout is not None
    assert dashboard.layout.get("header") is not None
    assert dashboard.layout.get("body") is not None
    assert dashboard.layout.get("footer") is not None
