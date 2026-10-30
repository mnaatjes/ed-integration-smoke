"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EddnFsssignaldiscoveredV10HeaderDTO:
    """Data transfer object for EddnFsssignaldiscoveredV10HeaderDTO."""

    uploaderID: str
    softwareName: str
    softwareVersion: str
    gameversion: str | None = None
    gamebuild: str | None = None
    gatewayTimestamp: str | None = None


@dataclass(frozen=True)
class EddnFsssignaldiscoveredV10MessageSignalsItemDTO:
    """Single FSSSignalDiscovered event"""

    timestamp: str
    SignalName: str
    SignalType: str | None = None
    IsStation: bool | None = None
    USSType: str | None = None
    TimeRemaining: Any | None = None
    SpawningState: str | None = None
    SpawningFaction: str | None = None
    SpawningPower: str | None = None
    OpposingPower: str | None = None
    ThreatLevel: int | None = None
    patternProperties: Any | None = None


@dataclass(frozen=True)
class EddnFsssignaldiscoveredV10MessageDTO:
    """Contains all properties from the listed events in the client's journal minus Localised strings and the properties marked below as 'disallowed'"""

    event: Any
    timestamp: str
    SystemAddress: int
    signals: list[EddnFsssignaldiscoveredV10MessageSignalsItemDTO]
    StarSystem: str
    StarPos: list[float]
    horizons: bool | None = None
    odyssey: bool | None = None


@dataclass(frozen=True)
class EddnFsssignaldiscoveredV10DTO:
    """EDDN schema for FSSSignalDiscovered Journal events.  Full documentation at https://github.com/EDCD/EDDN/tree/master/schemas/fsssignaldiscovered-README.md"""

    schemaRef: str
    header: EddnFsssignaldiscoveredV10HeaderDTO
    message: EddnFsssignaldiscoveredV10MessageDTO

__all__ = ('EddnFsssignaldiscoveredV10HeaderDTO', 'EddnFsssignaldiscoveredV10MessageSignalsItemDTO', 'EddnFsssignaldiscoveredV10MessageDTO', 'EddnFsssignaldiscoveredV10DTO')
