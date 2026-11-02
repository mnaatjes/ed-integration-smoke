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

    async def fetch_current_status(self) -> dict[str, Any] | None:
        """Query remote status snapshot."""
        url = f"{self.base_url}/status"
        request = HttpRequestDTO(method="GET", url=url)
        try:
            response = await self.transport.send_async(request)
            if response.status_code == 200:
                data: dict[str, Any] = json.loads(response.body.decode("utf-8"))
                return data
        except Exception as exc:
            logger.error("Failed to query remote status from %s: %s", url, exc)
        return None

    async def poll_stream(self, interval_seconds: float = 1.0) -> AsyncIterator[dict[str, Any]]:
        """Poll remote telemetry endpoint at regular intervals."""
        while not self.transport.is_closed():
            status = await self.fetch_current_status()
            if status:
                yield status
            await asyncio.sleep(interval_seconds)

    async def aclose(self) -> None:
        """Close transport client."""
        await self.transport.aclose()
