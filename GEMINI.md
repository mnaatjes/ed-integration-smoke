# Context & Developer Environment Guide: `ed-integration-smoke`

## 1. Project Overview & Architecture
`ed-integration-smoke` is an integration sandbox for executing combined workflows across the *Elite Dangerous* software fleet libraries (`ed-schema`, `ed-transport`, `ed-telemetry`).

It verifies contract compliance, request dispatch, and DTO hydration across boundary layers.

---

## 2. Python Virtual Environment & Tooling Paths

The project uses a local virtual environment located at `.venv/` in the repository root:

* **Python Interpreter:** `.venv/bin/python`
* **Pytest:** `.venv/bin/pytest`
* **Ruff (Linter & Formatter):** `.venv/bin/ruff`
* **Type Checker:** `.venv/bin/mypy`

---

## 3. Standard Verification Commands

```bash
# 1. Run all smoke tests:
.venv/bin/pytest

# 2. Run Ruff linter:
.venv/bin/ruff check .

# 3. Run MyPy type checker:
.venv/bin/mypy scripts/ tests/
```
