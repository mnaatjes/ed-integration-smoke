"""Generalized parity and structural depth test suite for all schema targets and generated DTOs."""

from __future__ import annotations

import dataclasses
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, get_args, get_origin, get_type_hints

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SCHEMAS_ROOT = ROOT_DIR / "schemas"
GENERATED_DTOS_ROOT = ROOT_DIR / "generated_dtos"


def _discover_all_schemas() -> list[tuple[str, Path]]:
    """Discovers all (namespace, schema_path) pairs across schemas/."""
    discovered = []
    if not SCHEMAS_ROOT.exists():
        return discovered

    for ns_dir in sorted(SCHEMAS_ROOT.iterdir()):
        if not ns_dir.is_dir():
            continue
        namespace = ns_dir.name
        for schema_file in sorted(ns_dir.glob("*.json")):
            discovered.append((namespace, schema_file))
    return discovered


ALL_SCHEMAS = _discover_all_schemas()


@pytest.mark.parametrize(
    ("namespace", "schema_file"),
    ALL_SCHEMAS,
    ids=[f"{ns}:{p.name}" for ns, p in ALL_SCHEMAS],
)
def test_schema_dto_structural_parity(namespace: str, schema_file: Path) -> None:
    """Verifies that every JSON schema has a matching compiled DTO module with deep typing."""
    # 1. Assert corresponding Python module exists
    clean_stem = re.sub(r"[^0-9a-zA-Z_]+", "_", schema_file.stem).lower().strip("_")
    module_path = GENERATED_DTOS_ROOT / namespace / f"{clean_stem}.py"
    assert module_path.exists(), (
        f"Missing generated DTO module for schema {schema_file}. "
        f"Expected path: {module_path}"
    )

    # 2. Dynamically import the module
    module_name = f"generated_dtos.{namespace}.{clean_stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None, f"Failed creating spec for {module_path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # 3. Assert module exports valid dataclasses in __all__
    exported_names = getattr(module, "__all__", ())
    assert len(exported_names) > 0, f"Module {module_name} must export class names in __all__."

    root_class_name = exported_names[-1]
    root_cls = getattr(module, root_class_name, None)
    assert root_cls is not None, f"Root class {root_class_name} not found in {module_name}."
    assert dataclasses.is_dataclass(root_cls), f"{root_cls} must be a dataclass."
    assert root_cls.__dataclass_params__.frozen, f"{root_cls} must be frozen=True."

    # 4. Load raw JSON schema definition
    raw_schema = json.loads(schema_file.read_text(encoding="utf-8"))
    assert isinstance(raw_schema, dict), f"Schema {schema_file} root must be an object."

    schema_properties = raw_schema.get("properties", {})
    schema_required = set(raw_schema.get("required", []))

    # 5. Assert root class fields match schema properties and requirements
    type_hints = get_type_hints(root_cls)
    field_map = {f.name: f for f in dataclasses.fields(root_cls)}

    for prop_name, prop_spec in schema_properties.items():
        # Account for identifier sanitization (e.g. $schemaRef -> schemaRef)
        sanitized_prop_name = prop_name.lstrip("$")
        assert sanitized_prop_name in field_map, (
            f"Field '{sanitized_prop_name}' (from schema prop '{prop_name}') "
            f"missing from {root_cls.__name__} in {module_path.name}."
        )

        field = field_map[sanitized_prop_name]
        is_required = prop_name in schema_required

        # Requirement parity check
        if is_required:
            assert field.default is dataclasses.MISSING, (
                f"Field '{sanitized_prop_name}' in {root_cls.__name__} is required in schema, "
                f"but has default: {field.default}."
            )
        else:
            assert field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING, (
                f"Field '{sanitized_prop_name}' in {root_cls.__name__} is optional in schema, "
                f"but marked as required (default is MISSING)."
            )

        # Depth & Nesting parity check: Object properties must resolve to child dataclasses
        prop_type = prop_spec.get("type") if isinstance(prop_spec, dict) else None
        if prop_type == "object" and isinstance(prop_spec.get("properties"), dict):
            field_type = type_hints.get(sanitized_prop_name, field.type)
            # Unwrap Optional (Union[T, None])
            actual_type = field_type
            if get_origin(field_type) is type(None):
                pass
            args = get_args(field_type)
            if args:
                non_none = [a for a in args if a is not type(None)]
                if non_none:
                    actual_type = non_none[0]

            assert dataclasses.is_dataclass(actual_type), (
                f"Child object '{sanitized_prop_name}' in {root_cls.__name__} must resolve "
                f"to a compiled dataclass, got: {actual_type}."
            )
            assert actual_type.__dataclass_params__.frozen, (
                f"Child dataclass {actual_type} must be frozen=True."
            )
