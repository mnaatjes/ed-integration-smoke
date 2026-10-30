"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnJournalV10HeaderDTO:
    """Data transfer object for EddnJournalV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnJournalV10MessageFactionsItemDTO:
    """Data transfer object for EddnJournalV10MessageFactionsItemDTO."""

    HappiestSystem: Any | None = None
    HomeSystem: Any | None = None
    MyReputation: Any | None = None
    SquadronFaction: Any | None = None


@dataclass(frozen=True)
class EddnJournalV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    horizons: bool | None = None
    odyssey: bool | None = None
    Factions: list[EddnJournalV10MessageFactionsItemDTO] | None = None
    ActiveFine: Any | None = None
    CockpitBreach: Any | None = None
    BoostUsed: Any | None = None
    FuelLevel: Any | None = None
    FuelUsed: Any | None = None
    JumpDist: Any | None = None
    Latitude: Any | None = None
    Longitude: Any | None = None
    Wanted: Any | None = None
    IsNewEntry: Any | None = None
    NewTraitsDiscovered: Any | None = None
    Traits: Any | None = None
    VoucherAmount: Any | None = None


@dataclass(frozen=True)
class EddnJournalV10DTO:
    """Data transfer object for EddnJournalV10DTO."""

    schemaRef: str
    header: EddnJournalV10HeaderDTO
    message: EddnJournalV10MessageDTO

__all__ = ('EddnJournalV10HeaderDTO', 'EddnJournalV10MessageFactionsItemDTO', 'EddnJournalV10MessageDTO', 'EddnJournalV10DTO')
