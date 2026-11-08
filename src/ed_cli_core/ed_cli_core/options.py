"""Reusable Typer options and standard parameter presets for Elite Dangerous CLI tools."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated

import typer


class OutputFormat(StrEnum):
    """Supported output rendering formats across CLI scripts."""

    RICH = "rich"
    JSON = "json"
    YAML = "yaml"
    COMPACT = "compact"


# Standard CLI Option Annotations
HostOption = Annotated[
    str,
    typer.Option(
        "--host",
        "-h",
        help="Target ed-telemetry host or IP address.",
        envvar="ED_TELEMETRY_HOST",
    ),
]

PortOption = Annotated[
    int,
    typer.Option(
        "--port",
        "-p",
        help="Target ed-telemetry port number.",
        envvar="ED_TELEMETRY_PORT",
    ),
]

ApiKeyOption = Annotated[
    str | None,
    typer.Option(
        "--api-key",
        "-k",
        help="Authentication API key (overrides ED_API_KEY environment variable).",
        envvar="ED_API_KEY",
    ),
]

FormatOption = Annotated[
    OutputFormat,
    typer.Option(
        "--format",
        "-f",
        help="Output serialization format.",
        case_sensitive=False,
    ),
]

VerboseOption = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Enable verbose output and stack traces.",
    ),
]

IntervalOption = Annotated[
    float,
    typer.Option(
        "--interval",
        "-i",
        help="Polling interval in seconds.",
    ),
]

CountOption = Annotated[
    int | None,
    typer.Option(
        "--count",
        "-n",
        help="Number of iterations or events to process before terminating (None for infinite).",
    ),
]


@dataclass(frozen=True)
class TelemetryServerParams:
    """Consolidated parameter set for connecting to an ed-telemetry server."""

    host: str = "192.168.1.214"
    port: int = 8080
    api_key: str | None = None

    @classmethod
    def from_env_or_defaults(
        cls,
        host: str | None = None,
        port: int | None = None,
        api_key: str | None = None,
    ) -> TelemetryServerParams:
        resolved_host = host or os.environ.get("ED_TELEMETRY_HOST", "192.168.1.214")
        resolved_port = port or int(os.environ.get("ED_TELEMETRY_PORT", "8080"))
        resolved_key = api_key or os.environ.get("ED_API_KEY")
        return cls(host=resolved_host, port=resolved_port, api_key=resolved_key)
