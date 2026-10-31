"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemEstimatedValueResponseValuablebodiesItemDTO:
    """Data transfer object for EdsmSystemEstimatedValueResponseValuablebodiesItemDTO."""

    bodyId: float
    bodyName: str
    distance: float
    valueMax: float


@dataclass(frozen=True)
class EdsmSystemEstimatedValueResponseDTO:
    """Response structure of the EDSM system estimated value request."""

    estimatedValue: float
    estimatedValueMapped: float
    id: float
    id64: Any
    name: str
    url: str
    valuableBodies: list[EdsmSystemEstimatedValueResponseValuablebodiesItemDTO]

__all__ = ('EdsmSystemEstimatedValueResponseValuablebodiesItemDTO', 'EdsmSystemEstimatedValueResponseDTO')
