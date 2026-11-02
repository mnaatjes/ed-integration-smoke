"""Unit and integration tests for telemetry harness, SQLite storage, and pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from ed_models.core.domain.status.flags import StatusFlags, StatusFlags2

from ed_integration_smoke.daemon import (
    TelemetryPipeline,
    TelemetryStorageEngine,
    build_all_targets,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_telemetry.db"


@pytest.fixture
def storage(test_db_path: Path) -> TelemetryStorageEngine:
    engine = TelemetryStorageEngine(test_db_path)
    engine.seed_targets(build_all_targets())
    return engine


@pytest.fixture
def pipeline(storage: TelemetryStorageEngine) -> TelemetryPipeline:
    return TelemetryPipeline(storage=storage)


def test_target_seeding(storage: TelemetryStorageEngine) -> None:
    summary = storage.get_coverage_summary()
    assert summary["total_targets"] >= 300  # 258 events + 47 status flags
    assert summary["achieved_targets"] == 0
    assert summary["percentage"] == 0.0
    assert "travel" in summary["by_chapter"]
    assert "combat" in summary["by_chapter"]


def test_process_valid_journal_event(
    pipeline: TelemetryPipeline, storage: TelemetryStorageEngine
) -> None:
    payload: dict[str, Any] = {
        "timestamp": "2026-11-02T00:00:00Z",
        "event": "FSDJump",
        "StarSystem": "Sol",
        "SystemAddress": 10477373803,
        "StarPos": [0.0, 0.0, 0.0],
        "SystemAllegiance": "Federation",
        "SystemEconomy": "$economy_Refinery;",
        "SystemGovernment": "$government_Democracy;",
        "SystemSecurity": "$SYSTEM_SECURITY_high;",
        "Population": 22780871769,
        "JumpDist": 12.5,
        "FuelUsed": 2.1,
        "FuelLevel": 29.9,
    }

    result = pipeline.process_envelope(payload)
    assert result.success is True
    assert result.target_id == "FSDJump"
    assert result.is_mismatch is False
    assert result.hydrated_object is not None

    summary = storage.get_coverage_summary()
    assert summary["achieved_targets"] == 1
    assert summary["total_hits"] == 1
    assert summary["by_chapter"]["travel"]["achieved"] == 1

    unachieved = storage.list_unachieved_targets(chapter="travel")
    unachieved_ids = [t.target_id for t in unachieved]
    assert "FSDJump" not in unachieved_ids
    assert "Docked" in unachieved_ids


def test_process_telemetry_status(
    pipeline: TelemetryPipeline, storage: TelemetryStorageEngine
) -> None:
    # Bitmask with DOCKED (1) + SHIELDS_UP (8) + LIGHTS_ON (256)
    docked_val = StatusFlags.DOCKED.value
    shields_val = StatusFlags.SHIELDS_UP.value
    lights_val = StatusFlags.LIGHTS_ON.value
    combined_flags = docked_val | shields_val | lights_val

    # Bitmask 2 with ON_FOOT_IN_STATION
    on_foot_val = StatusFlags2.ON_FOOT_IN_STATION.value

    payload: dict[str, Any] = {
        "timestamp": "2026-11-02T00:00:01Z",
        "Flags": combined_flags,
        "Flags2": on_foot_val,
        "Pips": [4, 4, 4],
        "FireGroup": 0,
        "GuiFocus": 0,
        "Fuel": {"FuelMain": 32.0, "FuelReservoir": 0.5},
        "Cargo": 0,
    }

    result = pipeline.process_envelope(payload)
    assert result.success is True
    assert result.target_id == "StatusTelemetry"

    summary = storage.get_coverage_summary()
    assert summary["by_chapter"]["status"]["achieved"] >= 3
    assert summary["by_chapter"]["status2"]["achieved"] >= 1


def test_domain_mismatch_recording(
    pipeline: TelemetryPipeline, storage: TelemetryStorageEngine
) -> None:
    # Bogus event not present in Frontier journal specifications
    payload: dict[str, Any] = {
        "timestamp": "2026-11-02T00:00:02Z",
        "event": "NonExistentFrontierEvent",
        "BogusField": 12345,
    }

    result = pipeline.process_envelope(payload)
    assert result.success is False
    assert result.is_mismatch is True
    assert result.target_id == "NonExistentFrontierEvent"

    mismatches = storage.list_mismatches()
    assert len(mismatches) == 1
    assert mismatches[0].target_id == "NonExistentFrontierEvent"
    assert "NonExistentFrontierEvent" in mismatches[0].raw_payload
