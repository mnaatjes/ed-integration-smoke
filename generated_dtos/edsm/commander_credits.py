"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmCommanderCreditsResponseCreditsItemDTO:
    """Data transfer object for EdsmCommanderCreditsResponseCreditsItemDTO."""

    balance: float
    date: str
    loan: float


@dataclass(frozen=True)
class EdsmCommanderCreditsResponseDTO:
    """Commander credits response returned by  {@link  getCommanderCredits }  request."""

    credits: list[EdsmCommanderCreditsResponseCreditsItemDTO]
    period: str | None = None

__all__ = ('EdsmCommanderCreditsResponseCreditsItemDTO', 'EdsmCommanderCreditsResponseDTO')
