"""Extracts and synthesizes clean Draft 2020-12 schemas from Spansh OpenAPI and dump specifications with full recursive dereferencing, then compiles typed Python dataclasses via ed-schema."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from ed_schema import SchemaEngine, create_schema_engine

ROOT_DIR = Path(__file__).resolve().parent.parent
SPANSH_RAW_DIR = ROOT_DIR / "schemas" / "spansh"
SPANSH_SYNTH_DIR = ROOT_DIR / "schemas" / "spansh_compiled"
SPANSH_DTOS_DIR = ROOT_DIR / "generated_dtos" / "spansh"


def _dereference_spansh(node: Any, components: dict[str, Any], depth: int = 0) -> Any:
    if depth > 20:
        return {"type": "object"}

    if isinstance(node, dict):
        if "$ref" in node:
            ref_val = node["$ref"]
            ref_name = ref_val.split("/")[-1]
            if ref_name in components:
                target = copy.deepcopy(components[ref_name])
                # Inline target properties
                return _dereference_spansh(target, components, depth + 1)
            return {"type": "object"}

        new_dict: dict[str, Any] = {}
        for k, v in node.items():
            new_dict[k] = _dereference_spansh(v, components, depth + 1)

        # OpenAPI 3.1 `nullable: true` -> JSON Schema Draft 2020-12 `type: [<type>, "null"]`
        if new_dict.get("nullable") is True:
            existing_type = new_dict.get("type")
            if isinstance(existing_type, str):
                new_dict["type"] = [existing_type, "null"]
            elif isinstance(existing_type, list) and "null" not in existing_type:
                new_dict["type"] = existing_type + ["null"]
            del new_dict["nullable"]

        return new_dict

    if isinstance(node, list):
        return [_dereference_spansh(item, components, depth + 1) for item in node]

    return node


def synthesize_spansh_models() -> list[Path]:
    SPANSH_SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    print("=" * 75)
    print("EXTRACTING & RECURSIVELY DEREFERENCING SPANSH SCHEMAS TO DRAFT 2020-12")
    print("=" * 75)

    with open(SPANSH_RAW_DIR / "model.openapi.json", encoding="utf-8") as f:
        model_openapi = json.load(f)

    components = model_openapi.get("components", {}).get("schemas", {})
    print(f"Total components available: {len(components)}")

    # Extract all object and enum definitions into standalone dereferenced schemas
    for name, schema_def in components.items():
        title = f"Spansh{name}"
        dereferenced_def = _dereference_spansh(schema_def, components)

        synth_schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://spansh.co.uk/schemas/{name.lower()}#",
            "title": title,
            "description": dereferenced_def.get("description", f"Spansh {name} contract."),
        }

        if "type" in dereferenced_def:
            synth_schema["type"] = dereferenced_def["type"]
        if "properties" in dereferenced_def:
            synth_schema["properties"] = dereferenced_def["properties"]
        if "required" in dereferenced_def:
            synth_schema["required"] = dereferenced_def["required"]
        if "enum" in dereferenced_def:
            synth_schema["enum"] = dereferenced_def["enum"]
        if "items" in dereferenced_def:
            synth_schema["items"] = dereferenced_def["items"]

        out_path = SPANSH_SYNTH_DIR / f"{name.lower()}.json"
        out_path.write_text(json.dumps(synth_schema, indent=2) + "\n", encoding="utf-8")
        generated_files.append(out_path)

    # Also dereference dump schemas: galaxy, systems, factions
    for dump_name in ["systems", "galaxy", "factions"]:
        raw_path = SPANSH_RAW_DIR / f"{dump_name}.schema.json"
        if not raw_path.exists():
            continue
        with open(raw_path, encoding="utf-8") as f:
            dump_raw = json.load(f)

        defs = dump_raw.get("definitions", {})
        merged_defs = {**components, **defs}

        root_ref = dump_raw.get("$ref", "")
        def_key = root_ref.split("/")[-1] if root_ref else list(defs.keys())[0]
        root_def = defs.get(def_key, {})
        dereferenced_dump = _dereference_spansh(root_def, merged_defs)

        dump_schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://spansh.co.uk/schemas/dump_{dump_name}#",
            "title": f"SpanshDump{dump_name.capitalize()}",
            "description": dump_raw.get("description", f"Spansh {dump_name} dump contract."),
            "type": dereferenced_dump.get("type", "object"),
            "properties": dereferenced_dump.get("properties", {}),
            "required": dereferenced_dump.get("required", []),
        }
        if "items" in dereferenced_dump:
            dump_schema["items"] = dereferenced_dump["items"]

        out_path = SPANSH_SYNTH_DIR / f"dump_{dump_name}.json"
        out_path.write_text(json.dumps(dump_schema, indent=2) + "\n", encoding="utf-8")
        generated_files.append(out_path)

    print(f"Generated {len(generated_files)} dereferenced schemas in {SPANSH_SYNTH_DIR}")
    return generated_files


def compile_spansh_dtos() -> None:
    SPANSH_DTOS_DIR.mkdir(parents=True, exist_ok=True)
    engine: SchemaEngine = create_schema_engine()

    print("\n" + "=" * 75)
    print("COMPILING SPANSH SCHEMAS TO TYPED PYTHON DATACLASSES")
    print("=" * 75)

    compiled = engine.compile_models(
        schema_dir=SPANSH_SYNTH_DIR,
        output_dir=SPANSH_DTOS_DIR,
        class_prefix="Spansh",
    )
    print(f"Successfully compiled {len(compiled)} DTO modules in {SPANSH_DTOS_DIR}")


if __name__ == "__main__":
    synthesize_spansh_models()
    compile_spansh_dtos()
