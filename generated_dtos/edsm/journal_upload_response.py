"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmEdsmJournalUploadResponseEventsItemDTO:
    """Data transfer object for EdsmEdsmJournalUploadResponseEventsItemDTO."""

    msgnum: int
    msg: str


@dataclass(frozen=True)
class EdsmEdsmJournalUploadResponseDTO:
    """Response envelope returned by EDSM /api-journal-v1 upload endpoint."""

    msgnum: int
    msg: str
    events: list[EdsmEdsmJournalUploadResponseEventsItemDTO]

__all__ = ('EdsmEdsmJournalUploadResponseEventsItemDTO', 'EdsmEdsmJournalUploadResponseDTO')
