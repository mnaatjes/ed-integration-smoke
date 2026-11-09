# `ed-services`

Domain calculation engines, stream derivers, and reactive navigation services for *Elite Dangerous* telemetry.

## Architecture
`ed-services` provides derived higher-order telemetry through two complementary patterns:
* **Pattern 1 (State-Guarded Pull):** Synchronous query methods returning `Result[T] | None` guarded against uninitialized preconditions.
* **Pattern 2 (Reactive Stream Pipe):** Internal event observers that compute and dispatch derived events (`NavBearingUpdated`) only when all required parameters are present.
