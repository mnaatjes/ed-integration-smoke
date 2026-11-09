"""Pure-functional domain hydrator converting telemetry response DTOs into typed ed-models."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ed_models import (
    JournalEvent,
    StatusTelemetry,
    create_domain_facade,
    parse_journal_event,
)

from ed_telemetry_client import TelemetryResponseDTO

from .models import (
    HydratedEventRecord,
    HydratedTelemetryState,
    RawSnapshotRecord,
)


class TelemetryDomainHydrator:
    """Transforms raw or parsed payloads from ed-telemetry endpoints into typed ed-models."""

    def __init__(self) -> None:
        self._facade = create_domain_facade()

    def hydrate_status(self, payload: Mapping[str, Any] | str) -> StatusTelemetry | None:
        """Hydrates Status.json bitfields and telemetry values into ed_models.StatusTelemetry."""
        data: dict[str, Any]
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                return None
        elif isinstance(payload, Mapping):
            # Check if payload is the server envelope containing 'raw_payload'
            if "raw_payload" in payload and isinstance(payload["raw_payload"], str):
                try:
                    data = json.loads(payload["raw_payload"])
                except (json.JSONDecodeError, TypeError):
                    return None
            else:
                data = dict(payload)
        else:
            return None

        flags = int(data.get("Flags", 0))
        flags2 = int(data.get("Flags2", 0))

        raw_pips = data.get("Pips", [4, 4, 4])
        if isinstance(raw_pips, list) and len(raw_pips) >= 3:
            pips = (int(raw_pips[0]), int(raw_pips[1]), int(raw_pips[2]))
        else:
            pips = (4, 4, 4)

        fuel = data.get("Fuel", {})
        fuel_main = float(fuel.get("FuelMain", 0.0)) if isinstance(fuel, dict) else 0.0
        fuel_reservoir = (
            float(fuel.get("FuelReservoir", 0.0)) if isinstance(fuel, dict) else 0.0
        )
        cargo = int(data.get("Cargo", 0))
        legal_state = str(data.get("LegalState", "Clean"))

        return self._facade.parse_telemetry(
            flags=flags,
            flags2=flags2,
            pips=pips,
            fuel_main=fuel_main,
            fuel_reservoir=fuel_reservoir,
            cargo=cargo,
            legal_state=legal_state,
        )

    def hydrate_event(self, payload: Mapping[str, Any] | str) -> JournalEvent | None:
        """Hydrates a Frontier Journal event payload into a typed ed_models.JournalEvent."""
        data: dict[str, Any]
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except (json.JSONDecodeError, TypeError):
                return None
        elif isinstance(payload, Mapping):
            # Check if wrapped in envelope
            if "payload_json" in payload and isinstance(payload["payload_json"], str):
                try:
                    data = json.loads(payload["payload_json"])
                except (json.JSONDecodeError, TypeError):
                    return None
            elif "raw_payload" in payload and isinstance(payload["raw_payload"], str):
                try:
                    data = json.loads(payload["raw_payload"])
                except (json.JSONDecodeError, TypeError):
                    return None
            else:
                data = dict(payload)
        else:
            return None

        if "event" not in data:
            return None

        try:
            return parse_journal_event(data)
        except Exception:
            return None

    def hydrate_state(
        self,
        response_dto: TelemetryResponseDTO[Any],
    ) -> HydratedTelemetryState:
        """Consolidates complete GET /api/v1/state payload into HydratedTelemetryState."""
        data = response_dto.data
        if not isinstance(data, Mapping):
            return HydratedTelemetryState(
                state_sequence=0,
                timestamp="",
                active_journal=None,
                status=None,
                latest_event=None,
                metadata=response_dto.metadata,
            )

        seq = int(data.get("state_sequence", 0))
        ts = str(data.get("timestamp", ""))
        active_journal = data.get("active_journal")

        # 1. Hydrate game_status
        raw_status = data.get("game_status")
        status_entity: StatusTelemetry | None = None
        if raw_status is not None:
            status_entity = self.hydrate_status(raw_status)

        # 2. Hydrate latest journal event
        raw_event = data.get("latest_journal_event")
        latest_event: JournalEvent | None = None
        if raw_event is not None:
            latest_event = self.hydrate_event(raw_event)

        # 3. Parse auxiliary snapshots map
        raw_snaps = data.get("snapshots", {})
        snapshots_map: dict[str, RawSnapshotRecord] = {}
        if isinstance(raw_snaps, Mapping):
            for snap_name, snap_dict in raw_snaps.items():
                if isinstance(snap_dict, Mapping):
                    inner_payload = snap_dict.get("raw_payload", "{}")
                    parsed_inner: dict[str, Any] = {}
                    if isinstance(inner_payload, str):
                        try:
                            parsed_inner = json.loads(inner_payload)
                        except (json.JSONDecodeError, TypeError):
                            parsed_inner = {}
                    elif isinstance(inner_payload, Mapping):
                        parsed_inner = dict(inner_payload)

                    snapshots_map[snap_name] = RawSnapshotRecord(
                        target_name=str(snap_dict.get("target_name", snap_name)),
                        exists=bool(snap_dict.get("exists", True)),
                        is_live_session=bool(snap_dict.get("is_live_session", True)),
                        timestamp=snap_dict.get("timestamp"),
                        raw_hash=snap_dict.get("raw_hash"),
                        data=parsed_inner,
                    )

        return HydratedTelemetryState(
            state_sequence=seq,
            timestamp=ts,
            active_journal=str(active_journal) if active_journal else None,
            status=status_entity,
            latest_event=latest_event,
            raw_snapshots=snapshots_map,
            metadata=response_dto.metadata,
        )

    def hydrate_response(
        self,
        response_dto: TelemetryResponseDTO[Any],
    ) -> (
        HydratedTelemetryState
        | HydratedEventRecord
        | tuple[HydratedEventRecord, ...]
        | StatusTelemetry
        | None
    ):
        """Universal dispatcher inspecting response metadata plane and hydrating appropriately."""
        plane = getattr(response_dto.metadata, "plane", None)
        plane_str = getattr(plane, "value", str(plane))

        if plane_str == "state":
            return self.hydrate_state(response_dto)

        if plane_str == "status":
            return self.hydrate_status(response_dto.data)

        # Handle list of events (from /journal/events or /events/query)
        if isinstance(response_dto.data, (list, tuple)):
            records: list[HydratedEventRecord] = []
            for item in response_dto.data:
                if isinstance(item, Mapping):
                    ev = self.hydrate_event(item)
                    if ev is not None:
                        records.append(
                            HydratedEventRecord(
                                event_id=item.get("event_id") or item.get("id"),
                                topic=str(item.get("topic", "telemetry.journal")),
                                timestamp=item.get("timestamp", ""),
                                event=ev,
                                raw_hash=item.get("raw_hash"),
                                metadata=response_dto.metadata,
                            )
                        )
            return tuple(records)

        if plane_str in ("journal", "events"):
            event = self.hydrate_event(response_dto.data)
            if event is None:
                return None
            data = response_dto.data if isinstance(response_dto.data, Mapping) else {}
            return HydratedEventRecord(
                event_id=data.get("event_id") or data.get("id"),
                topic=str(data.get("topic", "telemetry.journal")),
                timestamp=data.get("timestamp", ""),
                event=event,
                raw_hash=data.get("raw_hash"),
                metadata=response_dto.metadata,
            )

        # Fallback to opportunistic hydration
        if isinstance(response_dto.data, Mapping):
            if "Flags" in response_dto.data or "game_status" in response_dto.data:
                return self.hydrate_status(response_dto.data)
            if "event" in response_dto.data:
                ev = self.hydrate_event(response_dto.data)
                if ev is not None:
                    return HydratedEventRecord(
                        event_id=None,
                        topic="telemetry.journal",
                        timestamp="",
                        event=ev,
                        metadata=response_dto.metadata,
                    )

        return None

