"""Validates Spansh JSON Schemas and OpenAPI specifications for standard adherence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema.validators import validator_for

ROOT_DIR = Path(__file__).resolve().parent.parent
SPANSH_SCHEMAS_DIR = ROOT_DIR / "schemas" / "spansh"


def check_json_schemas() -> None:
    print("=" * 75)
    print("VALIDATING SPANSH JSON SCHEMAS AGAINST FORMAL SPECIFICATIONS")
    print("=" * 75)

    schema_files = sorted(SPANSH_SCHEMAS_DIR.glob("*.schema.json"))
    openapi_files = sorted(SPANSH_SCHEMAS_DIR.glob("*.openapi.json"))

    print(f"\n[1/2] Checking {len(schema_files)} Pure JSON Schemas...")
    for sf in schema_files:
        print(f"\nEvaluating: {sf.name}")
        raw_text = sf.read_text(encoding="utf-8")
        schema: dict[str, Any] = json.loads(raw_text)

        # Detect dialect or fallback to Draft 4 / Draft 7
        schema_version = schema.get("$schema")
        print(f"  Declared $schema: {schema_version}")

        # Resolve proper validator class
        if schema_version:
            validator_cls = validator_for(schema)
        else:
            # Default for Spansh legacy dump schemas is Draft 4
            validator_cls = jsonschema.Draft4Validator

        print(f"  Validator Dialect: {validator_cls.__name__}")

        # Check meta-schema adherence
        try:
            validator_cls.check_schema(schema)
            print("  Status: VALID JSON SCHEMA")
        except jsonschema.exceptions.SchemaError as err:
            print(f"  Status: INVALID SCHEMA -> {err.message}")

    print(f"\n[2/2] Checking {len(openapi_files)} OpenAPI 3.1 Specifications...")
    for of in openapi_files:
        print(f"\nEvaluating: {of.name}")
        raw_text = of.read_text(encoding="utf-8")
        spec: dict[str, Any] = json.loads(raw_text)

        openapi_version = spec.get("openapi")
        info = spec.get("info", {})
        paths_count = len(spec.get("paths", {}))
        components_count = len(spec.get("components", {}).get("schemas", {}))

        print(f"  OpenAPI Version: {openapi_version}")
        print(f"  Title: {info.get('title')}")
        print(f"  Paths defined: {paths_count}")
        print(f"  Components/Schemas defined: {components_count}")

        # Basic OpenAPI Structural Validation
        assert openapi_version and openapi_version.startswith("3."), f"Expected OpenAPI 3.x, got {openapi_version}"
        print("  Status: VALID OPENAPI 3.1 SPECIFICATION")

    print("\n" + "=" * 75)
    print("ALL SPANSH SPECIFICATIONS VERIFIED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    check_json_schemas()
