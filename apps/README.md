---
title: "Prototype & Reference Applications Index"
tags: ["apps", "prototypes", "reference-apps", "taxonomy"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Prototype & Reference Applications Index

The `apps/` directory houses runnable, end-to-end prototype and reference applications that compose multiple *Elite Dangerous* fleet packages (`ed-fleet-client`, `ed-ui-tk`, `ed-ui-cli`, `ed-telemetry`, etc.) and incubated libraries.

Per [ADR 0021](../architecture/adr/0021_repository_taxonomy_incubator_and_apps_topology.md), applications are runnable deployment targets rather than reusable libraries. They serve to validate user experience, UI responsiveness, event streaming throughput, and composition root ergonomics under realistic runtime conditions.

## Structure & Layout

Each prototype application must reside in its own self-contained directory:

```
apps/<app_name>/
├── README.md              # Application runbook, runtime prerequisites, and usage guide
├── main.py                # Executable entry point and composition root
├── config.py              # Application settings and connection parameters
├── views/                 # Presentation views (Tkinter frames, Textual screens, web assets)
└── assets/                # Local static assets, icons, or mock data (if required)
```

## Application Governance Rules

* **Dependency Direction:** Applications depend inward on fleet libraries (`ed-fleet-client`, `ed-ui-core`, `ed-ui-cli`, `ed-ui-tk`) or local `incubator/*` modules. Fleet libraries must never depend on code in `apps/`.
* **Execution Independence:** Each application must include a clear `README.md` documenting the exact launch command (e.g., `uv run python apps/cockpit_station/main.py`) and required runtime environment (e.g., display server, running `ed-telemetry` mock).
* **Disposable Prototypes:** Unlike canonical fleet libraries, applications here can be modified or retired freely as integration experiments conclude.
