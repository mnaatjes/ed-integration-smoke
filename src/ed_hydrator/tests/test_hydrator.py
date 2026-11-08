"""Unit tests for ed_hydrator domain entity transformations."""

import json

from ed_models import JournalEvent, StatusTelemetry

from ed_hydrator import (
    HydratedEventRecord,
    HydratedTelemetryState,
    TelemetryDomainHydrator,
)
from ed_telemetry_client import (
    EndpointMetadata,
    TelemetryPlane,
    TelemetryResponseDTO,
    TelemetrySource,
)


def test_hydrate_status_entity() -> None:
    hydrator = TelemetryDomainHydrator()
    payload = {
        "Flags": 16842769,  # Docked (1) + Landed (2) etc.
        "Flags2": 0,
        "Pips": [4, 4, 4],
        "Fuel": {"FuelMain": 32.0, "FuelReservoir": 0.5},
        "Cargo": 4,
        "LegalState": "Clean",
    }
    status = hydrator.hydrate_status(payload)
    assert status is not None
    assert isinstance(status, StatusTelemetry)
    assert status.is_docked is True
    assert status.fuel_main == 32.0
    assert status.cargo == 4
    assert status.legal_state == "Clean"


def test_hydrate_event_entity() -> None:
    hydrator = TelemetryDomainHydrator()
    payload = {
        "timestamp": "2026-11-08T12:00:00Z",
        "event": "FSDJump",
        "StarSystem": "Shinrarta Dezhra",
        "SystemAddress": 3932277478106,
        "StarPos": [55.71875, 17.59375, 27.15625],
        "SystemAllegiance": "PilotsFederation",
        "SystemEconomy": "$economy_HighTech;",
        "SystemGovernment": "$government_Democracy;",
        "SystemSecurity": "$SYSTEM_SECURITY_high;",
        "Population": 85199,
        "JumpDist": 14.8,
        "FuelUsed": 2.1,
        "FuelLevel": 29.9,
    }
    event = hydrator.hydrate_event(payload)
    assert event is not None
    assert isinstance(event, JournalEvent)
    is_valid_event = (
        getattr(event, "star_system", None) == "Shinrarta Dezhra"
        or getattr(event, "event", None) == "FSDJump"
    )
    assert is_valid_event is True


def test_hydrate_full_state_response() -> None:
    hydrator = TelemetryDomainHydrator()
    state_payload = {
        "state_sequence": 88,
        "timestamp": "2026-11-08T14:30:00+00:00",
        "active_journal": "Journal.2026-11-08T140000.01.log",
        "latest_journal_event": {
            "id": 88,
            "event_id": "c1f7b098",
            "topic": "telemetry.journal",
            "payload_json": json.dumps({
                "timestamp": "2026-11-08T14:30:00Z",
                "event": "Docked",
                "StationName": "Jameson Memorial",
                "StationType": "Orbis",
                "StarSystem": "Shinrarta Dezhra",
            }),
        },
        "game_status": {
            "exists": True,
            "raw_payload": json.dumps({
                "Flags": 1,
                "Pips": [2, 8, 2],
                "Fuel": {"FuelMain": 16.0},
                "Cargo": 0,
            }),
        },
        "snapshots": {
            "Market": {
                "target_name": "Market.json",
                "exists": True,
                "raw_payload": json.dumps({"event": "Market", "MarketID": 128114}),
            }
        },
    }

    meta = EndpointMetadata(
        endpoint_url="http://192.168.1.214:8080/api/v1/state",
        status_code=200,
        plane=TelemetryPlane.STATE,
        source=TelemetrySource.MEMORY_BUFFER,
    )
    resp_dto = TelemetryResponseDTO(
        metadata=meta,
        raw_payload=json.dumps(state_payload).encode("utf-8"),
        data=state_payload,
    )

    state = hydrator.hydrate_state(resp_dto)
    assert isinstance(state, HydratedTelemetryState)
    assert state.state_sequence == 88
    assert state.active_journal == "Journal.2026-11-08T140000.01.log"
    assert state.has_active_session is True

    # Validate nested domain entities
    assert state.status is not None
    assert state.status.is_docked is True
    assert state.latest_event is not None
    is_docked_event = (
        getattr(state.latest_event, "station_name", None) == "Jameson Memorial"
        or getattr(state.latest_event, "event", None) == "Docked"
    )
    assert is_docked_event is True

    # Validate raw snapshots map
    assert "Market" in state.raw_snapshots
    assert state.raw_snapshots["Market"].data.get("MarketID") == 128114


def test_hydrate_response_dispatcher_journal() -> None:
    hydrator = TelemetryDomainHydrator()
    journal_payload = {
        "id": 10,
        "event_id": "test-uuid",
        "topic": "telemetry.journal",
        "timestamp": "2026-11-08T15:00:00Z",
        "payload_json": json.dumps({
            "timestamp": "2026-11-08T15:00:00Z",
            "event": "Music",
            "MusicTrack": "NoTrack",
        }),
    }
    meta = EndpointMetadata(
        endpoint_url="http://192.168.1.214:8080/api/v1/journal/latest",
        status_code=200,
        plane=TelemetryPlane.JOURNAL,
        source=TelemetrySource.MEMORY_BUFFER,
    )
    dto = TelemetryResponseDTO(
        metadata=meta,
        raw_payload=b"{}",
        data=journal_payload,
    )

    result = hydrator.hydrate_response(dto)
    assert isinstance(result, HydratedEventRecord)
    assert result.event_id == "test-uuid"
    assert result.topic == "telemetry.journal"
    assert isinstance(result.event, JournalEvent)
