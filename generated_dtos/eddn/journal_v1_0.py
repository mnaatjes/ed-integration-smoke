"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EddnJournalV10DTO:
    """Data transfer object for JournalV10."""

    schemaRef: str
    header: dict[str, Any]
    message: dict[str, Any]


__all__ = ("EddnJournalV10DTO",)
