---
title: "ADR 0018: Developer Diagnostics and Connection Verification for ed-fleet-client"
tags: ["adr", "diagnostics", "ed-fleet-client", "developer-experience", "smoke-test"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0018: Developer Diagnostics and Connection Verification for `ed-fleet-client`

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** `ed-integration-smoke` (`scripts/diagnose_telemetry.py`, `ed-fleet-client`)

## 1. Context & Problem Statement

When a user-developer installs `ed-fleet-client` to build telemetry-driven applications, they require a reliable diagnostic utility to verify that their local or remote `ed-telemetry` instance is reachable, authenticated, streaming events, and correctly hydrating domain state.

While `scripts/diagnose_telemetry.py` (ADR 0016, ADR 0017) exercises HTTP REST endpoints and basic class attributes:
1. `create_client()` was instantiated without connection configuration, causing client-level calls to target hardcoded default endpoints rather than CLI `--target` and `--api-key` options.
2. `client.get_snapshot` was invoked with mismatched argument ordering (`base_url` instead of `snapshot_name`).
3. Streaming ingestion was never validated end-to-end; `client.connect()` was never run, leaving event processing and live state hydration untested.
4. Developers lacked machine-readable outputs (`--json`) for automated pipelines and actionable remediation guidance when diagnostic checks failed.

## 2. Decision

Enhance `scripts/diagnose_telemetry.py` to serve as a comprehensive developer verification tool:

1. **Explicit Client Connection Configuration:**
   - Parse `--target` into host and port.
   - Construct `TelemetryConnectionConfig(host=host, port=port, api_key=api_key)` and supply it to `create_client(config=config)`.
   - Correct `client.get_snapshot(name, endpoint)` parameter mapping.

2. **Bounded Asynchronous Stream Smoke Probe (`--stream-probe [seconds]`):**
   - Provide an active event streaming probe (defaulting to 2.0s in `--game-running` mode, configurable via `--stream-probe`).
   - Execute `client.connect()` inside an asynchronous task, listen for SSE frames and state engine sequence increments, and cleanly disconnect.
   - Report stream connectivity, event count/sequence delta, and elapsed latency in real time.

3. **Machine-Readable Diagnostics (`--json`):**
   - Provide a `--json` CLI flag to output structured diagnostic telemetry (results, pass/fail metrics, latencies) for CI/CD and developer scripting.

4. **Actionable Remediation Guidance:**
   - On diagnostic failure, print contextual remediation hints (e.g. server reachability, API key verification, game running state, journal directory configuration).

## 3. Consequences

- **Positive:** Gives developers a bulletproof diagnostic command (`diagnose_telemetry.py --target <host> --game-running`) that verifies both the raw server infrastructure and the high-level `ed-fleet-client` reactive runtime.
- **Negative / Trade-offs:** The streaming probe introduces an intentional bounded latency (e.g., 1–2 seconds) when `--game-running` or `--stream-probe` is active, which is necessary to capture real-time SSE frames.
