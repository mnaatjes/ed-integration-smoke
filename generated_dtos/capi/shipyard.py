"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CapiCapiShipyardResponseShipsDTO:
    """Catalog of available ships for purchase."""

    unavailable_list: list[str] | None = None


@dataclass(frozen=True)
class CapiCapiShipyardResponseDTO:
    """Available starport shipyard purchasing catalog and stored vessels."""

    id: int
    name: str
    ships: CapiCapiShipyardResponseShipsDTO | None = None

__all__ = ('CapiCapiShipyardResponseShipsDTO', 'CapiCapiShipyardResponseDTO')
