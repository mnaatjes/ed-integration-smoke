"""Synthetic EDDN Gateway test double and controller."""

from __future__ import annotations

import collections
from dataclasses import dataclass, field
from enum import Enum, auto
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import threading
import time
from typing import Any, Callable

from ed_schema import SchemaEngine, SchemaKey, create_schema_engine


class GatewayMode(Enum):
    """Operational simulation modes for the MockEddnGateway."""

    STRICT_VALIDATION = auto()
    STATIC_STATUS = auto()
    RATE_LIMITED = auto()
    SEQUENCE = auto()


@dataclass(frozen=True)
class CapturedRequest:
    """Immutable record of an inbound HTTP request received by the mock gateway."""

    method: str
    path: str
    headers: dict[str, str]
    body: bytes
    json_payload: dict[str, Any] | None
    timestamp: float


@dataclass
class MockResponse:
    """Pre-configured response descriptor."""

    status_code: int = 200
    body: str | bytes = "OK"
    headers: dict[str, str] = field(default_factory=dict)


class MockEddnGateway:
    """In-process mock server controller modeling the EDDN gateway."""

    def __init__(self, schemas_dir: Path | None = None) -> None:
        self.schemas_dir = schemas_dir or (
            Path(__file__).resolve().parent.parent.parent / "schemas" / "eddn"
        )
        self.mode = GatewayMode.STRICT_VALIDATION
        self.static_response = MockResponse()
        self.response_sequence: collections.deque[MockResponse] = collections.deque()
        self.received_requests: list[CapturedRequest] = []
        self._lock = threading.Lock()

        self.schema_engine = create_schema_engine()
        self._schema_routes: dict[str, str] = {}
        self._load_local_schemas()

        # Spin up HTTP server on an OS-allocated ephemeral port
        gateway_controller = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                pass  # Suppress default noisy stderr logging during tests

            def do_POST(self) -> None:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len) if content_len > 0 else b""
                json_data = None
                try:
                    if body:
                        json_data = json.loads(body.decode("utf-8"))
                except Exception:
                    pass

                req = CapturedRequest(
                    method="POST",
                    path=self.path,
                    headers={k: v for k, v in self.headers.items()},
                    body=body,
                    json_payload=json_data,
                    timestamp=time.time(),
                )
                with gateway_controller._lock:
                    gateway_controller.received_requests.append(req)

                status_code, resp_body, resp_hdrs = gateway_controller._handle_request(req)

                self.send_response(status_code)
                for h_name, h_val in resp_hdrs.items():
                    self.send_header(h_name, h_val)
                self.end_headers()

                if isinstance(resp_body, str):
                    self.wfile.write(resp_body.encode("utf-8"))
                elif isinstance(resp_body, bytes):
                    self.wfile.write(resp_body)

            def do_GET(self) -> None:
                self.send_response(405)
                self.end_headers()
                self.wfile.write(b"Method Not Allowed")

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port: int = self._server.server_port
        self.host: str = self._server.server_address[0]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    @property
    def upload_url(self) -> str:
        """Returns the full synthetic upload endpoint URL."""
        return f"http://{self.host}:{self.port}/upload/"

    def _load_local_schemas(self) -> None:
        if not self.schemas_dir.exists():
            return
        from ed_schema import EndpointContract

        endpoints = []
        for s_file in self.schemas_dir.glob("*.json"):
            try:
                data = json.loads(s_file.read_text(encoding="utf-8"))
                schema_id = data.get("id") or data.get("$id")
                route = f"/{s_file.stem}"
                endpoints.append(
                    EndpointContract(
                        route=route,
                        schema_file=s_file.name,
                    )
                )
                if schema_id:
                    clean_id = schema_id.rstrip("#")
                    self._schema_routes[schema_id] = route
                    self._schema_routes[clean_id] = route
                    self._schema_routes[f"{clean_id}/test"] = route
            except Exception:
                pass

        if endpoints:
            class EddnMockManifest:
                name = "mock_eddn"
                schema_dir = self.schemas_dir
                endpoints = ()

            EddnMockManifest.endpoints = tuple(endpoints)
            self.schema_engine.load_manifests([EddnMockManifest])

    def _handle_request(self, req: CapturedRequest) -> tuple[int, str | bytes, dict[str, str]]:
        if req.path.rstrip("/") != "/upload":
            return 404, "Not Found", {"Content-Type": "text/plain"}

        if self.mode == GatewayMode.STATIC_STATUS:
            return (
                self.static_response.status_code,
                self.static_response.body,
                self.static_response.headers or {"Content-Type": "text/plain"},
            )

        if self.mode == GatewayMode.RATE_LIMITED:
            retry_after = self.static_response.headers.get("Retry-After", "5")
            return (
                429,
                "Too Many Requests",
                {"Content-Type": "text/plain", "Retry-After": retry_after},
            )

        if self.mode == GatewayMode.SEQUENCE:
            if self.response_sequence:
                resp = self.response_sequence.popleft()
                return resp.status_code, resp.body, resp.headers or {"Content-Type": "text/plain"}
            return 200, "OK", {"Content-Type": "text/plain"}

        # Default STRICT_VALIDATION mode
        if not req.json_payload or not isinstance(req.json_payload, dict):
            return 400, "FAIL: Malformed JSON or empty body", {"Content-Type": "text/plain"}

        schema_ref = req.json_payload.get("$schemaRef")
        if not schema_ref:
            return 400, "FAIL: Missing '$schemaRef' in payload", {"Content-Type": "text/plain"}

        matched_route = self._schema_routes.get(schema_ref) or self._schema_routes.get(schema_ref.rstrip("#"))
        if not matched_route:
            base_ref = schema_ref.replace("/test", "")
            matched_route = self._schema_routes.get(base_ref) or self._schema_routes.get(f"{base_ref}#")

        if not matched_route:
            return 400, f"FAIL: Unknown or unsupported schemaRef '{schema_ref}'", {"Content-Type": "text/plain"}

        key = SchemaKey(namespace="mock_eddn", endpoint=matched_route)
        val_result = self.schema_engine.validate_call(
            key=key,
            headers=req.headers,
            payload=req.json_payload,
        )

        # Also check for EDDN disallowed properties ($ref to #/definitions/disallowed)
        desc = self.schema_engine.resolve_descriptor(key)
        if desc and isinstance(req.json_payload.get("message"), dict):
            msg_props = desc.schema_definition.get("properties", {}).get("message", {}).get("properties", {})
            for m_key in req.json_payload["message"]:
                spec = msg_props.get(m_key)
                if isinstance(spec, dict) and spec.get("$ref") == "#/definitions/disallowed":
                    return 400, f"FAIL: Schema validation error: Disallowed property '{m_key}' in message", {"Content-Type": "text/plain"}

        if val_result.is_valid:
            return 200, "OK", {"Content-Type": "text/plain"}

        err_msgs = "; ".join(e.message for e in val_result.payload_errors)
        return 400, f"FAIL: Schema validation error: {err_msgs}", {"Content-Type": "text/plain"}

    def reset(self) -> None:
        """Resets the mock state and clears all captured requests."""
        with self._lock:
            self.mode = GatewayMode.STRICT_VALIDATION
            self.static_response = MockResponse()
            self.response_sequence.clear()
            self.received_requests.clear()

    def simulate_status(
        self,
        status_code: int,
        body: str | bytes = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        """Configures the mock to return a fixed HTTP status code."""
        with self._lock:
            self.mode = GatewayMode.STATIC_STATUS
            self.static_response = MockResponse(
                status_code=status_code,
                body=body or f"Status {status_code}",
                headers=headers or {},
            )

    def simulate_rate_limit(self, retry_after_seconds: int = 5) -> None:
        """Configures the mock to emit HTTP 429 with Retry-After header."""
        with self._lock:
            self.mode = GatewayMode.RATE_LIMITED
            self.static_response = MockResponse(
                status_code=429,
                body="Too Many Requests",
                headers={"Retry-After": str(retry_after_seconds)},
            )

    def simulate_sequence(self, responses: list[MockResponse]) -> None:
        """Configures the mock to return a sequence of responses."""
        with self._lock:
            self.mode = GatewayMode.SEQUENCE
            self.response_sequence = collections.deque(responses)

    def close(self) -> None:
        """Shuts down the server and closes the socket."""
        self._server.shutdown()
        self._server.server_close()
