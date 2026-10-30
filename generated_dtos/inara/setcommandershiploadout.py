"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringModifiersItemDTO:
    """Data transfer object for InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringModifiersItemDTO."""

    name: str
    value: float
    originalValue: float | None = None
    lessIsGood: bool | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringDTO:
    """Data transfer object for InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringDTO."""

    blueprintName: str
    blueprintLevel: int
    blueprintQuality: float | None = None
    experimentalEffect: str | None = None
    modifiers: list[InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringModifiersItemDTO] | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemDTO:
    """Data transfer object for InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemDTO."""

    slotName: str
    itemName: str
    itemValue: int | None = None
    itemHealth: float | None = None
    isOn: bool | None = None
    itemPriority: int | None = None
    itemAmmoClip: int | None = None
    itemAmmoHopper: int | None = None
    engineering: InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringDTO | None = None


@dataclass(frozen=True)
class InaraInaraSetCommanderShipLoadoutEventdataDTO:
    """Data transfer object for InaraInaraSetCommanderShipLoadoutEventdataDTO."""

    shipType: str
    shipGameID: int
    shipLoadout: list[InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemDTO]


@dataclass(frozen=True)
class InaraInaraSetCommanderShipLoadoutDTO:
    """Sets the complete outfitting loadout and engineering mods for a ship."""

    eventName: str
    eventTimestamp: str
    eventData: InaraInaraSetCommanderShipLoadoutEventdataDTO
    eventCustomID: int | None = None

__all__ = ('InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringModifiersItemDTO', 'InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemEngineeringDTO', 'InaraInaraSetCommanderShipLoadoutEventdataShiploadoutItemDTO', 'InaraInaraSetCommanderShipLoadoutEventdataDTO', 'InaraInaraSetCommanderShipLoadoutDTO')
