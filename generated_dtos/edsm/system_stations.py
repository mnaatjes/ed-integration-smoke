"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemStationsResponseDTO:
    """Response structure of the EDSM system stations request."""

    id: float
    id64: Any
    name: str
    stations: list[Any]
    url: str

__all__ = ('EdsmSystemStationsResponseDTO',)
