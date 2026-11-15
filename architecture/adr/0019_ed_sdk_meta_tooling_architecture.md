---
title: "ADR 0019: Meta-Tooling vs. Runtime Facade Architecture for ed-sdk"
tags: ["adr", "ed-sdk", "ed-fleet-client", "developer-tooling", "mcp", "architecture"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# ADR 0019: Meta-Tooling vs. Runtime Facade Architecture for `ed-sdk`

- **Status:** Proposed
- **Date:** 2026-11-15
- **Context:** Elite Dangerous Fleet Ecosystem (`ed-fleet-client`, `ed-sdk`, `ed-telemetry`, `ed-gui-core`)

## 1. Context & Problem Statement

As the Elite Dangerous software fleet matures toward external developer adoption, a clear architectural boundary is required between runtime client libraries and developer-facing toolchains.

Developers building plugins (e.g. EDMC extensions), desktop HUDs, or headless event listeners require:
1. Fast scaffolding and dependency management.
2. Comprehensive connectivity and environment auditing (`doctor`).
3. Offline telemetry mocking and playback harnesses during automated tests (`pytest`).
4. Native integration with AI coding agents via the Model Context Protocol (MCP).

If these developer-centric capabilities are integrated directly into `ed-fleet-client`, production applications will suffer from facade bloat, bloated dependency graphs (inheriting test mocks, CLI engines, and MCP protocols), and increased security/attack surface. Conversely, if an `ed-sdk` is introduced as an all-encompassing senior runtime facade wrapping `ed-fleet-client`, every production application is forced to depend on `ed-sdk`.

## 2. Decision

We establish the **Meta-Tool vs. Runtime Facade Decoupling Pattern** across the fleet:

1. **`ed-sdk` Operational Boundary (Workstation Plane):**
   `ed-sdk` serves strictly as the developer's scaffolding, test harness, and agent toolchain residing on the development workstation. It interacts with projects in two complementary capacities:
   - **At Setup & Build Time (CLI & Toolchain):** Manages project initialization, audits connectivity (`doctor`), generates boilerplates, and hosts the MCP server.
   - **At Development & Test Time (Fixtures & Mocks):** Supplies test harnesses and mock telemetry fixtures during `pytest`.
   - **Never Ships in Production:** `ed-sdk` is never included in `[project.dependencies]`. It is installed globally via `pipx` or declared exclusively under `[dependency-groups] dev`.

2. **Runtime Code Plane (`ed-fleet-client`):**
   In production and runtime application source code (`src/`), application logic interacts directly with `ed-fleet-client` (`create_client()`, `client.state`, `client.navigation`, `client.on()`), not through an intermediary `ed-sdk` wrapper.

3. **Core CLI Command Surface in `ed-sdk`:**
   - **`ed-sdk init <project-name> --template <template>`:**
     Scaffolds clean repository structures with compliant `pyproject.toml`, `.gitignore`, `ruff.toml`, and typed stubs. Populates `[project.dependencies]` with runtime packages (`ed-fleet-client`, `ed-gui-core`) and `[dependency-groups] dev` with `ed-sdk` and `pytest`.
   - **`ed-sdk add <module>`:**
     Intelligently appends fleet dependencies into the local `pyproject.toml` with pinned/compatible versions.
   - **`ed-sdk doctor --target <host:port> [--game-running]`:**
     Executes environment and infrastructure diagnostics (migrated from `diagnose_telemetry.py`), auditing daemon reachability, API keys, journal access, SSE stream ingestion, and state engine hydration.
   - **`ed-sdk mcp [--transport stdio|sse] [--target <host:port>]`:**
     Hosts a Model Context Protocol daemon for AI coding agents (Antigravity, Claude Desktop, Cursor), exposing tools:
     - `get_telemetry_state`: Live JSON inspection of ship coordinates, pips, cargo, system.
     - `list_journal_schemas`: Returns typed schemas for Frontier journal events.
     - `replay_telemetry_sample`: Injects mock journal events into a local test stream.
     - `run_diagnostics`: Runs health audits on the running daemon.
   - **`ed-sdk mock --journal-dir ./fixtures/samples/ --port 8080`:**
     Spins up a lightweight mock `ed-telemetry` HTTP/SSE server serving recorded flight logs so developers can build and test UI/logic offline without running the game.
   - **`ed-sdk install-telemetry [--service]`:**
     Optional convenience command for single-machine gaming setups (where the game and development occur on the same host) to install and configure the standalone `ed-telemetry` daemon.

4. **`ed-telemetry` Architectural Boundary & Decoupling:**
   - **No Hard Dependency:** `ed-telemetry` is **not** a hard dependency of `ed-sdk`. This keeps `ed-sdk` lightweight, cross-platform (installable across macOS, Linux, and Windows), and avoids requiring game journal path configurations on developer machines that do not host the game.
   - **Heterogeneous Topologies:** Supports split-machine sim gaming topologies (game running on dedicated Windows PC or Steam Deck, development on Linux/macOS) by allowing `ed-sdk doctor` to probe remote hosts and output actionable setup instructions.
   - **Zero-Setup Mocking:** `ed-sdk mock` is bundled out of the box to enable immediate development and CI test execution without requiring a live game client or local daemon.

5. **Testing & Test Harness Contract:**
   Test suites (`tests/`) import test harnesses directly from `ed-sdk`:
   ```python
   import pytest
   from ed_sdk.testing import MockTelemetryHarness

   @pytest.fixture
   def test_client():
       with MockTelemetryHarness(sample="docked_station") as harness:
           yield harness.client
   ```

6. **Scaffolding & Dependency Declaration Pattern:**
   ```toml
   [project]
   name = "commander-hud"
   dependencies = [
       "ed-fleet-client>=0.1.0",
       "ed-gui-core>=0.1.0",     # optional GUI components
   ]

   [dependency-groups]
   dev = [
       "ed-sdk>=0.1.0",           # Development harness, mocks, test fixtures
       "pytest>=8.0.0",
   ]
   ```

## 3. Consequences

- **Positive:**
  - **Zero Production Bloat:** Production applications bundle only `ed-fleet-client` and runtime peers, keeping binary sizes minimal and startup fast.
  - **Standardized Developer Onboarding:** New developers scaffold fully configured, linted, and type-checked fleet applications with a single command (`ed-sdk init`).
  - **Agent-Aided Acceleration:** Built-in MCP server arms AI coding assistants with deep telemetry inspection, schema lookup, and diagnostic capabilities without modifying application source code.
  - **Offline Resilience:** Developers can develop and run CI test pipelines without requiring a running game client or remote daemon via `MockTelemetryHarness`.
- **Negative / Trade-offs:**
  - Requires maintaining two separate repositories/packages (`ed-fleet-client` for runtime and `ed-sdk` for tooling).
  - Version alignment must be preserved between `ed-sdk` scaffolding templates and released versions of `ed-fleet-client`.
