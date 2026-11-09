"""Public API exports for ed-dispatcher package."""

from __future__ import annotations

from .dispatcher import TelemetryEventDispatcher
from .models import (
    DispatchResult,
    EventHandler,
    HandlerFailure,
    Subscription,
    TelemetryEvent,
)

__all__ = [
    "DispatchResult",
    "EventHandler",
    "HandlerFailure",
    "Subscription",
    "TelemetryEvent",
    "TelemetryEventDispatcher",
]
