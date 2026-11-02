"""Data structures and domain models for the telemetry harness and audit daemon."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class TargetType(StrEnum):
    """Categorization of audit target."""

    EVENT = "event"
    STATUS_FLAG = "status_flag"
    STATUS_FLAG2 = "status_flag2"


@dataclass(frozen=True, slots=True)
class TargetDefinition:
    """Static metadata definition for an in-game telemetry or event target."""

    target_id: str
    target_type: TargetType
    chapter: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class CoverageRecord:
    """Current achievement record for an audit target."""

    target_id: str
    target_type: str
    chapter: str
    description: str
    hit_count: int
    first_seen_at: str | None
    last_seen_at: str | None


@dataclass(frozen=True, slots=True)
class DomainMismatchRecord:
    """Diagnostic record of an unhandled payload or entity hydration failure."""

    target_id: str
    error_class: str
    error_message: str
    traceback: str
    raw_payload: str
    occurred_at: str | None = None
    mismatch_id: int | None = None


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    """Outcome of processing an individual telemetry or journal envelope."""

    success: bool
    target_id: str
    chapter: str
    hydrated_object: Any | None = None
    error_message: str | None = None
    is_mismatch: bool = False
