"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmCommanderInventoryResponseCargoItemDTO:
    """Data transfer object for EdsmCommanderInventoryResponseCargoItemDTO."""

    name: str
    qty: float
    type: Any


@dataclass(frozen=True)
class EdsmCommanderInventoryResponseDataItemDTO:
    """Data transfer object for EdsmCommanderInventoryResponseDataItemDTO."""

    name: str
    qty: float
    type: Any


@dataclass(frozen=True)
class EdsmCommanderInventoryResponseMaterialsItemDTO:
    """Data transfer object for EdsmCommanderInventoryResponseMaterialsItemDTO."""

    name: str
    qty: float
    type: Any


@dataclass(frozen=True)
class EdsmCommanderInventoryResponseDTO:
    """Commander inventory response returned by  {@link  getCommanderInventory }  request."""

    cargo: list[EdsmCommanderInventoryResponseCargoItemDTO] | None = None
    data: list[EdsmCommanderInventoryResponseDataItemDTO] | None = None
    materials: list[EdsmCommanderInventoryResponseMaterialsItemDTO] | None = None

__all__ = ('EdsmCommanderInventoryResponseCargoItemDTO', 'EdsmCommanderInventoryResponseDataItemDTO', 'EdsmCommanderInventoryResponseMaterialsItemDTO', 'EdsmCommanderInventoryResponseDTO')
