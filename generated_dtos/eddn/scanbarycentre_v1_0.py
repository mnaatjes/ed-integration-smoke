"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnScanbarycentreV10HeaderDTO:
    """Data transfer object for EddnScanbarycentreV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnScanbarycentreV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    BodyID: int
    horizons: bool | None = None
    odyssey: bool | None = None
    SemiMajorAxis: float | None = None
    Eccentricity: float | None = None
    OrbitalInclination: float | None = None
    Periapsis: float | None = None
    OrbitalPeriod: float | None = None
    AscendingNode: float | None = None
    MeanAnomaly: float | None = None


@dataclass(frozen=True)
class EddnScanbarycentreV10DTO:
    """Data transfer object for EddnScanbarycentreV10DTO."""

    schemaRef: str
    header: EddnScanbarycentreV10HeaderDTO
    message: EddnScanbarycentreV10MessageDTO

__all__ = ('EddnScanbarycentreV10HeaderDTO', 'EddnScanbarycentreV10MessageDTO', 'EddnScanbarycentreV10DTO')
