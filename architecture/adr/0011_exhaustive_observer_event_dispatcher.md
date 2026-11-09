---
title: "ADR 0011: Exhaustive Observer Event Dispatcher for Hydrated Telemetry"
tags: ["adr", "observer", "event-dispatcher", "pub-sub", "ed-dispatcher", "ed-models"]
created_at: "2026-11-09"
last_updated_at: "2026-11-09"
---

# ADR 0011: Exhaustive Observer Event Dispatcher for Hydrated Telemetry

* **Status:** Accepted
* **Deciders:** Elite Dangerous Fleet Architecture Team
* **Date:** 2026-11-09

---

## 1. Context and Problem Statement

Downstream application developers building cockpit overlays, diagnostic monitors, voice assistants, and analytics engines need an ergonomic, type-safe mechanism to react to incoming telemetry events. 

While `ed_reducer` (ADR 0010) aggregates persistent player state into materialized projections (`ClientStateProjection`), consumers frequently require immediate notifications to trigger side effects (e.g., text-to-speech alerts, UI audio cues, external API synchronizations) for both transient events (`Music`, `ReceiveText`, `FSSSignalDiscovered`) and state-mutating events (`FSDJump`, `Docked`, `StatusTelemetry`).

Without a centralized dispatcher, consumers are forced to manually author repetitive `if isinstance(event, X)` pattern checks inside streaming loops. Furthermore, unhandled exceptions in user callbacks risk terminating the underlying SSE telemetry connection.

We require a decoupled member package (`src/ed_dispatcher`) providing an exhaustive, type-safe event subscription and dispatch engine.

---

## 2. Decision Drivers

* **Type-Safe Callback Registration:** Provide an intuitive `@dispatcher.on(EventType)` decorator and programmatic `subscribe(event_type, handler)` API.
* **Exhaustive Coverage:** Every hydrated `ed-models` domain entity (transient, stateful, and status telemetry) must be dispatachable.
* **Polymorphic Type Inheritance:** Subscriptions to a parent type (e.g. `JournalEvent`) must receive all specialized subtypes, allowing wildcard / audit listeners.
* **Sync and Async Compatibility:** Handlers may be synchronous callables or asynchronous coroutines (`async def`).
* **Fault Isolation:** User callback exceptions must be captured and reported in a `DispatchResult` without crashing the dispatcher or interrupting telemetry ingestion.
* **Clean Unsubscription:** Provide lightweight `Subscription` tokens allowing listeners to detach dynamically.

---

## 3. Considered Options

1. **Option 1: Direct Asyncio Event Queue (`asyncio.Queue`).** Expose raw queues to callers. Rejected because callers must manage their own consumer tasks, worker loops, and type filtering boilerplate.
2. **Option 2: Signal Bus / String Topic Publisher (`blinker` / `PyDispatcher`).** Route events based on string topic names (`"journal.fsd_jump"`). Rejected because string-based routing breaks Python static typing and IDE autocompletion for `ed-models`.
3. **Option 3: Type-Centric Observer Dispatcher (`src/ed_dispatcher`).** Maintain a registry indexed by event class type, supporting inheritance matching, error isolation, and async execution.

---

## 4. Decision Outcome

Chosen option: **Option 3: Type-Centric Observer Dispatcher (`src/ed_dispatcher`)**.

### Positive Consequences
* Complete type safety and IDE autocompletion using `ed-models` classes as subscription targets.
* Resilient execution: user exceptions are isolated and collected.
* Clean integration with the overarching `EliteDangerousClient` facade.

### Negative Consequences
* Handlers executing heavy, blocking CPU work in synchronous handlers could stall sequential dispatch if not properly offloaded to worker threads.
