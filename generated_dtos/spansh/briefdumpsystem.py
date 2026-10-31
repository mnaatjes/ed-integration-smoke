"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshBriefDumpSystemCoordsDTO:
    """Coordinates of the system."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class SpanshSpanshBriefDumpSystemDTO:
    """Spansh BriefDumpSystem contract."""

    id64: int
    name: str
    coords: SpanshSpanshBriefDumpSystemCoordsDTO
    updateTime: str
    mainStar: str | None = None
    needsPermit: bool | None = None

__all__ = ('SpanshSpanshBriefDumpSystemCoordsDTO', 'SpanshSpanshBriefDumpSystemDTO')
