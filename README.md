# ed-integration-smoke

Fleet-wide integration, smoke testing, and experimental script harness for the *Elite Dangerous* software fleet.

## Overview
`ed-integration-smoke` serves as an isolated runtime sandbox to orchestrate multi-package pipelines combining:
* `ed-schema`: JSON Schema registry, contract validation, and DTO model binding.
* `ed-transport`: Resilient HTTP dispatch, rate-limiting, and retry mechanisms.
* `ed-telemetry` (when applicable): Local journal monitoring and telemetry distribution.

It provides a safe environment for executing end-to-end integration scripts, live API probe tests, and simulated connector pipelines without imposing cross-library dependencies on leaf packages.

## Setup & Running

```bash
# 1. Create and sync the virtual environment using uv
uv sync

# 2. Run the integration test suite
.venv/bin/pytest

# 3. Run the sample smoke script
.venv/bin/python scripts/smoke_capi_pipeline.py
```
