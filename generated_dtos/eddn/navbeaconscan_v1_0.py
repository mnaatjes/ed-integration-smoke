"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnNavbeaconscanV10HeaderDTO:
    """Data transfer object for EddnNavbeaconscanV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnNavbeaconscanV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    NumBodies: int
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnNavbeaconscanV10DTO:
    """Data transfer object for EddnNavbeaconscanV10DTO."""

    schemaRef: str
    header: EddnNavbeaconscanV10HeaderDTO
    message: EddnNavbeaconscanV10MessageDTO

__all__ = ('EddnNavbeaconscanV10HeaderDTO', 'EddnNavbeaconscanV10MessageDTO', 'EddnNavbeaconscanV10DTO')
