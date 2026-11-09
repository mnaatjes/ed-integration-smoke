"""Unit tests for EliteDangerousClient facade."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ed_models import StatusTelemetry
from ed_models.core.domain.events import FSDJump, LoadGame

from ed_fleet_client import EliteDangerousClient
from ed_telemetry_client import (
    EndpointMetadata,
    TelemetryPlane,
    TelemetryResponseDTO,
    TelemetrySource,
)


def test_client_initialization() -> None:
    client = EliteDangerousClient("http://192.168.1.214:8080")
    assert client.endpoint == "http://192.168.1.214:8080"
    assert client.state.location.star_system == "Unknown"
    assert client.state.session.commander_name == "Unknown"


def test_client_reactive_listener_and_state_reduction() -> None:
    client = EliteDangerousClient("http://localhost:8080")
    received_jumps: list[FSDJump] = []

    @client.on(FSDJump)
    def handle_jump(jump: FSDJump) -> None:
        # Guarantee: when listener runs, state must already be updated
        assert client.state.location.star_system == "Sol"
        received_jumps.append(jump)

    jump = FSDJump(
        timestamp="2026-11-09T04:40:00Z",
        event="FSDJump",
        StarSystem="Sol",
        Body="Sol",
        Population=22800000000,
    )

    result = client._ingest_event(jump)
    assert result.event_name == "FSDJump"
    assert result.executed_count == 1
    assert len(received_jumps) == 1
    assert client.state.location.star_system == "Sol"
    assert client.state.location.population == 22800000000


def test_client_status_telemetry_ingest() -> None:
    client = EliteDangerousClient("http://localhost:8080")
    status = StatusTelemetry(fuel_main=32.0, cargo=16)

    client._ingest_event(status)
    assert client.state.ship.telemetry is not None
    assert client.state.ship.telemetry.fuel_main == 32.0
    assert client.state.ship.telemetry.cargo == 16


@patch("ed_telemetry_client.TelemetryHttpClient.get_status")
def test_client_get_status_query(mock_get_status: MagicMock) -> None:
    meta = EndpointMetadata(
        endpoint_url="http://localhost:8080/api/v1/status",
        status_code=200,
        plane=TelemetryPlane.STATUS,
        source=TelemetrySource.SQLITE_WAL,
    )
    mock_get_status.return_value = TelemetryResponseDTO(
        metadata=meta,
        raw_payload=b"{}",
        data={"Flags": 1, "Pips": [4, 4, 4], "Fuel": {"FuelMain": 16.0}},
    )
    client = EliteDangerousClient("http://localhost:8080")
    status = client.get_status()

    assert status is not None
    assert client.state.ship.telemetry is not None
    assert client.state.ship.telemetry.fuel_main == 16.0


@patch("ed_telemetry_client.TelemetryHttpClient.get_latest_journal")
def test_client_get_latest_journal_query(mock_latest: MagicMock) -> None:
    meta = EndpointMetadata(
        endpoint_url="http://localhost:8080/api/v1/journal/latest",
        status_code=200,
        plane=TelemetryPlane.JOURNAL,
        source=TelemetrySource.SQLITE_WAL,
    )
    mock_latest.return_value = TelemetryResponseDTO(
        metadata=meta,
        raw_payload=b"{}",
        data={"event": "LoadGame", "Commander": "Adulantis", "Credits": 777000000},
    )
    client = EliteDangerousClient("http://localhost:8080")
    ev = client.get_latest_journal()

    assert ev is not None
    assert isinstance(ev, LoadGame)
    assert client.state.session.commander_name == "Adulantis"
    assert client.state.session.credits == 777000000


def test_client_background_lifecycle() -> None:
    client = EliteDangerousClient("http://localhost:8080", auto_poll_status_interval=None)
    with patch.object(client, "get_status"), patch.object(client, "get_latest_journal"):
        client.start_background()
        assert client._running is True
        assert client._worker_thread is not None
        assert client._worker_thread.is_alive()

        client.stop()
        assert client._running is False
        assert client._worker_thread is None
