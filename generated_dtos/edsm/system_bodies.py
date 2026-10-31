"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemBodiesResponseDTO:
    """Response structure of the EDSM system bodies request."""

    bodies: list[Any]
    bodyCount: float
    id: float
    id64: Any
    name: str
    url: str

__all__ = ('EdsmSystemBodiesResponseDTO',)
