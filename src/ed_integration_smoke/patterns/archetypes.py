"""Behavioral Abstraction Archetypes for Elite Dangerous Telemetry Streams.

Implements ADR 0003: Decoupled mathematical patterns for edge-detection,
metric quantization, epoch milestones, and context set mutations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any


class EdgeType(Enum):
    """Directional transition edge."""

    RISING = auto()  # 0 -> 1
    FALLING = auto()  # 1 -> 0


@dataclass(frozen=True)
class EdgeEvent:
    """Represents a bitfield edge transition."""

    flag_bit: int
    edge_type: EdgeType
    timestamp: datetime
    raw_flags: int


class BitfieldEdgeDetector:
    """Evaluates rising and falling edge transitions across integer bitfields."""

    def __init__(self, initial_flags: int = 0) -> None:
        self._previous_flags = initial_flags

    @property
    def current_flags(self) -> int:
        return self._previous_flags

    def evaluate(self, current_flags: int, timestamp: datetime | None = None) -> list[EdgeEvent]:
        """Detect rising and falling edges between previous and current flags."""
        if timestamp is None:
            timestamp = datetime.now(UTC)

        if current_flags == self._previous_flags:
            return []

        rising = current_flags & ~self._previous_flags
        falling = ~current_flags & self._previous_flags

        events: list[EdgeEvent] = []

        # Check all 32 possible bit positions
        for bit_index in range(32):
            mask = 1 << bit_index
            if rising & mask:
                events.append(
                    EdgeEvent(
                        flag_bit=mask,
                        edge_type=EdgeType.RISING,
                        timestamp=timestamp,
                        raw_flags=current_flags,
                    )
                )
            elif falling & mask:
                events.append(
                    EdgeEvent(
                        flag_bit=mask,
                        edge_type=EdgeType.FALLING,
                        timestamp=timestamp,
                        raw_flags=current_flags,
                    )
                )

        self._previous_flags = current_flags
        return events


class MetricQuantizer:
    """Discretizes continuous scalar metrics into threshold bands with hysteresis."""

    def __init__(self, thresholds: list[float], labels: list[str]) -> None:
        if len(labels) != len(thresholds) + 1:
            raise ValueError("Labels count must be exactly len(thresholds) + 1")
        self._thresholds = sorted(thresholds)
        self._labels = labels
        self._current_band: str | None = None

    @property
    def current_band(self) -> str | None:
        return self._current_band

    def update(self, value: float) -> str | None:
        """Evaluates value against bands. Returns new band label if changed, else None."""
        new_band = self._labels[0]
        for idx, threshold in enumerate(self._thresholds):
            if value >= threshold:
                new_band = self._labels[idx + 1]

        if new_band != self._current_band:
            self._current_band = new_band
            return new_band
        return None


@dataclass
class EnvironmentMilestoneContext:
    """Consolidated semantic context populated idempotently by discrete milestones."""

    current_system: str | None = None
    current_body: str | None = None
    current_station: str | None = None
    flight_mode: str = "NORMAL_SPACE"
    is_docked: bool = False
    is_landed: bool = False
    last_update: datetime = field(default_factory=lambda: datetime.now(UTC))

    def apply_milestone(
        self, event_name: str, payload: dict[str, Any], timestamp: datetime | None = None
    ) -> None:
        """Updates ambient context directly without sequential preconditions."""
        if timestamp is None:
            timestamp = datetime.now(UTC)
        self.last_update = timestamp

        match event_name:
            case "Docked":
                self.is_docked = True
                self.is_landed = False
                self.flight_mode = "DOCKED"
                self.current_station = payload.get("StationName")
                self.current_system = payload.get("StarSystem", self.current_system)
            case "Undocked":
                self.is_docked = False
                self.current_station = None
                self.flight_mode = "NORMAL_SPACE"
            case "Touchdown":
                self.is_landed = True
                self.flight_mode = "LANDED"
            case "Liftoff":
                self.is_landed = False
                self.flight_mode = "NORMAL_SPACE"
            case "SupercruiseEntry":
                self.flight_mode = "SUPERCRUISE"
            case "SupercruiseExit":
                self.flight_mode = "NORMAL_SPACE"
                self.current_body = payload.get("Body", self.current_body)
            case "FSDJump" | "CarrierJump":
                self.current_system = payload.get("StarSystem", self.current_system)
                self.current_body = payload.get("Body", None)
                self.flight_mode = "SUPERCRUISE"


@dataclass(frozen=True)
class SetDelta:
    """Represents differences detected in context sets."""

    added: frozenset[str]
    removed: frozenset[str]


class ContextSetDiffer:
    """Tracks discrete inventory/equipment additions and removals."""

    def __init__(self, initial_items: set[str] | None = None) -> None:
        self._current_items: set[str] = set(initial_items) if initial_items else set()

    @property
    def current_items(self) -> frozenset[str]:
        return frozenset(self._current_items)

    def update(self, new_items: set[str]) -> SetDelta | None:
        """Compares new collection with existing state. Returns delta if changed."""
        if new_items == self._current_items:
            return None

        added = new_items - self._current_items
        removed = self._current_items - new_items

        self._current_items = set(new_items)
        return SetDelta(added=frozenset(added), removed=frozenset(removed))
