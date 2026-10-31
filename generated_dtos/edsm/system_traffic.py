"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemTrafficResponseDiscoveryDTO:
    """Data transfer object for EdsmSystemTrafficResponseDiscoveryDTO."""

    commander: str
    date: str


@dataclass(frozen=True)
class EdsmSystemTrafficResponseTrafficDTO:
    """Data transfer object for EdsmSystemTrafficResponseTrafficDTO."""

    day: float
    total: float
    week: float


@dataclass(frozen=True)
class EdsmSystemTrafficResponseDTO:
    """Response structure of the EDSM system traffic request."""

    breakdown: Any
    discovery: EdsmSystemTrafficResponseDiscoveryDTO
    id: float
    id64: Any
    name: str
    traffic: EdsmSystemTrafficResponseTrafficDTO
    url: str

__all__ = ('EdsmSystemTrafficResponseDiscoveryDTO', 'EdsmSystemTrafficResponseTrafficDTO', 'EdsmSystemTrafficResponseDTO')
