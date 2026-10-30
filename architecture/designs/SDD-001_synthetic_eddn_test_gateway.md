---
title: "SDD-001: Synthetic EDDN Test Gateway Architecture & Pytest Fixture"
tags: ["sdd", "architecture", "test-architecture", "eddn", "simulation", "pytest"]
created_at: "2026-10-30"
last_updated_at: "2026-10-30"
---

# SDD-001: Synthetic EDDN Test Gateway Architecture & Pytest Fixture

## 1. Executive Summary & Problem Context

Testing integration fleets across `ed-schema`, `ed-transport`, and `ed-connectors` against the live remote EDDN gateway (`https://eddn.edcd.io:4430/upload/`) presents significant operational liabilities:
1. **Network Flakiness & Non-Deterministic Latency:** Remote calls introduce variance, timeout risks, and potential CI failures due to external network blips.
2. **Inability to Inject Failure Scenarios:** The live gateway cannot be commanded to return `503 Service Unavailable`, `429 Too Many Requests`, `500 Internal Server Error`, or `404 Not Found` on demand, preventing automated testing of client retry policies, sliding window rate limiters, and offline request spooling.
3. **No Inbound Request Ledger:** Client code cannot inspect what was actually received on the wire to assert header case-insensitivity, exact body bytes, or payload scrubbing.

This specification details a zero-dependency, in-process synthetic HTTP test double modeling the EDDN gateway for deterministic unit, integration, and scenario testing.

---

## 2. Architectural Design & Operating Modes

The synthetic gateway operates as a configurable HTTP server running on `127.0.0.1` during test execution, exposing the canonical `/upload/` route and an inspection API:

```mermaid
flowchart TD
    Client["Client Under Test (ed-transport / ed-connectors)"] -->|POST /upload/| Gateway["MockEddnGateway (Local HTTP Server)"]

    subgraph StateModes ["Simulation Modes"]
        M1["Mode: VALIDATING (Upstream Draft-04 JSON Schema Engine)"]
        M2["Mode: STATIC_RESPONSE (200, 400, 404, 500, 503)"]
        M3["Mode: RATE_LIMIT (429 + Retry-After)"]
        M4["Mode: LATENCY (Injected Sleep)"]
    end

    Gateway --> StateModes
    Gateway --> Ledger["Inbound Request Journal (CapturedRequest)"]

    StateModes -->|HTTP Response Code + Body| Client
    TestRunner["Pytest Test Scenario"] -->|assert gateway.received_requests| Ledger
    TestRunner -->|gateway.set_mode(...)| Gateway
```

### 2.1 Simulation Modes

1. **`GatewayMode.STRICT_VALIDATION` (Default):**
   - Ingests incoming `$schemaRef` and extracts the corresponding local canonical schema from `schemas/eddn/`.
   - Validates payload using `ed_schema.core.ports.driving.SchemaValidatorPort` (`jsonschema`).
   - If valid: returns `HTTP 200 OK`.
   - If invalid: returns `HTTP 400 FAIL: <validation error>`, matching upstream EDDN behavior.
2. **`GatewayMode.STATIC_STATUS(status_code, body=None, headers=None)`:**
   - Immediately returns the configured status code (e.g. `404`, `500`, `503`) to verify client resilience, fallback error handling, and spool routing.
3. **`GatewayMode.RATE_LIMITED(retry_after_seconds)`:**
   - Emits `HTTP 429 Too Many Requests` with `Retry-After: <seconds>` to verify exponential backoff and rate limiter compliance.
4. **`GatewayMode.SEQUENCE([response_1, response_2, ...])`:**
   - Returns responses in sequence (e.g. `503` on first 2 calls, then `200` on 3rd call) to verify client retry and recovery behaviors.

---

## 3. Data Structures & Fixture Interface

### 3.1 Captured Request Ledger

Every request received by the mock server is recorded in an immutable ledger:

```python
@dataclass(frozen=True)
class CapturedRequest:
    method: str
    path: str
    headers: dict[str, str]
    body: bytes
    json_payload: dict[str, Any] | None
    timestamp: float
```

### 3.2 Fixture API (`mock_eddn_gateway`)

```python
def test_resilience(mock_eddn_gateway: MockEddnGateway) -> None:
    # 1. Inspect URL
    url = mock_eddn_gateway.upload_url  # http://127.0.0.1:<port>/upload/

    # 2. Configure Failure Mode
    mock_eddn_gateway.simulate_status(503, body="Service Temporarily Unavailable")

    # 3. Execute Client Request
    response = client.post(url, ...)
    assert response.status_code == 503

    # 4. Assert Inbound Request Ledger
    assert len(mock_eddn_gateway.received_requests) == 1
    assert mock_eddn_gateway.received_requests[0].method == "POST"
```

---

## 4. Implementation Details

- **Transport Mechanism:** Uses Python standard library `http.server.HTTPServer` running in a dedicated daemon thread on an ephemeral OS-assigned port (`port=0`).
- **Zero Heavy External Dependencies:** Pure Python standard library implementation ensuring fast test startup and compatibility across all platforms (Linux, macOS, Windows).
- **Cleanup & Tear-down:** Pytest fixture guarantees `server.shutdown()` and thread termination at fixture exit.
