"""Network client communicating across the LAN to remote ed-telemetry service."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from ed_transport import AsyncTransportClient, HttpRequestDTO, create_async_transport_client

logger = logging.getLogger(__name__)


class TelemetryIngressClient:
    """Consumes telemetry payloads from a remote ed-telemetry host over HTTP/LAN."""

    def __init__(
        self,
        base_url: str,
        transport: AsyncTransportClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.transport = transport or create_async_transport_client()

    async def fetch_game_status(self) -> dict[str, Any] | None:
        """Query active cockpit Status.json snapshot via /api/v1/status/game."""
        url = f"{self.base_url}/api/v1/status/game"
        request = HttpRequestDTO(method="GET", url=url)
        try:
            response = await self.transport.send_async(request)
            if response.status_code == 200:
                wrapper: dict[str, Any] = json.loads(response.body.decode("utf-8"))
                raw_payload = wrapper.get("raw_payload")
                if isinstance(raw_payload, str):
                    parsed: dict[str, Any] = json.loads(raw_payload)
                    return parsed
                elif isinstance(raw_payload, dict):
                    return raw_payload
        except Exception as exc:
            logger.error("Failed to query game status from %s: %s", url, exc)
        return None

    async def fetch_recent_events(self, since_id: int = 0) -> list[tuple[int, dict[str, Any]]]:
        """Query recent journal events via /api/v1/events returning (event_id, payload) tuples."""
        url = f"{self.base_url}/api/v1/events?since_id={since_id}&limit=100"
        request = HttpRequestDTO(method="GET", url=url)
        try:
            response = await self.transport.send_async(request)
            if response.status_code == 200:
                items: list[dict[str, Any]] = json.loads(response.body.decode("utf-8"))
                results: list[tuple[int, dict[str, Any]]] = []
                for item in items:
                    item_id = int(item.get("id", 0))
                    raw = (
                        item.get("payload_json")
                        or item.get("payload")
                        or item.get("raw_payload")
                    )
                    if isinstance(raw, str):
                        try:
                            results.append((item_id, json.loads(raw)))
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(raw, dict):
                        results.append((item_id, raw))
                return results
        except Exception as exc:
            logger.error("Failed to query events from %s: %s", url, exc)
        return []

    async def poll_stream(self, interval_seconds: float = 1.0) -> AsyncIterator[dict[str, Any]]:
        """Poll remote telemetry endpoint at regular intervals."""
        while not self.transport.is_closed():
            status = await self.fetch_game_status()
            if status:
                yield status
            await asyncio.sleep(interval_seconds)

    async def aclose(self) -> None:
        """Close transport client."""
        await self.transport.aclose()
