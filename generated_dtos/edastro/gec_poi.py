"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdAstroEDAstroGecPoiDTO:
    """Galactic Exploration Catalog (GEC) Point of Interest record formatted according to the EDSM GMP-JSON schema."""

    id: int
    name: str
    type: str
    coordinates: list[float]
    source: str | None = None
    type2: Any | None = None
    categoryId: int | None = None
    categoryId2: int | None = None
    region: Any | None = None
    galMapSearch: Any | None = None
    galMapUrl: Any | None = None
    summary: Any | None = None
    descriptionMardown: Any | None = None
    descriptionHtml: Any | None = None
    solDistance: Any | None = None
    id64: Any | None = None
    rating: Any | None = None
    curation: Any | None = None
    avgStars: Any | None = None
    votes: Any | None = None
    poiUrl: Any | None = None
    mainImage: Any | None = None
    callsign: Any | None = None
    rare: Any | None = None

__all__ = ('EdAstroEDAstroGecPoiDTO',)
