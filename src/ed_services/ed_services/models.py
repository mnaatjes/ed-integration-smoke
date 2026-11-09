"""Derived domain events produced by ed-services calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ed_models import JournalEvent


@dataclass
class NavBearingUpdated(JournalEvent):
    """Event emitted when ship geodetic bearing to a surface destination is recomputed."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "NavBearingUpdated"
    destination_name: str = ""
    bearing_deg: float = 0.0
    distance_km: float = 0.0
    heading_deg: float | None = None
    deflection_deg: float | None = None


@dataclass
class NavDistanceUpdated(JournalEvent):
    """Event emitted when relative surface distance to a target is recomputed."""

    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event: str = "NavDistanceUpdated"
    destination_name: str = ""
    distance_km: float = 0.0
    altitude_m: float | None = None
