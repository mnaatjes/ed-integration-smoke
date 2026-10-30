"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraBatchEnvelopeHeaderDTO:
    """Data transfer object for InaraInaraBatchEnvelopeHeaderDTO."""

    appName: str
    appVersion: str
    APIkey: str
    isBeingDeveloped: bool | None = None
    commanderName: str | None = None
    commanderFrontierID: str | None = None


@dataclass(frozen=True)
class InaraInaraBatchEnvelopeEventsItemDTO:
    """Data transfer object for InaraInaraBatchEnvelopeEventsItemDTO."""

    eventName: str
    eventTimestamp: str
    eventData: dict[str, Any]
    eventCustomID: int | None = None


@dataclass(frozen=True)
class InaraInaraBatchEnvelopeDTO:
    """Standard root batch request envelope for the Inara API v1."""

    header: InaraInaraBatchEnvelopeHeaderDTO
    events: list[InaraInaraBatchEnvelopeEventsItemDTO]

__all__ = ('InaraInaraBatchEnvelopeHeaderDTO', 'InaraInaraBatchEnvelopeEventsItemDTO', 'InaraInaraBatchEnvelopeDTO')
