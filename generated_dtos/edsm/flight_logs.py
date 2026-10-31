"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmFlightLogsResponseLogsItemDTO:
    """Data transfer object for EdsmFlightLogsResponseLogsItemDTO."""

    date: str
    firstDiscover: bool
    shipId: Any
    system: str
    systemId: float | None = None
    systemId64: Any | None = None


@dataclass(frozen=True)
class EdsmFlightLogsResponseDTO:
    """EDSM FlightLogsResponse data contract."""

    endDateTime: str
    logs: list[EdsmFlightLogsResponseLogsItemDTO]
    startDateTime: str

__all__ = ('EdsmFlightLogsResponseLogsItemDTO', 'EdsmFlightLogsResponseDTO')
