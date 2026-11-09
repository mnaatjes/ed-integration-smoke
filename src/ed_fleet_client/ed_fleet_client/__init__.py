"""Public API exports for ed-fleet-client package."""

from __future__ import annotations

from ed_services.models import NavBearingUpdated, NavDistanceUpdated

from ed_dispatcher import DispatchResult, EventHandler, Subscription
from ed_reducer import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)

from .client import EliteDangerousClient

__all__ = [
    "ClientStateProjection",
    "DispatchResult",
    "EliteDangerousClient",
    "EventHandler",
    "LocationProjection",
    "NavBearingUpdated",
    "NavDistanceUpdated",
    "SessionProjection",
    "ShipProjection",
    "Subscription",
]
