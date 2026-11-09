from __future__ import annotations

import threading

from ed_models import JournalEvent, StatusTelemetry

from .models import (
    ClientStateProjection,
    LocationProjection,
    SessionProjection,
    ShipProjection,
)
from .reducers import reduce_client_state


class TelemetryStateEngine:
    """Coordinates event reduction into a thread-safe materialized client state projection."""

    def __init__(self, initial_state: ClientStateProjection | None = None) -> None:
        self._lock = threading.RLock()
        self._state = initial_state or ClientStateProjection()

    @property
    def current(self) -> ClientStateProjection:
        """Returns the current immutable materialized state snapshot."""
        with self._lock:
            return self._state

    @property
    def location(self) -> LocationProjection:
        """Convenience property for current location projection."""
        with self._lock:
            return self._state.location

    @property
    def session(self) -> SessionProjection:
        """Convenience property for current session projection."""
        with self._lock:
            return self._state.session

    @property
    def ship(self) -> ShipProjection:
        """Convenience property for current ship projection."""
        with self._lock:
            return self._state.ship

    def apply(self, event: JournalEvent | StatusTelemetry) -> ClientStateProjection:
        """Applies an incoming hydrated event or status telemetry and returns the updated state."""
        with self._lock:
            self._state = reduce_client_state(self._state, event)
            return self._state

    def reset(self, new_state: ClientStateProjection | None = None) -> ClientStateProjection:
        """Resets the state engine to default or specified initial state."""
        with self._lock:
            self._state = new_state or ClientStateProjection()
            return self._state

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"TelemetryStateEngine(seq={self._state.sequence_number}, "
                f"system='{self._state.location.star_system}', "
                f"commander='{self._state.session.commander_name}')"
            )
