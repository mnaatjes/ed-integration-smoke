"""Remedial structured JSON logger conforming to RFC 0001."""

from __future__ import annotations

import datetime
import json
import logging
import sys
from typing import Any


class StructuredJsonLogger:
    """Remedial logger emitting RFC 0001 compliant structured JSON events."""

    def __init__(self, name: str = "ed_integration_smoke") -> None:
        self.name = name
        self._records: list[dict[str, Any]] = []
        self._std_logger = logging.getLogger(name)

    @property
    def records(self) -> list[dict[str, Any]]:
        """Returns in-memory journal of all recorded structured log events."""
        return list(self._records)

    def clear(self) -> None:
        """Clears logged records."""
        self._records.clear()

    def log_event(
        self,
        level: str,
        event: str,
        *,
        target: dict[str, Any] | None = None,
        schema: dict[str, Any] | None = None,
        error: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Constructs, journals, and formats an RFC 0001 structured log event."""
        timestamp = (
            datetime.datetime.now(datetime.timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
        record: dict[str, Any] = {
            "timestamp": timestamp,
            "level": level.upper(),
            "logger": self.name,
            "event": event,
        }

        if target is not None:
            record["target"] = target
        if schema is not None:
            record["schema"] = schema
        if error is not None:
            record["error"] = error
        if message is not None:
            record["message"] = message

        self._records.append(record)

        # Output to stdout/logger
        formatted_json = json.dumps(record)
        log_method = getattr(self._std_logger, level.lower(), self._std_logger.info)
        log_method(formatted_json)

        return record

    def info(self, event: str, **kwargs: Any) -> dict[str, Any]:
        return self.log_event("INFO", event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> dict[str, Any]:
        return self.log_event("WARNING", event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> dict[str, Any]:
        return self.log_event("ERROR", event, **kwargs)


__all__ = ["StructuredJsonLogger"]
