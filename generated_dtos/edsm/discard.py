"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmEdsmDiscardResponseDTO:
    """List of journal event names that EDSM discards from telemetry ingestion."""

    discardedEvents: list[str]

__all__ = ('EdsmEdsmDiscardResponseDTO',)
