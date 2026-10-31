"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshFactionDetailsActivestatesItemDTO:
    """Data transfer object for SpanshSpanshFactionDetailsActivestatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshFactionDetailsPendingstatesItemDTO:
    """Data transfer object for SpanshSpanshFactionDetailsPendingstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshFactionDetailsRecoveringstatesItemDTO:
    """Data transfer object for SpanshSpanshFactionDetailsRecoveringstatesItemDTO."""

    state: Any
    trend: float | None = None


@dataclass(frozen=True)
class SpanshSpanshFactionDetailsDTO:
    """Full faction state"""

    name: str
    state: Any | None = None
    allegiance: Any | None = None
    government: Any | None = None
    influence: float | None = None
    activeStates: list[SpanshSpanshFactionDetailsActivestatesItemDTO] | None = None
    pendingStates: list[SpanshSpanshFactionDetailsPendingstatesItemDTO] | None = None
    recoveringStates: list[SpanshSpanshFactionDetailsRecoveringstatesItemDTO] | None = None

__all__ = ('SpanshSpanshFactionDetailsActivestatesItemDTO', 'SpanshSpanshFactionDetailsPendingstatesItemDTO', 'SpanshSpanshFactionDetailsRecoveringstatesItemDTO', 'SpanshSpanshFactionDetailsDTO')
