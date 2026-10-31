"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshFactionDetailsDTO:
    """Full faction state"""

    name: str
    state: Any | None = None
    allegiance: Any | None = None
    government: Any | None = None
    influence: Any | None = None
    activeStates: Any | None = None
    pendingStates: Any | None = None
    recoveringStates: Any | None = None

__all__ = ('SpanshSpanshFactionDetailsDTO',)
