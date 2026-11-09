"""Unit and integration tests for ed_telemetry_client."""

import json
from unittest.mock import MagicMock

from ed_transport.adapters.driving.client import TransportClient
from ed_transport.core.ports.dto import HttpResponseDTO

from ed_telemetry_client import (
    EndpointMetadata,
    MetadataHydrationMiddleware,
    TelemetryConnectionConfig,
    TelemetryHttpClient,
    TelemetryPlane,
    TelemetryResponseDTO,
    TelemetrySource,
)


def test_connection_config_defaults() -> None:
    config = TelemetryConnectionConfig()
    assert config.host == "192.168.1.214"
    assert config.port == 8080
    assert config.api_key is None
    assert config.default_path == "/api/v1/state"
    assert config.base_url == "http://192.168.1.214:8080"
    assert config.build_url() == "http://192.168.1.214:8080/api/v1/state"
    assert config.build_url("/api/v1/status") == "http://192.168.1.214:8080/api/v1/status"
    assert config.build_url("api/v1/status") == "http://192.168.1.214:8080/api/v1/status"


def test_metadata_plane_and_source_parsing() -> None:
    assert TelemetryPlane.from_header("state") == TelemetryPlane.STATE
    assert TelemetryPlane.from_header("STATUS") == TelemetryPlane.STATUS
    assert TelemetryPlane.from_header("snapshots") == TelemetryPlane.SNAPSHOTS
    assert TelemetryPlane.from_header("journal") == TelemetryPlane.JOURNAL
    assert TelemetryPlane.from_header("system") == TelemetryPlane.SYSTEM
    assert TelemetryPlane.from_header("unknown_plane") == TelemetryPlane.UNKNOWN
    assert TelemetryPlane.from_header(None) == TelemetryPlane.UNKNOWN

    assert TelemetrySource.from_header("memory-buffer") == TelemetrySource.MEMORY_BUFFER
    assert TelemetrySource.from_header("sqlite-wal") == TelemetrySource.SQLITE_WAL
    assert TelemetrySource.from_header(None) == TelemetrySource.UNKNOWN


def test_middleware_hydrates_metadata_and_payload() -> None:
    middleware = MetadataHydrationMiddleware()
    body_dict = {
        "state_sequence": 42,
        "timestamp": "2026-11-08T14:00:00+00:00",
        "active_journal": "Journal.2026-11-08T100000.01.log",
    }
    raw_bytes = json.dumps(body_dict).encode("utf-8")
    headers = {
        "X-Telemetry-Plane": "state",
        "X-Telemetry-Source": "memory-buffer",
        "ETag": 'W/"42"',
        "Content-Type": "application/json",
    }
    http_resp = HttpResponseDTO(
        status_code=200,
        headers=headers,
        body=raw_bytes,
    )

    dto: TelemetryResponseDTO[dict[str, object]] = middleware.hydrate(
        endpoint_url="http://192.168.1.214:8080/api/v1/state",
        response=http_resp,
        latency_ms=12.5,
    )

    assert isinstance(dto, TelemetryResponseDTO)
    assert dto.raw_payload == raw_bytes
    assert dto.data == body_dict
    assert dto.text == json.dumps(body_dict)

    meta = dto.metadata
    assert isinstance(meta, EndpointMetadata)
    assert meta.endpoint_url == "http://192.168.1.214:8080/api/v1/state"
    assert meta.status_code == 200
    assert meta.plane == TelemetryPlane.STATE
    assert meta.source == TelemetrySource.MEMORY_BUFFER
    assert meta.etag == 'W/"42"'
    assert meta.content_type == "application/json"
    assert meta.latency_ms == 12.5
    assert meta.is_cached_candidate is True


def test_telemetry_http_client_dispatches_with_headers_and_key() -> None:
    mock_transport = MagicMock(spec=TransportClient)
    body = b'{"status": "ok"}'
    mock_transport.get.return_value = HttpResponseDTO(
        status_code=200,
        headers={
            "X-Telemetry-Plane": "system",
            "X-Telemetry-Source": "memory-buffer",
            "Content-Type": "application/json",
        },
        body=body,
    )

    config = TelemetryConnectionConfig(
        host="10.0.0.5",
        port=9000,
        api_key="secret-token-123",
    )
    client = TelemetryHttpClient(config=config, transport_client=mock_transport)

    dto = client.get_system_health()

    mock_transport.get.assert_called_once()
    called_kwargs = mock_transport.get.call_args.kwargs
    assert called_kwargs["url"] == "http://10.0.0.5:9000/api/v1/system/health"
    assert called_kwargs["headers"]["X-API-Key"] == "secret-token-123"
    assert called_kwargs["headers"]["Authorization"] == "Bearer secret-token-123"
    assert dto.metadata.plane == TelemetryPlane.SYSTEM
    assert dto.data == {"status": "ok"}
    assert dto.raw_payload == body


def test_telemetry_http_client_convenience_endpoints() -> None:
    mock_transport = MagicMock(spec=TransportClient)
    mock_transport.get.return_value = HttpResponseDTO(
        status_code=200,
        headers={
            "X-Telemetry-Plane": "state",
            "X-Telemetry-Source": "memory-buffer",
            "ETag": 'W/"100"',
        },
        body=b'{"state_sequence": 100}',
    )

    client = TelemetryHttpClient(transport_client=mock_transport)

    # 1. State
    res_state = client.get_state(if_none_match='W/"99"')
    assert mock_transport.get.call_args.kwargs["url"] == "http://192.168.1.214:8080/api/v1/state"
    assert mock_transport.get.call_args.kwargs["headers"]["If-None-Match"] == 'W/"99"'
    assert res_state.data == {"state_sequence": 100}

    # 2. Heartbeat
    client.get_state_heartbeat()
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/state/heartbeat"
    )

    # 3. Status
    client.get_status()
    assert mock_transport.get.call_args.kwargs["url"] == "http://192.168.1.214:8080/api/v1/status"

    # 4. Snapshots map
    client.get_snapshots()
    assert mock_transport.get.call_args.kwargs["url"] == "http://192.168.1.214:8080/api/v1/snapshots"

    # 5. Specific snapshot
    client.get_snapshot("Market")
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/snapshots/Market"
    )

    # 6. Journal latest
    client.get_latest_journal()
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/journal/latest"
    )

    # 7. Journal events query
    client.get_journal_events(topic="FSDJump", limit=50)
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/journal/events"
    )
    assert mock_transport.get.call_args.kwargs["params"] == {
        "limit": "50",
        "order": "asc",
        "topic": "FSDJump",
    }

    # 8. Unified events query
    client.query_events(topic="telemetry.file_delta", limit=20)
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/events/query"
    )
    assert mock_transport.get.call_args.kwargs["params"] == {
        "limit": "20",
        "order": "asc",
        "topic": "telemetry.file_delta",
    }

    # 9. Drain events queue
    client.drain_events_queue(limit=10)
    assert (
        mock_transport.get.call_args.kwargs["url"]
        == "http://192.168.1.214:8080/api/v1/events/queue"
    )
    assert mock_transport.get.call_args.kwargs["params"] == {"limit": "10"}


def test_middleware_handles_non_json_cleanly() -> None:
    middleware = MetadataHydrationMiddleware()
    raw_text = b"Not JSON Plain text error"
    http_resp = HttpResponseDTO(
        status_code=500,
        headers={"Content-Type": "text/plain"},
        body=raw_text,
    )
    dto = middleware.hydrate("http://localhost/error", http_resp)
    assert dto.data == "Not JSON Plain text error"
    assert dto.raw_payload == raw_text
    assert dto.metadata.plane == TelemetryPlane.UNKNOWN
