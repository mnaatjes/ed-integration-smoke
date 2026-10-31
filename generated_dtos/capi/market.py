"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CapiCapiMarketResponseCommoditiesItemDTO:
    """Data transfer object for CapiCapiMarketResponseCommoditiesItemDTO."""

    id: int
    name: str
    buyPrice: int
    sellPrice: int
    stock: int
    demand: int
    meanPrice: int | None = None
    demandBracket: int | None = None
    stockBracket: int | None = None
    categoryname: str | None = None


@dataclass(frozen=True)
class CapiCapiMarketResponseDTO:
    """Starport commodity market pricing, supply, demand, and brackets."""

    id: int
    name: str
    commodities: list[CapiCapiMarketResponseCommoditiesItemDTO]

__all__ = ('CapiCapiMarketResponseCommoditiesItemDTO', 'CapiCapiMarketResponseDTO')
