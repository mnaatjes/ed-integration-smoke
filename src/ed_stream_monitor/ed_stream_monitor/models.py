"""Domain models and DTOs for SSE streaming events and file-delta notifications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class FileDeltaDTO:
    """Lightweight notification emitted when a monitored companion or journal file is written."""

    target: str
    action: str
    raw_hash: str
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileDeltaDTO:
        """Parse raw delta dictionary emitted over telemetry.file_delta."""
        ts_val = data.get("timestamp")
        if isinstance(ts_val, str):
            ts = datetime.fromisoformat(ts_val)
        elif isinstance(ts_val, datetime):
            ts = ts_val
        else:
            ts = datetime.now(UTC)

        return cls(
            target=str(data.get("target", "")),
            action=str(data.get("action", "modified")),
            raw_hash=str(data.get("raw_hash", "")),
            timestamp=ts,
        )


@dataclass(frozen=True, slots=True)
class StreamMessageDTO:
    """Generic envelope for any message emitted across /api/v1/events/stream."""

    topic: str
    timestamp: datetime
    raw_payload: str
    data: dict[str, Any] | None = None
