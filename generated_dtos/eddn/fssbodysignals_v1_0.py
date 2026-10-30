"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFssbodysignalsV10HeaderDTO:
    """Data transfer object for EddnFssbodysignalsV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFssbodysignalsV10MessageSignalsItemDTO:
    """Data transfer object for EddnFssbodysignalsV10MessageSignalsItemDTO."""

    Type: str
    Count: int


@dataclass(frozen=True)
class EddnFssbodysignalsV10MessageDTO:
    """Contains all properties from the listed events in the client's journal, minus the Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    StarSystem: str
    StarPos: list[float]
    SystemAddress: int
    BodyID: int
    Signals: list[EddnFssbodysignalsV10MessageSignalsItemDTO]
    horizons: bool | None = None
    odyssey: bool | None = None
    BodyName: str | None = None


@dataclass(frozen=True)
class EddnFssbodysignalsV10DTO:
    """Data transfer object for EddnFssbodysignalsV10DTO."""

    schemaRef: str
    header: EddnFssbodysignalsV10HeaderDTO
    message: EddnFssbodysignalsV10MessageDTO

__all__ = ('EddnFssbodysignalsV10HeaderDTO', 'EddnFssbodysignalsV10MessageSignalsItemDTO', 'EddnFssbodysignalsV10MessageDTO', 'EddnFssbodysignalsV10DTO')
