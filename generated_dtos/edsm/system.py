"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EdsmSystemResponseCoordsDTO:
    """The coordinates of the system. Only present when  {@link  SystemRequestOptions#showCoordinates  }  option is set to 1."""

    x: float
    y: float
    z: float


@dataclass(frozen=True)
class EdsmSystemResponseInformationDTO:
    """System information. Only present when  {@link  SystemRequestOptions#showInformation  }  option is set to 1."""

    allegiance: str | None = None
    economy: str | None = None
    faction: str | None = None
    factionState: str | None = None
    government: str | None = None
    population: float | None = None
    reserve: str | None = None
    secondEconomy: str | None = None
    security: str | None = None


@dataclass(frozen=True)
class EdsmSystemResponsePrimarystarDTO:
    """Information about the primary star if any. Only present when  {@link  SystemRequestOptions#showPrimaryStar  }  option is set to 1."""

    isScoopable: bool
    name: str
    type: str


@dataclass(frozen=True)
class EdsmSystemResponseDTO:
    """Response of a  {@link  getSystem }  request."""

    name: str
    coords: EdsmSystemResponseCoordsDTO | None = None
    coordsLocked: bool | None = None
    duplicates: list[float] | None = None
    hidden_at: str | None = None
    id: float | None = None
    id64: Any | None = None
    information: EdsmSystemResponseInformationDTO | None = None
    mergedTo: float | None = None
    permitName: str | None = None
    primaryStar: EdsmSystemResponsePrimarystarDTO | None = None
    requirePermit: bool | None = None

__all__ = ('EdsmSystemResponseCoordsDTO', 'EdsmSystemResponseInformationDTO', 'EdsmSystemResponsePrimarystarDTO', 'EdsmSystemResponseDTO')
