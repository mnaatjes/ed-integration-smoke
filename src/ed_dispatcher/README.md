# `ed-dispatcher`

Type-safe observer and event dispatch engine for hydrated *Elite Dangerous* telemetry domain events.

## Overview
`ed-dispatcher` provides subscription and notification primitives mapping `ed-models` domain events (`JournalEvent` subclasses, `StatusTelemetry`) to registered synchronous or asynchronous callbacks with fault isolation and polymorphic inheritance matching.
