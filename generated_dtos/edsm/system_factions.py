"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemFactionsResponseFactionsItemActivestatesItemDTO:
    """Data transfer object for EdsmSystemFactionsResponseFactionsItemActivestatesItemDTO."""

    state: str


@dataclass(frozen=True)
class EdsmSystemFactionsResponseFactionsItemPendingstatesItemDTO:
    """Data transfer object for EdsmSystemFactionsResponseFactionsItemPendingstatesItemDTO."""

    state: str
    trend: float | None = None


@dataclass(frozen=True)
class EdsmSystemFactionsResponseFactionsItemRecoveringstatesItemDTO:
    """Data transfer object for EdsmSystemFactionsResponseFactionsItemRecoveringstatesItemDTO."""

    state: str
    trend: float | None = None


@dataclass(frozen=True)
class EdsmSystemFactionsResponseFactionsItemDTO:
    """Data transfer object for EdsmSystemFactionsResponseFactionsItemDTO."""

    activeStates: list[EdsmSystemFactionsResponseFactionsItemActivestatesItemDTO]
    allegiance: str
    government: str
    happiness: str
    id: float
    influence: float
    isPlayer: bool
    lastUpdate: float
    name: str
    pendingStates: list[EdsmSystemFactionsResponseFactionsItemPendingstatesItemDTO]
    recoveringStates: list[EdsmSystemFactionsResponseFactionsItemRecoveringstatesItemDTO]
    state: str
    activeStatesHistory: Any | None = None
    happinessHistory: Any | None = None
    influenceHistory: Any | None = None
    pendingStatesHistory: Any | None = None
    recoveringStatesHistory: Any | None = None
    stateHistory: Any | None = None


@dataclass(frozen=True)
class EdsmSystemFactionsResponseControllingfactionDTO:
    """Data transfer object for EdsmSystemFactionsResponseControllingfactionDTO."""

    allegiance: str
    government: str
    id: float
    name: str


@dataclass(frozen=True)
class EdsmSystemFactionsResponseDTO:
    """Response structure of the EDSM system factions request."""

    factions: list[EdsmSystemFactionsResponseFactionsItemDTO]
    id: float
    id64: Any
    name: str
    url: str
    controllingFaction: EdsmSystemFactionsResponseControllingfactionDTO | None = None

__all__ = ('EdsmSystemFactionsResponseFactionsItemActivestatesItemDTO', 'EdsmSystemFactionsResponseFactionsItemPendingstatesItemDTO', 'EdsmSystemFactionsResponseFactionsItemRecoveringstatesItemDTO', 'EdsmSystemFactionsResponseFactionsItemDTO', 'EdsmSystemFactionsResponseControllingfactionDTO', 'EdsmSystemFactionsResponseDTO')
