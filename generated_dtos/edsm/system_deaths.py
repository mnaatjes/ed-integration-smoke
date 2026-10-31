"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemDeathsResponseDeathsDTO:
    """Data transfer object for EdsmSystemDeathsResponseDeathsDTO."""

    day: float
    total: float
    week: float


@dataclass(frozen=True)
class EdsmSystemDeathsResponseDTO:
    """Response structure of the EDSM system deaths request."""

    deaths: EdsmSystemDeathsResponseDeathsDTO
    id: float
    id64: Any
    name: str
    url: str

__all__ = ('EdsmSystemDeathsResponseDeathsDTO', 'EdsmSystemDeathsResponseDTO')
