"""Auto-generated Python dataclasses synthesized by ed-schema."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class SpanshSpanshBodySignalsDTO:
    """Planets only.  The signals that can be found on the planet."""

    signals: Any | None = None
    updateTime: str | None = None
    genuses: list[str] | None = None


@dataclass(frozen=True)
class SpanshSpanshBodyDTO:
    """Spansh Body contract."""

    id64: int
    bodyId: int
    name: str
    updateTime: str
    orbitalPeriod: float | None = None
    semiMajorAxis: float | None = None
    orbitalEccentricity: float | None = None
    orbitalInclination: float | None = None
    argOfPeriapsis: float | None = None
    meanAnomaly: float | None = None
    ascendingNode: float | None = None
    timestamps: Any | None = None
    stations: list[Any] | None = None
    type: Any | None = None
    subType: Any | None = None
    distanceToArrival: float | None = None
    mainStar: bool | None = None
    age: int | None = None
    spectralClass: Any | None = None
    luminosity: Any | None = None
    absoluteMagnitude: float | None = None
    solarMasses: float | None = None
    solarRadius: float | None = None
    surfaceTemperature: float | None = None
    rotationalPeriod: float | None = None
    rotationalPeriodTidallyLocked: bool | None = None
    axialTilt: float | None = None
    parents: list[Any] | None = None
    isLandable: bool | None = None
    gravity: float | None = None
    earthMasses: float | None = None
    radius: float | None = None
    surfacePressure: float | None = None
    volcanismType: Any | None = None
    atmosphereType: Any | None = None
    atmosphereComposition: Any | None = None
    solidComposition: Any | None = None
    terraformingState: Any | None = None
    materials: Any | None = None
    signals: SpanshSpanshBodySignalsDTO | None = None
    reserveLevel: Any | None = None
    rings: list[Any] | None = None
    belts: list[Any] | None = None

__all__ = ('SpanshSpanshBodySignalsDTO', 'SpanshSpanshBodyDTO')
