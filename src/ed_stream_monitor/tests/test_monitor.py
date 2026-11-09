"""Unit tests for ed_stream_monitor package."""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

from ed_stream_monitor import FileDeltaDTO, TelemetryStreamMonitor


def test_file_delta_dto_from_dict() -> None:
    data = {
        "topic": "telemetry.file_delta",
        "target": "ModulesInfo.json",
        "action": "modified",
        "raw_hash": "43ef64b8e02f00b2",
        "timestamp": "2026-11-09T00:20:00+00:00",
    }
    dto = FileDeltaDTO.from_dict(data)
    assert dto.target == "ModulesInfo.json"
    assert dto.action == "modified"
    assert dto.raw_hash == "43ef64b8e02f00b2"
    assert dto.timestamp.year == 2026


def test_listen_deltas_parses_stream_and_filters() -> None:
    chunk1 = b'data: {"event":"connected"}\n\n'
    chunk2 = b'data: {"topic":"telemetry.journal","payload":"{\\"event\\":\\"Docked\\"}"}\n\n'
    chunk3 = (
        b'data: {"topic":"telemetry.file_delta","target":"ModulesInfo.json",'
        b'"action":"modified","raw_hash":"hash123","timestamp":"2026-11-09T00:20:00Z"}\n\n'
    )
    chunk4 = (
        b'data: {"topic":"telemetry.file_delta","target":"Cargo.json",'
        b'"action":"modified","raw_hash":"hash456","timestamp":"2026-11-09T00:20:01Z"}\n\n'
    )
    sample_stream = io.BytesIO(chunk1 + chunk2 + chunk3 + chunk4)

    monitor = TelemetryStreamMonitor()

    with patch("ed_stream_monitor.monitor.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = sample_stream
        mock_urlopen.return_value = mock_resp

        # Test filtering for only ModulesInfo
        deltas = list(monitor.listen_deltas(filter_targets={"ModulesInfo"}))
        assert len(deltas) == 1
        assert deltas[0].target == "ModulesInfo.json"
        assert deltas[0].raw_hash == "hash123"


def test_listen_raw_parses_messages() -> None:
    line = (
        b'data: {"topic":"telemetry.journal","timestamp":"2026-11-09T00:20:00Z",'
        b'"payload":"{\\"event\\":\\"FSDJump\\"}"}\n\n'
    )
    sample_stream = io.BytesIO(line)

    monitor = TelemetryStreamMonitor()

    with patch("ed_stream_monitor.monitor.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = sample_stream
        mock_urlopen.return_value = mock_resp

        msgs = list(monitor.listen_raw())
        assert len(msgs) == 1
        assert msgs[0].topic == "telemetry.journal"
