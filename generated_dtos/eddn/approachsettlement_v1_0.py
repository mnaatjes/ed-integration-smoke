"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnApproachsettlementV10HeaderDTO:
    """Data transfer object for EddnApproachsettlementV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnApproachsettlementV10MessageStationeconomiesItemDTO:
    """Data transfer object for EddnApproachsettlementV10MessageStationeconomiesItemDTO."""

    Name: str | None = None
    Proportion: float | None = None


@dataclass(frozen=True)
class EddnApproachsettlementV10MessageStationfactionDTO:
    """Data transfer object for EddnApproachsettlementV10MessageStationfactionDTO."""

    Name: str | None = None
    FactionState: str | None = None


@dataclass(frozen=True)
class EddnApproachsettlementV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    Name: str
    BodyID: int
    BodyName: str
    Latitude: float
    Longitude: float
    horizons: bool | None = None
    odyssey: bool | None = None
    StationGovernment: str | None = None
    StationAllegiance: str | None = None
    StationEconomies: list[EddnApproachsettlementV10MessageStationeconomiesItemDTO] | None = None
    StationFaction: EddnApproachsettlementV10MessageStationfactionDTO | None = None
    StationServices: list[str] | None = None
    StationEconomy: str | None = None
    MarketID: int | None = None


@dataclass(frozen=True)
class EddnApproachsettlementV10DTO:
    """Data transfer object for EddnApproachsettlementV10DTO."""

    schemaRef: str
    header: EddnApproachsettlementV10HeaderDTO
    message: EddnApproachsettlementV10MessageDTO

__all__ = ('EddnApproachsettlementV10HeaderDTO', 'EddnApproachsettlementV10MessageStationeconomiesItemDTO', 'EddnApproachsettlementV10MessageStationfactionDTO', 'EddnApproachsettlementV10MessageDTO', 'EddnApproachsettlementV10DTO')
