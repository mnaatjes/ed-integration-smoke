"""Extracts and synthesizes clean Draft 2020-12 schemas from Spansh OpenAPI and dump specifications, then compiles typed Python dataclasses via ed-schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ed_schema import SchemaEngine, create_schema_engine

ROOT_DIR = Path(__file__).resolve().parent.parent
SPANSH_RAW_DIR = ROOT_DIR / "schemas" / "spansh"
SPANSH_SYNTH_DIR = ROOT_DIR / "schemas" / "spansh_compiled"
SPANSH_DTOS_DIR = ROOT_DIR / "generated_dtos" / "spansh"


def synthesize_spansh_models() -> list[Path]:
    SPANSH_SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    print("=" * 75)
    print("EXTRACTING SPANSH COMPONENT MODELS TO DRAFT 2020-12 SCHEMAS")
    print("=" * 75)

    with open(SPANSH_RAW_DIR / "model.openapi.json", encoding="utf-8") as f:
        model_openapi = json.load(f)

    components = model_openapi.get("components", {}).get("schemas", {})
    print(f"Total components available: {len(components)}")

    # Extract all object and enum definitions into standalone schemas
    for name, schema_def in components.items():
        # Clean up refs to point locally or clean up types
        raw_def = dict(schema_def)
        title = f"Spansh{name}"

        # Build clean Draft 2020-12 schema
        synth_schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://spansh.co.uk/schemas/{name.lower()}#",
            "title": title,
            "description": raw_def.get("description", f"Spansh {name} contract."),
        }

        if "type" in raw_def:
            synth_schema["type"] = raw_def["type"]
        if "properties" in raw_def:
            synth_schema["properties"] = raw_def["properties"]
        if "required" in raw_def:
            synth_schema["required"] = raw_def["required"]
        if "enum" in raw_def:
            synth_schema["enum"] = raw_def["enum"]
        if "items" in raw_def:
            synth_schema["items"] = raw_def["items"]

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
        # Find the primary root object definition
        root_ref = dump_raw.get("$ref", "")
        def_key = root_ref.split("/")[-1] if root_ref else list(defs.keys())[0]
        root_def = defs.get(def_key, {})

        dump_schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://spansh.co.uk/schemas/dump_{dump_name}#",
            "title": f"SpanshDump{dump_name.capitalize()}",
            "description": dump_raw.get("description", f"Spansh {dump_name} dump contract."),
            "type": root_def.get("type", "object"),
            "properties": root_def.get("properties", {}),
            "required": root_def.get("required", []),
        }
        if "items" in root_def:
            dump_schema["items"] = root_def["items"]

        out_path = SPANSH_SYNTH_DIR / f"dump_{dump_name}.json"
        out_path.write_text(json.dumps(dump_schema, indent=2) + "\n", encoding="utf-8")
        generated_files.append(out_path)

    print(f"Generated {len(generated_files)} synthesized schemas in {SPANSH_SYNTH_DIR}")
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
