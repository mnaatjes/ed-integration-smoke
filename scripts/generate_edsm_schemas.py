"""Extracts, synthesizes, and compiles Draft 2020-12 JSON Schemas for EDSM API endpoints."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ed_schema import SchemaEngine, create_schema_engine

ROOT_DIR = Path(__file__).resolve().parent.parent
EDSM_SCHEMAS_DIR = ROOT_DIR / "schemas" / "edsm"
EDSM_DTOS_DIR = ROOT_DIR / "generated_dtos" / "edsm"

BASE_SCHEMA_URL = "https://kayahr.github.io/edsm/schemas"

# Catalog of canonical EDSM schema sources and definitions
CANONICAL_REMOTE_SCHEMAS: dict[str, str] = {
    "system": "system-response.schema.json",
    "system_bodies": "system-bodies-response.schema.json",
    "system_stations": "system-stations-response.schema.json",
    "system_factions": "system-factions-response.schema.json",
    "system_traffic": "system-traffic-response.schema.json",
    "system_deaths": "system-deaths-response.schema.json",
    "system_estimated_value": "system-estimated-value-response.schema.json",
    "station_market": "station-market-response.schema.json",
    "station_shipyard": "station-shipyard-response.schema.json",
    "station_outfitting": "station-outfitting-response.schema.json",
    "elite_server_status": "elite-server-status-response.schema.json",
    "commander_ranks": "commander-ranks-response.schema.json",
    "commander_credits": "commander-credits-response.schema.json",
    "commander_inventory": "commander-inventory-response.schema.json",
    "commander_position": "commander-position-response.schema.json",
    "flight_logs": "flight-logs-response.schema.json",
}

# Supplementary EDSM endpoints not covered by single-object dump schemas
SUPPLEMENTARY_SCHEMAS: dict[str, dict[str, Any]] = {
    "discard": {
        "title": "EdsmDiscardResponse",
        "description": "List of journal event names that EDSM discards from telemetry ingestion.",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "discardedEvents": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of journal event names to be discarded prior to upload.",
            }
        },
        "required": ["discardedEvents"],
    },
    "journal_upload_response": {
        "title": "EdsmJournalUploadResponse",
        "description": "Response envelope returned by EDSM /api-journal-v1 upload endpoint.",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "msgnum": {"type": "integer", "description": "EDSM response code (100 = success)."},
            "msg": {"type": "string", "description": "Status or error message."},
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "msgnum": {"type": "integer"},
                        "msg": {"type": "string"},
                    },
                    "required": ["msgnum", "msg"],
                },
                "description": "Status indicators for each event submitted in the batch.",
            },
        },
        "required": ["msgnum", "msg", "events"],
    },
}


def _dereference_schema(raw_schema: dict[str, Any], name_key: str) -> dict[str, Any]:
    """Recursively dereferences $ref constructs to produce self-contained object schemas."""
    definitions = raw_schema.get("definitions", {})

    def _resolve(node: Any) -> Any:
        if isinstance(node, dict):
            if "$ref" in node and isinstance(node["$ref"], str):
                ref_val = node["$ref"]
                if ref_val.startswith("#/definitions/"):
                    target_key = ref_val.split("/")[-1]
                    target_def = definitions.get(target_key, {})
                    resolved = dict(_resolve(target_def))
                    for k, v in node.items():
                        if k != "$ref":
                            resolved[k] = _resolve(v)
                    return resolved
            return {k: _resolve(v) for k, v in node.items() if k != "definitions"}
        if isinstance(node, list):
            return [_resolve(item) for item in node]
        return node

    resolved_root = _resolve(raw_schema)
    if "$ref" in raw_schema:
        target_name = raw_schema["$ref"].split("/")[-1]
    else:
        target_name = "".join(part.capitalize() for part in name_key.split("_"))

    # Construct clean Draft 2020-12 schema envelope
    title = target_name if target_name.endswith("Response") else f"{target_name}Response"
    clean_schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://edsm.net/schemas/{name_key}#",
        "title": title,
        "type": resolved_root.get("type", "object"),
        "description": resolved_root.get("description", f"EDSM {title} data contract."),
        "properties": resolved_root.get("properties", {}),
        "required": resolved_root.get("required", []),
    }
    return clean_schema


def fetch_and_synthesize_schemas() -> list[Path]:
    """Retrieves EDSM schemas, dereferences definitions, and writes Draft 2020-12 files."""
    EDSM_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    print("=" * 70)
    print("EDSM DRAFT 2020-12 SCHEMA EXTRACTION & GENERATION")
    print("=" * 70)

    # 1. Fetch and process canonical schemas
    for name_key, remote_filename in sorted(CANONICAL_REMOTE_SCHEMAS.items()):
        url = f"{BASE_SCHEMA_URL}/{remote_filename}"
        print(f"Fetching {name_key} from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ed-integration-smoke/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw_schema = json.loads(resp.read().decode("utf-8"))
            synthesized = _dereference_schema(raw_schema, name_key)
        except Exception as exc:
            print(f"  WARNING: Failed fetching {url}: {exc}. Using fallback minimal schema.")
            synthesized = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"https://edsm.net/schemas/{name_key}#",
                "title": f"Edsm{name_key.title().replace('_', '')}Response",
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            }

        out_file = EDSM_SCHEMAS_DIR / f"{name_key}.json"
        out_file.write_text(json.dumps(synthesized, indent=2) + "\n", encoding="utf-8")
        generated_files.append(out_file)
        print(f"  -> Generated {out_file.name}")

    # 2. Generate supplementary schemas
    for name_key, spec in sorted(SUPPLEMENTARY_SCHEMAS.items()):
        schema_dict = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://edsm.net/schemas/{name_key}#",
            "title": spec["title"],
            "type": spec["type"],
            "description": spec["description"],
            "properties": spec["properties"],
            "required": spec.get("required", []),
        }
        out_file = EDSM_SCHEMAS_DIR / f"{name_key}.json"
        out_file.write_text(json.dumps(schema_dict, indent=2) + "\n", encoding="utf-8")
        generated_files.append(out_file)
        print(f"  -> Generated supplementary schema {out_file.name}")

    print(f"\nSuccessfully generated {len(generated_files)} JSON schemas in {EDSM_SCHEMAS_DIR}")
    return generated_files


def compile_edsm_dtos() -> tuple[Path, ...]:
    """Compiles all schemas in schemas/edsm into Python dataclasses in generated_dtos/edsm."""
    print("\n" + "=" * 70)
    print("COMPILING EDSM SCHEMAS TO TYPED PYTHON DATACLASSES")
    print("=" * 70)

    EDSM_DTOS_DIR.mkdir(parents=True, exist_ok=True)
    engine: SchemaEngine = create_schema_engine()

    compiled_paths = engine.compile_models(
        schema_dir=EDSM_SCHEMAS_DIR,
        output_dir=EDSM_DTOS_DIR,
        class_prefix="Edsm",
    )
    print(f"Successfully compiled {len(compiled_paths)} DTO modules in {EDSM_DTOS_DIR}")
    return tuple(Path(p) for p in compiled_paths)


def main() -> None:
    fetch_and_synthesize_schemas()
    compile_edsm_dtos()


if __name__ == "__main__":
    main()
