"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFcmaterialsJournalV10HeaderDTO:
    """Data transfer object for EddnFcmaterialsJournalV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFcmaterialsJournalV10MessageItemsItemDTO:
    """Data transfer object for EddnFcmaterialsJournalV10MessageItemsItemDTO."""

    id: int
    Name: str
    Price: int
    Stock: int
    Demand: int


@dataclass(frozen=True)
class EddnFcmaterialsJournalV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    MarketID: int
    CarrierName: str
    CarrierID: str
    Items: list[EddnFcmaterialsJournalV10MessageItemsItemDTO]
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnFcmaterialsJournalV10DTO:
    """Data transfer object for EddnFcmaterialsJournalV10DTO."""

    schemaRef: str
    header: EddnFcmaterialsJournalV10HeaderDTO
    message: EddnFcmaterialsJournalV10MessageDTO

__all__ = ('EddnFcmaterialsJournalV10HeaderDTO', 'EddnFcmaterialsJournalV10MessageItemsItemDTO', 'EddnFcmaterialsJournalV10MessageDTO', 'EddnFcmaterialsJournalV10DTO')
