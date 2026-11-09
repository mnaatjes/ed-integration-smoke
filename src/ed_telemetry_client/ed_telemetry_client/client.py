"""Reusable HTTP client connecting to ed-telemetry endpoints via ed-transport."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from ed_transport.adapters.driving.client import TransportClient
from ed_transport.bootstrap.client_factory import create_transport_client

from .middleware import MetadataHydrationMiddleware
from .models import TelemetryConnectionConfig, TelemetryResponseDTO


class TelemetryHttpClient:
    """Synchronous client querying ed-telemetry REST endpoints with metadata hydration."""

    def __init__(
        self,
        config: TelemetryConnectionConfig | None = None,
        *,
        transport_client: TransportClient | None = None,
        middleware: MetadataHydrationMiddleware | None = None,
    ) -> None:
        self.config = config or TelemetryConnectionConfig()
        self._transport_client = transport_client or create_transport_client(
            default_timeout=self.config.timeout
        )
        self._middleware = middleware or MetadataHydrationMiddleware()

    def __enter__(self) -> TelemetryHttpClient:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes underlying transport resources."""
        self._transport_client.close()

    def _prepare_headers(
        self,
        custom_headers: Mapping[str, str] | None = None,
        if_none_match: str | None = None,
    ) -> dict[str, str]:
        """Prepares request headers injecting API key and ETag cache validators."""
        headers: dict[str, str] = dict(custom_headers) if custom_headers else {}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        return headers

    def request(
        self,
        path: str | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        if_none_match: str | None = None,
        timeout: float | None = None,
    ) -> TelemetryResponseDTO[Any]:
        """Dispatches an HTTP GET request to the target path and returns hydrated DTO."""
        url = self.config.build_url(path)
        req_headers = self._prepare_headers(headers, if_none_match=if_none_match)
        req_timeout = timeout if timeout is not None else self.config.timeout

        start = time.perf_counter()
        http_response = self._transport_client.get(
            url=url,
            headers=req_headers,
            params=params,
            timeout=req_timeout,
        )
        latency_ms = (time.perf_counter() - start) * 1000.0

        return self._middleware.hydrate(
            endpoint_url=url,
            response=http_response,
            latency_ms=latency_ms,
        )

    def get_state(self, if_none_match: str | None = None) -> TelemetryResponseDTO[Any]:
        """Retrieves consolidated state from GET /api/v1/state."""
        return self.request("/api/v1/state", if_none_match=if_none_match)

    def get_state_heartbeat(self, if_none_match: str | None = None) -> TelemetryResponseDTO[Any]:
        """Retrieves lightweight state heartbeat from GET /api/v1/state/heartbeat."""
        return self.request("/api/v1/state/heartbeat", if_none_match=if_none_match)

    def get_status(self) -> TelemetryResponseDTO[Any]:
        """Retrieves cockpit game status from GET /api/v1/status."""
        return self.request("/api/v1/status")

    def get_snapshots(self) -> TelemetryResponseDTO[Any]:
        """Retrieves all registered snapshots map from GET /api/v1/snapshots."""
        return self.request("/api/v1/snapshots")

    def get_snapshot(self, name: str) -> TelemetryResponseDTO[Any]:
        """Retrieves a specific auxiliary snapshot from GET /api/v1/snapshots/{name}."""
        return self.request(f"/api/v1/snapshots/{name}")

    def get_latest_journal(self) -> TelemetryResponseDTO[Any]:
        """Retrieves latest journal event from GET /api/v1/journal/latest."""
        return self.request("/api/v1/journal/latest")

    def get_journal_events(
        self,
        topic: str | None = None,
        since_id: int | None = None,
        limit: int = 100,
        order: str = "asc",
    ) -> TelemetryResponseDTO[Any]:
        """Queries historical Frontier journal events from GET /api/v1/journal/events."""
        params: dict[str, str] = {"limit": str(limit), "order": order}
        if topic is not None:
            params["topic"] = topic
        if since_id is not None:
            params["since_id"] = str(since_id)
        return self.request("/api/v1/journal/events", params=params)

    def query_events(
        self,
        topic: str | None = None,
        since_id: int | None = None,
        limit: int = 100,
        order: str = "asc",
    ) -> TelemetryResponseDTO[Any]:
        """Queries the unified multi-topic event store from GET /api/v1/events/query."""
        params: dict[str, str] = {"limit": str(limit), "order": order}
        if topic is not None:
            params["topic"] = topic
        if since_id is not None:
            params["since_id"] = str(since_id)
        return self.request("/api/v1/events/query", params=params)

    def drain_events_queue(self, limit: int = 100) -> TelemetryResponseDTO[Any]:
        """Drains uncommitted events from outbound ring buffer via GET /api/v1/events/queue."""
        return self.request("/api/v1/events/queue", params={"limit": str(limit)})

    def get_system_health(self) -> TelemetryResponseDTO[Any]:
        """Retrieves service health status from GET /api/v1/system/health."""
        return self.request("/api/v1/system/health")
