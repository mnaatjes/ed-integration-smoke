"""Scenario tests exercising ed-transport and ed-schema against the synthetic EDDN gateway."""

from __future__ import annotations

import json
from pathlib import Path

from ed_transport import HttpRequestDTO, HttpResponseDTO, create_transport_client
from tests.fixtures.mock_eddn_gateway import MockEddnGateway, MockResponse


def test_mock_eddn_strict_validation_success(mock_eddn_gateway: MockEddnGateway) -> None:
    """Verifies that a conformant payload passes strict local validation and returns HTTP 200 OK."""
    transport = create_transport_client()

    valid_payload = {
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/test",
        "header": {
            "uploaderID": "commander_connor",
            "softwareName": "ed-integration-smoke",
            "softwareVersion": "1.1.0",
        },
        "message": {
            "timestamp": "2026-10-30T04:20:00Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "StarPos": [0.0, 0.0, 0.0],
            "SystemAddress": 10477373803,
        },
    }

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        headers={"Content-Type": "application/json"},
        body=json.dumps(valid_payload),
    )

    assert response.status_code == 200
    assert response.body.decode("utf-8").strip() == "OK"
    assert len(mock_eddn_gateway.received_requests) == 1
    assert mock_eddn_gateway.received_requests[0].json_payload == valid_payload


def test_mock_eddn_strict_validation_schema_mismatch_failure(
    mock_eddn_gateway: MockEddnGateway,
) -> None:
    """Verifies that an invalid payload missing required fields is rejected with HTTP 400."""
    transport = create_transport_client()

    # Missing required message fields: StarSystem, StarPos, SystemAddress
    invalid_payload = {
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/test",
        "header": {
            "uploaderID": "commander_connor",
            "softwareName": "ed-integration-smoke",
            "softwareVersion": "1.1.0",
        },
        "message": {
            "timestamp": "2026-10-30T04:20:00Z",
            "event": "FSDJump",
        },
    }

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        headers={"Content-Type": "application/json"},
        body=json.dumps(invalid_payload),
    )

    assert response.status_code == 400
    assert "FAIL: Schema validation error" in response.body.decode("utf-8")
    assert len(mock_eddn_gateway.received_requests) == 1


def test_mock_eddn_route_not_found(mock_eddn_gateway: MockEddnGateway) -> None:
    """Verifies that requesting an unregistered path returns HTTP 404."""
    transport = create_transport_client()
    bad_url = f"http://{mock_eddn_gateway.host}:{mock_eddn_gateway.port}/unknown-route"

    response: HttpResponseDTO = transport.post(url=bad_url, body=b"{}")
    assert response.status_code == 404
    assert response.body.decode("utf-8").strip() == "Not Found"


def test_mock_eddn_simulate_rate_limit(mock_eddn_gateway: MockEddnGateway) -> None:
    """Verifies that simulating rate-limiting returns HTTP 429 with retry-after header."""
    mock_eddn_gateway.simulate_rate_limit(retry_after_seconds=12)
    transport = create_transport_client()

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        body=b"{}",
    )

    assert response.status_code == 429
    # ed-transport lower-cases response header names
    assert response.headers.get("retry-after") == "12"
    assert "Too Many Requests" in response.body.decode("utf-8")


def test_mock_eddn_simulate_status_503(mock_eddn_gateway: MockEddnGateway) -> None:
    """Verifies that simulating gateway server failure returns HTTP 503 after retries."""
    mock_eddn_gateway.simulate_status(503, body="EDDN Gateway Maintenance")
    transport = create_transport_client()

    response: HttpResponseDTO = transport.post(
        url=mock_eddn_gateway.upload_url,
        body=b"{}",
    )

    assert response.status_code == 503
    assert response.body.decode("utf-8").strip() == "EDDN Gateway Maintenance"
    # ed-transport default retry policy retries 503 3 times (initial + 3 retries = 4 attempts)
    assert len(mock_eddn_gateway.received_requests) == 4


def test_mock_eddn_simulate_sequence_recovery(mock_eddn_gateway: MockEddnGateway) -> None:
    """Verifies that ed-transport automatically retries 503 and recovers when server yields 200."""
    mock_eddn_gateway.simulate_sequence(
        [
            MockResponse(status_code=503, body="Temporary Outage"),
            MockResponse(status_code=200, body="OK"),
        ]
    )
    transport = create_transport_client()

    # ed-transport's retry policy automatically catches the 503, backs off, retries, and returns 200
    response = transport.post(url=mock_eddn_gateway.upload_url, body=b"{}")
    assert response.status_code == 200
    assert response.body.decode("utf-8").strip() == "OK"
    assert len(mock_eddn_gateway.received_requests) == 2
