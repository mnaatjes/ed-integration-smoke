"""Navigation calculation engine and reactive stream deriver."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable

from ed_models import StatusTelemetry
from ed_models.core.domain.events import ApproachSettlement

from ed_dispatcher import Subscription, TelemetryEventDispatcher
from ed_reducer import ClientStateProjection

from .base import TelemetryService
from .models import NavBearingUpdated, NavDistanceUpdated


def calculate_great_circle_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates initial great-circle bearing (degrees 0.0 to 360.0) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)

    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360.0) % 360.0
    return round(bearing, 2)


def calculate_surface_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float = 6371.0
) -> float:
    """Calculates great-circle distance in kilometers using the Haversine formula."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(radius_km * c, 2)


class NavigationService(TelemetryService):
    """Provides geodetic navigation calculations and reactive stream derivation."""

    def __init__(
        self,
        state_accessor: Callable[[], ClientStateProjection],
        dispatcher: TelemetryEventDispatcher,
    ) -> None:
        self._lock = threading.RLock()
        self._target_name: str | None = None
        self._target_lat: float | None = None
        self._target_lon: float | None = None
        self._target_radius_km: float = 6371.0
        self._subscriptions: list[Subscription] = []
        super().__init__(state_accessor, dispatcher)

    # =========================================================================
    # Pattern 1: State-Guarded Pull Methods
    # =========================================================================

    def get_destination(self) -> tuple[str, float, float] | None:
        """Returns the current destination (name, latitude, longitude) or None if unset."""
        with self._lock:
            if self._target_name and self._target_lat is not None and self._target_lon is not None:
                return (self._target_name, self._target_lat, self._target_lon)
            return None

    def set_destination(
        self, name: str, latitude: float, longitude: float, planet_radius_km: float = 6371.0
    ) -> None:
        """Manually sets a navigation destination waypoint."""
        with self._lock:
            self._target_name = name
            self._target_lat = latitude
            self._target_lon = longitude
            self._target_radius_km = planet_radius_km
            self._evaluate_and_dispatch()

    def clear_destination(self) -> None:
        """Clears the active navigation target."""
        with self._lock:
            self._target_name = None
            self._target_lat = None
            self._target_lon = None

    @property
    def target_name(self) -> str | None:
        """Returns the currently targeted destination settlement name, if set."""
        with self._lock:
            return self._target_name

    def bearing_to_target(self) -> float | None:
        """Calculates initial great-circle bearing to destination, or None if inputs unavailable."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None:
                return None

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return None

            return calculate_great_circle_bearing(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
            )

    def distance_to_target_km(self) -> float | None:
        """Calculates surface distance in kilometers to destination, or None if unavailable."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None:
                return None

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return None

            radius_km = (
                telemetry.planet_radius / 1000.0
                if telemetry.planet_radius
                else self._target_radius_km
            )
            return calculate_surface_distance_km(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
                radius_km=radius_km,
            )

    # =========================================================================
    # Pattern 2: Reactive Stream Pipe
    # =========================================================================

    def _evaluate_and_dispatch(self) -> None:
        """Internal evaluator that dispatches derived events once all parameters are valid."""
        with self._lock:
            if self._target_lat is None or self._target_lon is None or not self._target_name:
                return

            state = self._get_state()
            telemetry = state.ship.telemetry
            if not telemetry or telemetry.latitude is None or telemetry.longitude is None:
                return

            radius_km = (
                telemetry.planet_radius / 1000.0
                if telemetry.planet_radius
                else self._target_radius_km
            )
            bearing = calculate_great_circle_bearing(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
            )
            distance = calculate_surface_distance_km(
                telemetry.latitude,
                telemetry.longitude,
                self._target_lat,
                self._target_lon,
                radius_km=radius_km,
            )

            heading = telemetry.heading
            deflection = (
                ((bearing - heading + 180.0) % 360.0) - 180.0 if heading is not None else None
            )

            # Dispatch derived events onto the client's event bus
            bearing_ev = NavBearingUpdated(
                destination_name=self._target_name,
                bearing_deg=bearing,
                distance_km=distance,
                heading_deg=heading,
                deflection_deg=round(deflection, 2) if deflection is not None else None,
            )
            self._dispatcher.dispatch(bearing_ev)

            distance_ev = NavDistanceUpdated(
                destination_name=self._target_name,
                distance_km=distance,
                altitude_m=telemetry.altitude,
            )
            self._dispatcher.dispatch(distance_ev)

    def attach(self) -> None:
        """Subscribes to StatusTelemetry and ApproachSettlement to drive derivation."""
        if self._attached:
            return

        def _on_status(event: StatusTelemetry) -> None:
            self._evaluate_and_dispatch()

        def _on_settlement(event: ApproachSettlement) -> None:
            lat = getattr(event, "Latitude", None)
            lon = getattr(event, "Longitude", None)
            name = getattr(event, "Name", "Surface Settlement")
            if lat is not None and lon is not None:
                with self._lock:
                    self._target_name = name
                    self._target_lat = float(lat)
                    self._target_lon = float(lon)
                    self._evaluate_and_dispatch()

        sub_status = self._dispatcher.subscribe(StatusTelemetry, _on_status)
        sub_settlement = self._dispatcher.subscribe(ApproachSettlement, _on_settlement)
        self._subscriptions.extend([sub_status, sub_settlement])
        self._attached = True

    def detach(self) -> None:
        """Unsubscribes from the event bus."""
        for sub in self._subscriptions:
            self._dispatcher.unsubscribe(sub)
        self._subscriptions.clear()
        self._attached = False
