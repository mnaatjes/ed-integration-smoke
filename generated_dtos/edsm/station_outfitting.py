"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmStationOutfittingResponseOutfittingItemDTO:
    """Data transfer object for EdsmStationOutfittingResponseOutfittingItemDTO."""

    id: Any
    name: str


@dataclass(frozen=True)
class EdsmStationOutfittingResponseDTO:
    """Response structure of the EDSM system stations outfitting request."""

    id: float
    id64: Any
    marketId: float
    name: str
    outfitting: list[EdsmStationOutfittingResponseOutfittingItemDTO]
    sId: float
    sName: str
    url: str

__all__ = ('EdsmStationOutfittingResponseOutfittingItemDTO', 'EdsmStationOutfittingResponseDTO')
