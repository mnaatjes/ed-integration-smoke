"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshSearchBeltDTO:
    """Spansh SearchBelt contract."""

    name: str
    type: str
    mass: float
    inner_radius: float
    outer_radius: float

__all__ = ('SpanshSpanshSearchBeltDTO',)
