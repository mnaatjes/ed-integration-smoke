# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Authored [ADR 0019](architecture/adr/0019_ed_sdk_meta_tooling_architecture.md) defining the meta-tooling vs. runtime facade architecture for `ed-sdk`, establishing scaffolding, diagnostics (`doctor`), AI agent MCP server, offline telemetry mocks, and clean separation from `ed-fleet-client`.
- Authored [ADR 0018](architecture/adr/0018_developer_diagnostics_and_connection_verification.md) defining developer diagnostics, connection configuration, and streaming probe verification for `ed-fleet-client`.
- Enhanced [`scripts/diagnose_telemetry.py`](scripts/diagnose_telemetry.py) with:
  - Explicit `TelemetryConnectionConfig` configuration binding `--target` (host/port) and `--api-key` into `create_client(config=config)`.
  - Live SSE streaming smoke probe (`--stream-probe`, `--probe-duration`) verifying active event ingestion and state reduction sequence progression.
  - Corrected `client.get_snapshot(name, endpoint)` argument ordering.
  - Machine-readable `--json` output format for CI and developer automation.
  - Actionable remediation advice on check failures.
- Authored EDMC Tkinter UI research ([`architecture/research/edmc_ui_architecture.md`](architecture/research/edmc_ui_architecture.md)) and component library specification ([`architecture/research/tkinter_component_library.md`](architecture/research/tkinter_component_library.md)).
- Authored [ADR 0015](architecture/adr/0015_hexagonal_gui_core_and_component_library_architecture.md) and [SDD-004](architecture/designs/SDD-004_hexagonal_gui_core_and_legacy_edmc_components.md) defining a Hexagonal (Ports & Adapters) GUI core.
- Created workspace subpackage `src/ed_gui_core` (`ed-gui-core`) with `domain`, `ports`, and `adapters/tkinter/legacy_edmc` (`shell`, `theme`, `telemetry`, `settings`, `bridge`).
- Created presentation-only EDMC GUI preview script [`scripts/preview_edmc_gui.py`](scripts/preview_edmc_gui.py) using `ed_gui_core`.
- Authored [ADR 0013](architecture/adr/0013_reactive_domain_services_and_stream_derivers.md) detailing reactive domain services and stream derivers across Pattern 1 (State-Guarded Pull) and Pattern 2 (Reactive Stream Pipe).
- Created workspace subpackage `src/ed_services` (`ed-services`) providing abstract `TelemetryService` contract and specialized domain services:
  - `NavigationService`: Surface great-circle bearing, distance, heading deflection, target locking, and hyperspace route progress.
  - `OrbitalMechanicsService`: Keplerian equation solver and 3D orbital propagation ($x, y, z$ in light-seconds) for scanned celestial bodies.
  - `FlightPerformanceService`: Real-time vessel mass computation, mass-scaled jump reach, and fuel consumption burn rate.
  - `CombatAnalyticsService`: Real-time DPS dealt/received, Time-To-Kill estimation, and SYS capacitor pip shield damage resistance modeling.
  - `AstrophysicsService`: Stellar luminosity via Stefan-Boltzmann law and liquid-water habitable zone boundary evaluations.
- Mounted domain services onto `EliteDangerousClient` facade (`client.nav`, `client.orbital`, `client.performance`, `client.combat`, `client.astrophysics`).
- Created live terminal dashboard script [`scripts/live_ship_dashboard.py`](scripts/live_ship_dashboard.py) powered by `ed_cli_core` and `ed_fleet_client` featuring cockpit annunciator grid, power distribution meters, and real-time surface navigation vectors.
- [Conversation UUID: `350dc601-cf64-423f-b4bf-696d0d5a3070`]
- Authored [ADR 0006](architecture/adr/0006_workspace_driven_monorepo_architecture.md) recording repository migration to a UV workspace-driven monorepo architecture and fleet upstream decoupling.
- Created reusable workspace subpackage `src/ed_telemetry_client` (`ed-telemetry-client`) for connecting to `ed-telemetry` REST endpoints via `ed-transport`.
- Implemented `TelemetryHttpClient` with configurable connection settings (defaults: host `192.168.1.214`, port `8080`, target path `/api/v1/state`), API key authentication injection (`X-API-Key` and `Authorization: Bearer`), and ETag caching headers.
- Implemented `MetadataHydrationMiddleware` capturing and hydrating endpoint headers (`X-Telemetry-Plane`, `X-Telemetry-Source`, `ETag`, `Content-Type`) and roundtrip latency into `EndpointMetadata`.
- Defined `TelemetryResponseDTO[T]` unifying hydrated domain metadata and deserialized payload bodies.
- Added pytest unit test suite under `src/ed_telemetry_client/tests/test_client.py` validating client defaults, metadata parsing, convenience endpoints, and error handling.

### Changed
- Adopted upstream `ed-fleet-client` (`v0.1.0`) from `https://github.com/mnaatjes/ed-fleet-client.git` in `pyproject.toml`.
- Refactored repository root `pyproject.toml` into a UV workspace configuring `[tool.uv.workspace] members = ["src/*"]`.
- Updated Elite Dangerous fleet dependencies to latest upstream versions:
  - `ed-schema`: `v1.1.0`
  - `ed-transport`: `main` (rev `f0b0476`)
  - `ed-models`: `v0.2.1`
  - `ed-resolver`: `v0.2.0`
  - `ed-telemetry`: `v0.9.0`
- Configured Ruff and MyPy rules across the monorepo for Python 3.13.

### Removed
- Removed 7 superseded prototype submodules from `src/` (`ed_dispatcher`, `ed_fleet_client`, `ed_hydrator`, `ed_reducer`, `ed_services`, `ed_stream_monitor`, `ed_telemetry_client`) while preserving `src/ed_cli_core`.
- Removed deprecated local `schemas/` directory; schemas are now canonically imported directly from upstream `ed-schema`.
- Removed legacy `generated_dtos/` directory across Spansh, EDDN, EDSM, Inara, EDMC CAPI, and EDAstro.
- Purged obsolete legacy scripts, tests, and documentation.
- Cleared local database and mismatch logs in `data/`.

