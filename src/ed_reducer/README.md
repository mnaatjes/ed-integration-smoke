# `ed-reducer`

Pure-functional event-driven state reducer engine for materialized *Elite Dangerous* telemetry projections.

## Overview
`ed-reducer` provides deterministic, pure reducers that project incoming `ed-models` domain events (`FSDJump`, `Location`, `Commander`, etc.) and cockpit telemetry (`StatusTelemetry`) into immutable, materialized state snapshots (`ClientStateProjection`).
