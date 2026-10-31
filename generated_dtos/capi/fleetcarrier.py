"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CapiCapiFleetCarrierResponseCapacityDTO:
    """Tonnage capacity distribution."""

    freeSpace: int
    usedSpace: int
    totalSpace: int


@dataclass(frozen=True)
class CapiCapiFleetCarrierResponseNameDTO:
    """Data transfer object for CapiCapiFleetCarrierResponseNameDTO."""

    callsign: str
    vanityName: str | None = None


@dataclass(frozen=True)
class CapiCapiFleetCarrierResponseDTO:
    """Commander-owned Fleet Carrier telemetries, balances, and jump state."""

    carrierId: int
    currentStarSystem: str
    balance: int
    fuel: int
    capacity: CapiCapiFleetCarrierResponseCapacityDTO
    name: CapiCapiFleetCarrierResponseNameDTO

__all__ = ('CapiCapiFleetCarrierResponseCapacityDTO', 'CapiCapiFleetCarrierResponseNameDTO', 'CapiCapiFleetCarrierResponseDTO')
