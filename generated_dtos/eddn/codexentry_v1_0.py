"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnCodexentryV10HeaderDTO:
    """Data transfer object for EddnCodexentryV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnCodexentryV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    System: str
    StarPos: list[float]
    SystemAddress: int
    EntryID: int
    horizons: bool | None = None
    odyssey: bool | None = None
    Name: str | None = None
    Region: str | None = None
    Category: str | None = None
    Latitude: float | None = None
    Longitude: float | None = None
    SubCategory: str | None = None
    NearestDestination: str | None = None
    VoucherAmount: int | None = None
    Traits: list[str] | None = None
    BodyID: int | None = None
    BodyName: str | None = None
    IsNewEntry: Any | None = None
    NewTraitsDiscovered: Any | None = None


@dataclass(frozen=True)
class EddnCodexentryV10DTO:
    """EDDN schema for CodexEntry Journal events.  Full documentation at https://github.com/EDCD/EDDN/tree/master/schemas/codexentry-README.md"""

    schemaRef: str
    header: EddnCodexentryV10HeaderDTO
    message: EddnCodexentryV10MessageDTO

__all__ = ('EddnCodexentryV10HeaderDTO', 'EddnCodexentryV10MessageDTO', 'EddnCodexentryV10DTO')
