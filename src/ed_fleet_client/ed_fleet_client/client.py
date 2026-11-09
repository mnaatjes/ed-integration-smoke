"""Unified reactive client facade coordinating telemetry streaming, state reduction,
and event dispatch.
"""

from __future__ import annotations

import logging
import threading
import time
import urllib.parse
from collections.abc import Callable, Generator
from typing import Any, TypeVar

from ed_hydrator.hydrator import TelemetryDomainHydrator
from ed_models import JournalEvent, StatusTelemetry
from ed_services.navigation import NavigationService

from ed_dispatcher import DispatchResult, EventHandler, Subscription, TelemetryEventDispatcher
from ed_reducer import ClientStateProjection, TelemetryStateEngine
from ed_stream_monitor import TelemetryStreamMonitor
from ed_telemetry_client import (
    TelemetryConnectionConfig,
    TelemetryHttpClient,
    TelemetryResponseDTO,
)

E = TypeVar("E", bound=JournalEvent | StatusTelemetry)
logger = logging.getLogger(__name__)


class EliteDangerousClient:
    """Unified client facade for Elite Dangerous telemetry and domain event streams."""

    def __init__(
        self,
        endpoint: str = "http://localhost:8080",
        *,
        timeout: float = 10.0,
        auto_poll_status_interval: float | None = 2.0,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self._timeout = timeout
        self._auto_poll_interval = auto_poll_status_interval

        parsed = urllib.parse.urlparse(self.endpoint)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 8080)

        config = TelemetryConnectionConfig(host=host, port=port, timeout=timeout)
        self._http = TelemetryHttpClient(config=config)
        self._monitor = TelemetryStreamMonitor(config=config)
        self._hydrator = TelemetryDomainHydrator()
        self._state_engine = TelemetryStateEngine()
        self._dispatcher = TelemetryEventDispatcher()

        # Mount Domain Services
        self.nav = NavigationService(
            state_accessor=lambda: self.state,
            dispatcher=self._dispatcher,
        )

        # Lifecycle synchronization
        self._running = False
        self._worker_thread: threading.Thread | None = None
        self._lock = threading.RLock()

    # =========================================================================
    # Group B: Materialized State Projections
    # =========================================================================

    @property
    def state(self) -> ClientStateProjection:
        """Returns the current immutable materialized client state projection."""
        return self._state_engine.current

    # =========================================================================
    # Group A: Reactive Subscriptions
    # =========================================================================

    def on(self, event_type: type[E]) -> Callable[[EventHandler], EventHandler]:
        """Decorator registering a callback for a specific hydrated ed-models domain event type."""
        return self._dispatcher.on(event_type)

    def subscribe(self, event_type: type[E], handler: EventHandler) -> Subscription:
        """Programmatically registers an event handler for a specific domain event type."""
        return self._dispatcher.subscribe(event_type, handler)

    def unsubscribe(self, subscription: Subscription | str) -> bool:
        """Detaches an active subscription token."""
        return self._dispatcher.unsubscribe(subscription)

    # =========================================================================
    # Group C: On-Demand Query Services
    # =========================================================================

    def get_status(self) -> StatusTelemetry | None:
        """Queries the live cockpit status endpoint and updates internal ship telemetry state."""
        try:
            resp: TelemetryResponseDTO[Any] = self._http.get_status()
            status = self._hydrator.hydrate_status(resp.data)
            if status is not None:
                self._ingest_event(status)
            return status
        except Exception as ex:
            logger.warning(f"Failed to fetch status telemetry: {ex}")
            return None

    def get_latest_journal(self) -> JournalEvent | None:
        """Queries the latest Frontier journal event and updates internal state."""
        try:
            resp: TelemetryResponseDTO[Any] = self._http.get_latest_journal()
            event = self._hydrator.hydrate_event(resp.data)
            if event is not None:
                self._ingest_event(event)
            return event
        except Exception as ex:
            logger.warning(f"Failed to fetch latest journal event: {ex}")
            return None

    def query_events(
        self,
        *,
        topic: str | None = None,
        since_id: int | None = None,
        limit: int = 100,
        order: str = "desc",
    ) -> list[JournalEvent]:
        """Queries historical telemetry events and returns hydrated domain models."""
        try:
            resp: TelemetryResponseDTO[Any] = self._http.query_events(
                topic=topic,
                since_id=since_id,
                limit=limit,
                order=order,
            )
            raw_list = resp.data if isinstance(resp.data, list) else []
            hydrated: list[JournalEvent] = []
            for item in raw_list:
                ev = self._hydrator.hydrate_event(item)
                if ev is not None:
                    hydrated.append(ev)
            return hydrated
        except Exception as ex:
            logger.warning(f"Failed to query events: {ex}")
            return []

    # =========================================================================
    # Group D: Lifecycle & Stream Processing
    # =========================================================================

    def _ingest_event(self, event: JournalEvent | StatusTelemetry) -> DispatchResult:
        """Internal pipeline: folds event through state reducer first, then notifies listeners."""
        with self._lock:
            # 1. State Reduction (Guarantee: state is up-to-date before listeners fire)
            self._state_engine.apply(event)
            # 2. Dispatch to Subscribed Observers
            return self._dispatcher.dispatch(event)

    def stream(self) -> Generator[JournalEvent | StatusTelemetry]:
        """Yields hydrated events in real time by monitoring file deltas and journal updates."""
        for delta in self._monitor.listen_deltas():
            if not self._running:
                break

            target = delta.target
            # If Status.json was updated, resolve cockpit status
            if target == "Status.json":
                status = self.get_status()
                if status is not None:
                    yield status
            # If active journal log was updated, fetch and hydrate latest journal event
            elif target.startswith("Journal.") and target.endswith(".log"):
                ev = self.get_latest_journal()
                if ev is not None:
                    yield ev

    def _run_worker(self) -> None:
        """Worker loop monitoring streaming deltas and optionally polling cockpit status."""
        last_poll = time.monotonic()

        while self._running:
            try:
                for _event in self.stream():
                    if not self._running:
                        break
                    # Periodic cockpit status poll if enabled and idle
                    if (
                        self._auto_poll_interval
                        and time.monotonic() - last_poll >= self._auto_poll_interval
                    ):
                        self.get_status()
                        last_poll = time.monotonic()

            except Exception as ex:
                if self._running:
                    logger.warning(f"Telemetry stream interrupted: {ex}; reconnecting in 2s...")
                    time.sleep(2.0)

    def start_background(self) -> None:
        """Starts background telemetry ingestion on a dedicated daemon thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            # Initial seed of cockpit and session state
            self.get_status()
            self.get_latest_journal()

            self._worker_thread = threading.Thread(
                target=self._run_worker,
                daemon=True,
                name="EliteDangerousClientWorker",
            )
            self._worker_thread.start()

    def stop(self) -> None:
        """Stops background telemetry streaming."""
        with self._lock:
            self._running = False
            if self._worker_thread and self._worker_thread.is_alive():
                self._worker_thread.join(timeout=1.0)
            self._worker_thread = None

    def start(self) -> None:
        """Blocks and runs the client stream loop synchronously until interrupted."""
        self._running = True
        self.get_status()
        self.get_latest_journal()
        try:
            for _ in self.stream():
                pass
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def __enter__(self) -> EliteDangerousClient:
        self.start_background()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()
