"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchRingDTO:
    """Spansh SearchRing contract."""

    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float
    signals: Any | None = None
    signal_count: int | None = None
    signals_updated_at: str | None = None

__all__ = ('SpanshSpanshSearchRingDTO',)
