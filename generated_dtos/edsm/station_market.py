"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmStationMarketResponseCommoditiesItemDTO:
    """Data transfer object for EdsmStationMarketResponseCommoditiesItemDTO."""

    buyPrice: float
    demand: float
    id: Any
    name: str
    sellPrice: float
    stock: float
    stockBracket: float


@dataclass(frozen=True)
class EdsmStationMarketResponseDTO:
    """Response structure of the EDSM system stations market request."""

    commodities: list[EdsmStationMarketResponseCommoditiesItemDTO]
    id: float
    id64: Any
    marketId: float
    name: str
    sId: float
    sName: str
    url: str

__all__ = ('EdsmStationMarketResponseCommoditiesItemDTO', 'EdsmStationMarketResponseDTO')
