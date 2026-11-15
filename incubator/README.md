---
title: "Incubator Subpackages Governance"
tags: ["incubator", "subpackages", "governance", "taxonomy"]
created_at: "2026-11-15"
last_updated_at: "2026-11-15"
---

# Incubator Subpackages Governance

The `incubator/` directory houses multi-file, experimental library subpackages candidate for future extraction into standalone *Elite Dangerous* software fleet repositories.

Per [ADR 0021](../architecture/adr/0021_repository_taxonomy_incubator_and_apps_topology.md), code residing here represents reusable domain libraries, protocol drivers, or client utilities that require iterative refinement in the integration sandbox before becoming autonomous fleet packages.

## Structure & Layout

Each incubated library must be fully self-contained using standard `src-layout`:

```
incubator/<candidate_package>/
├── pyproject.toml               # PEP 621 package metadata & local dependencies
├── src/
│   └── <candidate_package>/     # Pure Python package source code
│       ├── __init__.py
│       └── ...
└── tests/                       # Package-level unit test suite
    ├── __init__.py
    └── test_*.py
```

## Incubator Lifecycle & Quality Gates

An incubated package advances through the following phases:

1. **Spike & Exploration:** Initial prototyping, rapid API iteration, and empirical verification against live endpoints.
2. **Standardization:** Refactoring into clean architecture layers (domain, ports, adapters), adding type hints, and establishing unit test coverage.
3. **Workspace Integration:** When ready for local consumption across the integration workbench, register the subpackage in the root `pyproject.toml`:
   ```toml
   [tool.uv.workspace]
   members = ["incubator/*"]
   ```
4. **Promotion / Extraction Gate:**
   - 100% test pass rate with coverage across public interfaces.
   - Clean `ruff` and `mypy --strict` compliance.
   - Inception documentation (ADR, SDD) authored in `architecture/`.
   - Extraction to a dedicated repository (`github.com/mnaatjes/<package-name>`) via repository template or `git subtree`.
