"""SSE stream monitoring client for ed-telemetry endpoints."""

from __future__ import annotations

import json
import logging
from collections.abc import Generator, Set
from datetime import UTC, datetime
from urllib.request import Request, urlopen

from ed_telemetry_client import TelemetryConnectionConfig

from .models import FileDeltaDTO, StreamMessageDTO

logger = logging.getLogger(__name__)


class TelemetryStreamMonitor:
    """Consumes real-time Server-Sent Events (SSE) from ed-telemetry with file-delta filtering."""

    def __init__(
        self,
        config: TelemetryConnectionConfig | None = None,
        stream_path: str = "/api/v1/stream",
    ) -> None:
        self.config = config or TelemetryConnectionConfig()
        self.stream_path = stream_path

    @property
    def stream_url(self) -> str:
        """Constructs target stream URL."""
        return self.config.build_url(self.stream_path)

    def _build_request(self) -> Request:
        """Builds HTTP request configuring headers for SSE streaming."""
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
        }
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return Request(self.stream_url, headers=headers)

    def listen_raw(
        self,
        timeout: float | None = None,
    ) -> Generator[StreamMessageDTO]:
        """Continuously streams raw parsed messages from the SSE feed."""
        req = self._build_request()

        with urlopen(req, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or not line.startswith("data:"):
                    continue

                payload_str = line[5:].strip()
                try:
                    payload_json = json.loads(payload_str)
                except Exception as exc:
                    logger.debug("Skipping unparseable SSE line: %s (%s)", line, exc)
                    continue

                # Skip connection handshakes
                if payload_json.get("event") == "connected":
                    continue

                topic = payload_json.get("topic", "unknown")
                ts_str = payload_json.get("timestamp")
                if isinstance(ts_str, str):
                    try:
                        ts = datetime.fromisoformat(ts_str)
                    except ValueError:
                        ts = datetime.now(UTC)
                else:
                    ts = datetime.now(UTC)

                yield StreamMessageDTO(
                    topic=topic,
                    timestamp=ts,
                    raw_payload=payload_str,
                    data=payload_json,
                )

    def listen_deltas(
        self,
        filter_targets: Set[str] | None = None,
        timeout: float | None = None,
    ) -> Generator[FileDeltaDTO]:
        """
        Continuously yields typed FileDeltaDTO notifications from the stream.

        Optionally filters deltas by target filename (e.g. {"ModulesInfo.json", "Status.json"}).
        """
        normalized_targets: set[str] | None = (
            {t.lower().removesuffix(".json") for t in filter_targets}
            if filter_targets is not None
            else None
        )

        for msg in self.listen_raw(timeout=timeout):
            if msg.topic != "telemetry.file_delta" or not msg.data:
                continue

            target_name = msg.data.get("target", "")
            if normalized_targets is not None:
                norm_name = target_name.lower().removesuffix(".json")
                if norm_name not in normalized_targets:
                    continue

            yield FileDeltaDTO.from_dict(msg.data)
