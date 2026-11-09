# `ed-fleet-client`

Unified reactive client SDK and state facade for *Elite Dangerous* telemetry services.

## Architecture
`ed-fleet-client` coordinates internal fleet libraries into a unified client facade (`EliteDangerousClient`):
* **Group A (Reactive Subscriptions):** `@client.on(EventType)` decorator with error isolation.
* **Group B (State Projections):** Live thread-safe `client.state` (`location`, `ship`, `session`).
* **Group C (Query Services):** Synchronous telemetry queries (`get_status()`, `get_latest_journal()`).
* **Group D (Lifecycle Management):** Blocking (`start()`), background worker (`start_background()`), and generator (`stream()`).
