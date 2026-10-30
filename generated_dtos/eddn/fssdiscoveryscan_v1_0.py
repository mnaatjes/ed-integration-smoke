"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFssdiscoveryscanV10HeaderDTO:
    """Data transfer object for EddnFssdiscoveryscanV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFssdiscoveryscanV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    timestamp: str
    event: Any
    SystemName: str
    StarPos: list[float]
    SystemAddress: int
    BodyCount: int
    NonBodyCount: int
    horizons: bool | None = None
    odyssey: bool | None = None
    Progress: Any | None = None


@dataclass(frozen=True)
class EddnFssdiscoveryscanV10DTO:
    """Data transfer object for EddnFssdiscoveryscanV10DTO."""

    schemaRef: str
    header: EddnFssdiscoveryscanV10HeaderDTO
    message: EddnFssdiscoveryscanV10MessageDTO

__all__ = ('EddnFssdiscoveryscanV10HeaderDTO', 'EddnFssdiscoveryscanV10MessageDTO', 'EddnFssdiscoveryscanV10DTO')
