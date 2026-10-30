"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFssallbodiesfoundV10HeaderDTO:
    """Data transfer object for EddnFssallbodiesfoundV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFssallbodiesfoundV10MessageDTO:
    """Contains all properties from the listed events in the client's journal, minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    SystemName: str
    StarPos: list[float]
    SystemAddress: int
    Count: int
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnFssallbodiesfoundV10DTO:
    """Data transfer object for EddnFssallbodiesfoundV10DTO."""

    schemaRef: str
    header: EddnFssallbodiesfoundV10HeaderDTO
    message: EddnFssallbodiesfoundV10MessageDTO

__all__ = ('EddnFssallbodiesfoundV10HeaderDTO', 'EddnFssallbodiesfoundV10MessageDTO', 'EddnFssallbodiesfoundV10DTO')
