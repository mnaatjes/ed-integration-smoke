"""Interrogation test suite exercising all RFC 0001 failure modes and structured logging."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from ed_integration_smoke import StructuredJsonLogger
from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaEngine,
    SchemaKey,
    create_schema_engine,
)
from ed_transport import (
    HttpRequestDTO,
    HttpResponseDTO,
    TransportClient,
    create_transport_client,
)
from generated_dtos.eddn.journal_v1_0 import (
    EddnJournalV10DTO,
    EddnJournalV10HeaderDTO,
    EddnJournalV10MessageDTO,
)
from tests.fixtures.mock_eddn_gateway import MockEddnGateway, MockResponse


@pytest.fixture
def test_logger() -> StructuredJsonLogger:
    """Provides a fresh instance of the RFC 0001 StructuredJsonLogger."""
    logger = StructuredJsonLogger(name="ed_integration_smoke.rfc0001_tests")
    logger.clear()
    return logger


@pytest.fixture
def loaded_schema_engine() -> tuple[SchemaEngine, SchemaKey]:
    """Provides a SchemaEngine pre-loaded with the EDDN Journal contract."""
    engine = create_schema_engine()
    schemas_dir = Path(__file__).resolve().parent.parent / "schemas" / "eddn"

    class EddnTestManifest:
        name = "eddn"
        schema_dir = schemas_dir
        endpoints = (
            EndpointContract(
                route="/schemas/journal/1",
                schema_file="journal-v1.0.json",
                model_cls=EddnJournalV10DTO,
                header_contract=HeaderContract(
                    parameters=(
                        HeaderParameterContract(
                            name="Content-Type",
                            required=True,
                            regex_pattern=r"^application/json.*$",
                        ),
                    )
                ),
            ),
        )

    engine.load_manifests([EddnTestManifest])
    key = SchemaKey(namespace="eddn", endpoint="/schemas/journal/1")
    return engine, key


# ==============================================================================
# Layer 1: Network & Socket Transport Layer
# ==============================================================================


def test_layer1_unreachable_network_failure(test_logger: StructuredJsonLogger) -> None:
    """Interrogates Layer 1 failure when host/port is completely unreachable."""
    transport = create_transport_client()
    # Ephemeral unallocated port on localhost
    unreachable_url = "http://127.0.0.1:1"

    with pytest.raises(Exception) as exc_info:
        transport.post(url=unreachable_url, body=b"{}", timeout=1.0)

    # Log structured failure conforming to RFC 0001
    log_record = test_logger.error(
        "network_connection_failed",
        target={"namespace": "eddn", "url": unreachable_url},
        error={
            "category": "NETWORK_UNREACHABLE",
            "exception": type(exc_info.value).__name__,
            "action": "QUEUE_FOR_OFFLINE_SPOOL",
        },
    )

    assert log_record["level"] == "ERROR"
    assert log_record["error"]["category"] == "NETWORK_UNREACHABLE"
    assert log_record["error"]["action"] == "QUEUE_FOR_OFFLINE_SPOOL"


# ==============================================================================
# Layer 2: HTTP Protocol & Routing Layer
# ==============================================================================


def test_layer2_http_404_route_not_found(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 2 failure when client targets an invalid route."""
    transport = create_transport_client()
    bad_url = f"http://{mock_eddn_gateway.host}:{mock_eddn_gateway.port}/wrong/path"

    response: HttpResponseDTO = transport.post(url=bad_url, body=b"{}")
    assert response.status_code == 404

    log_record = test_logger.error(
        "http_route_not_found",
        target={"namespace": "eddn", "url": bad_url},
        error={
            "category": "ROUTING_ERROR",
            "status_code": 404,
            "action": "ABORT_FATAL_CONFIG_BUG",
        },
    )

    assert log_record["error"]["status_code"] == 404
    assert log_record["error"]["action"] == "ABORT_FATAL_CONFIG_BUG"


def test_layer2_http_405_method_not_allowed(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 2 failure when client sends GET instead of POST."""
    transport = create_transport_client()
    response: HttpResponseDTO = transport.get(url=mock_eddn_gateway.upload_url)
    assert response.status_code == 405

    log_record = test_logger.error(
        "http_method_not_allowed",
        target={"namespace": "eddn", "url": mock_eddn_gateway.upload_url},
        error={
            "category": "PROTOCOL_MISMATCH",
            "status_code": 405,
            "action": "ABORT_METHOD_NOT_ALLOWED",
        },
    )

    assert log_record["error"]["status_code"] == 405


# ==============================================================================
# Layer 3: Traffic Governance & Rate-Limiting Layer
# ==============================================================================


def test_layer3_rate_limiting_with_retry_after(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 3 failure when receiving 429 with Retry-After header."""
    mock_eddn_gateway.simulate_rate_limit(retry_after_seconds=8)
    transport = create_transport_client()

    response: HttpResponseDTO = transport.post(url=mock_eddn_gateway.upload_url, body=b"{}")
    assert response.status_code == 429
    retry_after = response.headers.get("retry-after")
    assert retry_after == "8"

    log_record = test_logger.warning(
        "rate_limit_exceeded",
        target={"namespace": "eddn", "url": mock_eddn_gateway.upload_url},
        error={
            "category": "RATE_LIMIT_BURST",
            "status_code": 429,
            "retry_after_seconds": int(retry_after),
            "action": "HOLD_IN_QUEUE_UNTIL_EXPIRY",
        },
    )

    assert log_record["level"] == "WARNING"
    assert log_record["error"]["retry_after_seconds"] == 8


# ==============================================================================
# Layer 4: Schema Contract & Data Governance Layer
# ==============================================================================


def test_layer4_schema_missing_schema_ref(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 4 schema rejection when $schemaRef is completely missing."""
    transport = create_transport_client()
    poison_payload = {"header": {}, "message": {}}

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        body=json.dumps(poison_payload),
    )

    assert response.status_code == 400
    assert "Missing '$schemaRef'" in response.body.decode("utf-8")

    log_record = test_logger.error(
        "schema_rejection_missing_ref",
        target={"namespace": "eddn", "url": mock_eddn_gateway.upload_url},
        error={
            "category": "SCHEMA_VIOLATION",
            "status_code": 400,
            "response_body": response.body.decode("utf-8").strip(),
            "action": "DISCARD_POISON_PILL",
        },
    )

    assert log_record["error"]["action"] == "DISCARD_POISON_PILL"


def test_layer4_schema_missing_required_properties(
    mock_eddn_gateway: MockEddnGateway,
    loaded_schema_engine: tuple[SchemaEngine, SchemaKey],
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 4 schema rejection when message is missing required fields."""
    engine, key = loaded_schema_engine
    transport = create_transport_client()

    # Incomplete message: missing StarSystem, StarPos, SystemAddress
    incomplete_payload = {
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/test",
        "header": {
            "uploaderID": "pilot_001",
            "softwareName": "ed-integration-smoke",
            "softwareVersion": "1.1.0",
        },
        "message": {
            "timestamp": "2026-10-30T04:20:00Z",
            "event": "FSDJump",
        },
    }

    # Verify local ed-schema pre-flight catches this before sending
    local_val = engine.validate_call(
        key=key,
        headers={"Content-Type": "application/json"},
        payload=incomplete_payload,
    )
    assert not local_val.is_valid
    assert len(local_val.payload_errors) > 0

    # Dispatch to mock gateway and confirm gateway enforces the exact same rejection
    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        body=json.dumps(incomplete_payload),
    )
    assert response.status_code == 400
    assert "Schema validation error" in response.body.decode("utf-8")

    test_logger.error(
        "schema_required_field_missing",
        schema={"schemaRef": incomplete_payload["$schemaRef"]},
        error={
            "category": "SCHEMA_VIOLATION",
            "status_code": 400,
            "local_errors": [e.message for e in local_val.payload_errors],
            "action": "DISCARD_POISON_PILL",
        },
    )


def test_layer4_schema_disallowed_property_leakage(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 4 schema rejection when a blacklisted property (e.g. ActiveFine) leaks."""
    transport = create_transport_client()

    leaked_payload = {
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/test",
        "header": {
            "uploaderID": "pilot_001",
            "softwareName": "ed-integration-smoke",
            "softwareVersion": "1.1.0",
        },
        "message": {
            "timestamp": "2026-10-30T04:20:00Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "StarPos": [0.0, 0.0, 0.0],
            "SystemAddress": 10477373803,
            # ActiveFine is defined as $ref: "#/definitions/disallowed" in journal-v1.0.json
            "ActiveFine": 500,
        },
    }

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        body=json.dumps(leaked_payload),
    )
    assert response.status_code == 400
    assert "Schema validation error" in response.body.decode("utf-8")

    test_logger.error(
        "disallowed_field_leakage_detected",
        schema={"schemaRef": leaked_payload["$schemaRef"]},
        error={
            "category": "PRIVACY_GOVERNANCE_VIOLATION",
            "leaked_field": "ActiveFine",
            "status_code": 400,
            "action": "UPDATE_SCRUBBING_FILTER",
        },
    )


# ==============================================================================
# Layer 5: Server Outage & Maintenance Layer
# ==============================================================================


def test_layer5_server_maintenance_503_outage(
    mock_eddn_gateway: MockEddnGateway,
    test_logger: StructuredJsonLogger,
) -> None:
    """Interrogates Layer 5 failure when gateway undergoes scheduled maintenance."""
    mock_eddn_gateway.simulate_status(503, body="Gateway Under Scheduled Maintenance")
    transport = create_transport_client()

    response: HttpResponseDTO = transport.post(url=mock_eddn_gateway.upload_url, body=b"{}")
    assert response.status_code == 503

    log_record = test_logger.warning(
        "server_maintenance_outage",
        target={"namespace": "eddn", "url": mock_eddn_gateway.upload_url},
        error={
            "category": "SERVER_MAINTENANCE",
            "status_code": 503,
            "action": "IMMEDIATE_SPOOL_BUFFER",
        },
    )

    assert log_record["level"] == "WARNING"
    assert log_record["error"]["action"] == "IMMEDIATE_SPOOL_BUFFER"
