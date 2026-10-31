"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CapiCapiProfileResponseCommanderRankDTO:
    """Data transfer object for CapiCapiProfileResponseCommanderRankDTO."""

    combat: int
    trade: int
    explore: int
    cqc: int | None = None
    soldier: int | None = None
    exobiologist: int | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseCommanderDTO:
    """Commander account state, credits, and rank ladders."""

    id: int
    name: str
    credits: int
    alive: bool
    docked: bool
    rank: CapiCapiProfileResponseCommanderRankDTO
    debt: int | None = None
    currentShipId: int | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseShipValueDTO:
    """Data transfer object for CapiCapiProfileResponseShipValueDTO."""

    hull: int
    modules: int
    total: int
    cargo: int | None = None
    unloaned: int | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseShipHealthDTO:
    """Data transfer object for CapiCapiProfileResponseShipHealthDTO."""

    hull: int
    shield: int
    shieldUp: bool
    integrity: int


@dataclass(frozen=True)
class CapiCapiProfileResponseShipDTO:
    """Active ship specifications, health, and equipped modules."""

    id: int
    name: str
    free: bool
    value: CapiCapiProfileResponseShipValueDTO
    health: CapiCapiProfileResponseShipHealthDTO
    shipName: str | None = None
    shipID: str | None = None
    cockpitBreached: bool | None = None
    oxygenRemaining: int | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseLastsystemDTO:
    """Last recorded star system coordinates and system address."""

    name: str
    id: int


@dataclass(frozen=True)
class CapiCapiProfileResponseLaststarportServicesDTO:
    """Data transfer object for CapiCapiProfileResponseLaststarportServicesDTO."""

    dock: bool | None = None
    autodock: bool | None = None
    commodities: bool | None = None
    contacts: bool | None = None
    exploration: bool | None = None
    rearm: bool | None = None
    refuel: bool | None = None
    repair: bool | None = None
    shipyard: bool | None = None
    outfitting: bool | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseLaststarportDTO:
    """Last visited starport, available facilities, and market services."""

    name: str
    id: int
    services: CapiCapiProfileResponseLaststarportServicesDTO | None = None


@dataclass(frozen=True)
class CapiCapiProfileResponseDTO:
    """Full Commander profile, active ship status, loadout, and starport state."""

    commander: CapiCapiProfileResponseCommanderDTO
    ship: CapiCapiProfileResponseShipDTO
    lastSystem: CapiCapiProfileResponseLastsystemDTO
    lastStarport: CapiCapiProfileResponseLaststarportDTO

__all__ = ('CapiCapiProfileResponseCommanderRankDTO', 'CapiCapiProfileResponseCommanderDTO', 'CapiCapiProfileResponseShipValueDTO', 'CapiCapiProfileResponseShipHealthDTO', 'CapiCapiProfileResponseShipDTO', 'CapiCapiProfileResponseLastsystemDTO', 'CapiCapiProfileResponseLaststarportServicesDTO', 'CapiCapiProfileResponseLaststarportDTO', 'CapiCapiProfileResponseDTO')
