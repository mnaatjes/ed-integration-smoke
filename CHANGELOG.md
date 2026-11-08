# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Authored [ADR 0006](architecture/adr/0006_workspace_driven_monorepo_architecture.md) recording repository migration to a UV workspace-driven monorepo architecture and fleet upstream decoupling.
- Created reusable workspace subpackage `src/ed_telemetry_client` (`ed-telemetry-client`) for connecting to `ed-telemetry` REST endpoints via `ed-transport`.
- Implemented `TelemetryHttpClient` with configurable connection settings (defaults: host `192.168.1.214`, port `8080`, target path `/api/v1/state`), API key authentication injection (`X-API-Key` and `Authorization: Bearer`), and ETag caching headers.
- Implemented `MetadataHydrationMiddleware` capturing and hydrating endpoint headers (`X-Telemetry-Plane`, `X-Telemetry-Source`, `ETag`, `Content-Type`) and roundtrip latency into `EndpointMetadata`.
- Defined `TelemetryResponseDTO[T]` unifying hydrated domain metadata and deserialized payload bodies.
- Added pytest unit test suite under `src/ed_telemetry_client/tests/test_client.py` validating client defaults, metadata parsing, convenience endpoints, and error handling.

### Changed
- Refactored repository root `pyproject.toml` into a UV workspace configuring `[tool.uv.workspace] members = ["src/*"]`.
- Updated Elite Dangerous fleet dependencies to latest upstream versions:
  - `ed-schema`: `v1.1.0`
  - `ed-transport`: `main` (rev `f0b0476`)
  - `ed-models`: `v0.2.1`
  - `ed-resolver`: `v0.2.0`
  - `ed-telemetry`: `v0.9.0`
- Configured Ruff and MyPy rules across the monorepo for Python 3.13.

### Removed
- Removed deprecated local `schemas/` directory; schemas are now canonically imported directly from upstream `ed-schema`.
- Removed legacy `generated_dtos/` directory across Spansh, EDDN, EDSM, Inara, EDMC CAPI, and EDAstro.
- Purged obsolete legacy scripts, tests, and documentation.
- Cleared local database and mismatch logs in `data/`.

