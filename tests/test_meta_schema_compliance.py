"""Automated meta-schema compliance test suite for all fleet JSON Schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from jsonschema.exceptions import SchemaError

ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_ROOT = ROOT_DIR / "schemas"


def _discover_all_schema_paths() -> list[tuple[str, Path]]:
    """Discovers all (namespace, schema_file) paths across the schemas directory."""
    discovered: list[tuple[str, Path]] = []
    if not SCHEMAS_ROOT.exists():
        return discovered

    for ns_dir in sorted(SCHEMAS_ROOT.iterdir()):
        if not ns_dir.is_dir():
            continue
        namespace = ns_dir.name
        for schema_file in sorted(ns_dir.glob("*.json")):
            discovered.append((namespace, schema_file))
    return discovered


ALL_SCHEMAS = _discover_all_schema_paths()


@pytest.mark.parametrize(
    ("namespace", "schema_file"),
    ALL_SCHEMAS,
    ids=[f"{ns}:{p.name}" for ns, p in ALL_SCHEMAS],
)
def test_schema_conforms_to_standard_meta_schema(namespace: str, schema_file: Path) -> None:
    """Asserts that every JSON schema conforms to its declared standard specification."""
    raw_content = schema_file.read_text(encoding="utf-8")
    try:
        schema_dict: dict[str, Any] = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        pytest.fail(f"Invalid JSON syntax in {schema_file}: {exc}")

    assert isinstance(schema_dict, dict), f"Schema root in {schema_file} must be an object"

    # Select the canonical meta-schema validator class based on declared $schema
    validator_cls = jsonschema.validators.validator_for(schema_dict)

    try:
        validator_cls.check_schema(schema_dict)
    except SchemaError as err:
        pytest.fail(
            f"Schema '{schema_file.name}' in namespace '{namespace}' violates "
            f"standard JSON Schema meta-schema ({validator_cls.__name__}):\n"
            f"Validator: {err.validator}\n"
            f"Message: {err.message}\n"
            f"Path: {' -> '.join(str(p) for p in err.path)}"
        )
