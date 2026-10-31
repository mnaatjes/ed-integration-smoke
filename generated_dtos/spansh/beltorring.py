"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshBeltOrRingSignalsDTO:
    """The signals that can be found within the belt or ring."""

    signals: dict[str, Any]
    updateTime: str


@dataclass(frozen=True)
class SpanshSpanshBeltOrRingDTO:
    """Spansh BeltOrRing contract."""

    name: str
    type: str
    mass: float
    innerRadius: float
    outerRadius: float
    id64: int | None = None
    signals: SpanshSpanshBeltOrRingSignalsDTO | None = None

__all__ = ('SpanshSpanshBeltOrRingSignalsDTO', 'SpanshSpanshBeltOrRingDTO')
