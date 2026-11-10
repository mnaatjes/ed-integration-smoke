"""Public API exports for ed-fleet-client package."""

from __future__ import annotations

from ed_services.models import (
    BodyPositionPropagated,
    CombatDiagnosticsUpdated,
    HabitableZoneEvaluated,
    NavBearingUpdated,
    NavDistanceUpdated,
    PerformanceMetricsUpdated,
    RouteProgressUpdated,
    TargetLockedUpdated,
)

from ed_dispatcher import DispatchResult, EventHandler, Subscription
from ed_reducer import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)

from .client import EliteDangerousClient

__all__ = [
    "BodyPositionPropagated",
    "ClientStateProjection",
    "CombatDiagnosticsUpdated",
    "DispatchResult",
    "EliteDangerousClient",
    "EventHandler",
    "HabitableZoneEvaluated",
    "LocationProjection",
    "NavBearingUpdated",
    "NavDistanceUpdated",
    "PerformanceMetricsUpdated",
    "RouteProgressUpdated",
    "SessionProjection",
    "ShipProjection",
    "Subscription",
    "TargetLockedUpdated",
]
