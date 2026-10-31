"""Synthesizes canonical Draft 2020-12 JSON Schemas for Frontier Companion API (CAPI) endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ed_schema import SchemaEngine, create_schema_engine

ROOT_DIR = Path(__file__).resolve().parent.parent
CAPI_SCHEMAS_DIR = ROOT_DIR / "schemas" / "capi"
CAPI_DTOS_DIR = ROOT_DIR / "generated_dtos" / "capi"

CAPI_ENDPOINTS_CATALOG: dict[str, dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 1. GET /profile
    # -------------------------------------------------------------------------
    "profile": {
        "title": "CapiProfileResponse",
        "description": "Full Commander profile, active ship status, loadout, and starport state.",
        "type": "object",
        "properties": {
            "commander": {
                "type": "object",
                "description": "Commander account state, credits, and rank ladders.",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "credits": {"type": "integer"},
                    "debt": {"type": "integer"},
                    "currentShipId": {"type": "integer"},
                    "alive": {"type": "boolean"},
                    "docked": {"type": "boolean"},
                    "rank": {
                        "type": "object",
                        "properties": {
                            "combat": {"type": "integer"},
                            "trade": {"type": "integer"},
                            "explore": {"type": "integer"},
                            "cqc": {"type": "integer"},
                            "soldier": {"type": "integer"},
                            "exobiologist": {"type": "integer"},
                        },
                        "required": ["combat", "trade", "explore"],
                    },
                },
                "required": ["id", "name", "credits", "alive", "docked", "rank"],
            },
            "ship": {
                "type": "object",
                "description": "Active ship specifications, health, and equipped modules.",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "shipName": {"type": "string"},
                    "shipID": {"type": "string"},
                    "free": {"type": "boolean"},
                    "cockpitBreached": {"type": "boolean"},
                    "oxygenRemaining": {"type": "integer"},
                    "value": {
                        "type": "object",
                        "properties": {
                            "hull": {"type": "integer"},
                            "modules": {"type": "integer"},
                            "cargo": {"type": "integer"},
                            "total": {"type": "integer"},
                            "unloaned": {"type": "integer"},
                        },
                        "required": ["hull", "modules", "total"],
                    },
                    "health": {
                        "type": "object",
                        "properties": {
                            "hull": {"type": "integer"},
                            "shield": {"type": "integer"},
                            "shieldUp": {"type": "boolean"},
                            "integrity": {"type": "integer"},
                        },
                        "required": ["hull", "shield", "shieldUp", "integrity"],
                    },
                },
                "required": ["id", "name", "value", "health", "free"],
            },
            "lastSystem": {
                "type": "object",
                "description": "Last recorded star system coordinates and system address.",
                "properties": {
                    "name": {"type": "string"},
                    "id": {"type": "integer"},
                },
                "required": ["name", "id"],
            },
            "lastStarport": {
                "type": "object",
                "description": "Last visited starport, available facilities, and market services.",
                "properties": {
                    "name": {"type": "string"},
                    "id": {"type": "integer"},
                    "services": {
                        "type": "object",
                        "properties": {
                            "dock": {"type": "boolean"},
                            "autodock": {"type": "boolean"},
                            "commodities": {"type": "boolean"},
                            "contacts": {"type": "boolean"},
                            "exploration": {"type": "boolean"},
                            "rearm": {"type": "boolean"},
                            "refuel": {"type": "boolean"},
                            "repair": {"type": "boolean"},
                            "shipyard": {"type": "boolean"},
                            "outfitting": {"type": "boolean"},
                        },
                    },
                },
                "required": ["name", "id"],
            },
        },
        "required": ["commander", "ship", "lastSystem", "lastStarport"],
    },
    # -------------------------------------------------------------------------
    # 2. GET /market
    # -------------------------------------------------------------------------
    "market": {
        "title": "CapiMarketResponse",
        "description": "Starport commodity market pricing, supply, demand, and brackets.",
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "Frontier station MarketID."},
            "name": {"type": "string", "description": "Starport market name."},
            "commodities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "buyPrice": {"type": "integer"},
                        "sellPrice": {"type": "integer"},
                        "meanPrice": {"type": "integer"},
                        "demandBracket": {"type": "integer"},
                        "stockBracket": {"type": "integer"},
                        "stock": {"type": "integer"},
                        "demand": {"type": "integer"},
                        "categoryname": {"type": "string"},
                    },
                    "required": ["id", "name", "buyPrice", "sellPrice", "demand", "stock"],
                },
                "description": "Array of traded commodity listings.",
            },
        },
        "required": ["id", "name", "commodities"],
    },
    # -------------------------------------------------------------------------
    # 3. GET /shipyard
    # -------------------------------------------------------------------------
    "shipyard": {
        "title": "CapiShipyardResponse",
        "description": "Available starport shipyard purchasing catalog and stored vessels.",
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "Station MarketID."},
            "name": {"type": "string", "description": "Station shipyard facility name."},
            "ships": {
                "type": "object",
                "description": "Catalog of available ships for purchase.",
                "properties": {
                    "unavailable_list": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
        "required": ["id", "name"],
    },
    # -------------------------------------------------------------------------
    # 4. GET /fleetcarrier
    # -------------------------------------------------------------------------
    "fleetcarrier": {
        "title": "CapiFleetCarrierResponse",
        "description": "Commander-owned Fleet Carrier telemetries, balances, and jump state.",
        "type": "object",
        "properties": {
            "carrierId": {"type": "integer", "description": "Unique Fleet Carrier ID."},
            "currentStarSystem": {"type": "string", "description": "Current system name."},
            "balance": {"type": "integer", "description": "Carrier account credit balance."},
            "fuel": {"type": "integer", "description": "Remaining Tritium fuel count."},
            "capacity": {
                "type": "object",
                "description": "Tonnage capacity distribution.",
                "properties": {
                    "freeSpace": {"type": "integer"},
                    "usedSpace": {"type": "integer"},
                    "totalSpace": {"type": "integer"},
                },
                "required": ["freeSpace", "usedSpace", "totalSpace"],
            },
            "name": {
                "type": "object",
                "properties": {
                    "callsign": {"type": "string"},
                    "vanityName": {"type": "string"},
                },
                "required": ["callsign"],
            },
        },
        "required": ["carrierId", "currentStarSystem", "balance", "fuel", "capacity", "name"],
    },
}


def generate_capi_schemas() -> list[Path]:
    """Generates canonical Draft 2020-12 JSON Schema files for CAPI endpoints."""
    CAPI_SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    print("=" * 70)
    print("FRONTIER CAPI DRAFT 2020-12 SCHEMA SYNTHESIS")
    print("=" * 70)

    for endpoint, spec in sorted(CAPI_ENDPOINTS_CATALOG.items()):
        schema_dict = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://companion.orerve.net/schemas/{endpoint}#",
            "title": spec["title"],
            "description": spec["description"],
            "type": spec["type"],
            "properties": spec["properties"],
            "required": spec.get("required", []),
        }

        schema_file = CAPI_SCHEMAS_DIR / f"{endpoint}.json"
        schema_file.write_text(json.dumps(schema_dict, indent=2) + "\n", encoding="utf-8")
        generated_files.append(schema_file)
        print(f"Generated CAPI Schema: {schema_file.name} ({spec['title']})")

    print(f"\nSuccessfully synthesized {len(generated_files)} CAPI schemas in {CAPI_SCHEMAS_DIR}")
    return generated_files


def compile_capi_dtos() -> tuple[Path, ...]:
    """Compiles all schemas in schemas/capi into Python dataclasses in generated_dtos/capi."""
    print("\n" + "=" * 70)
    print("COMPILING CAPI SCHEMAS TO TYPED PYTHON DATACLASSES")
    print("=" * 70)

    CAPI_DTOS_DIR.mkdir(parents=True, exist_ok=True)
    engine: SchemaEngine = create_schema_engine()

    compiled_paths = engine.compile_models(
        schema_dir=CAPI_SCHEMAS_DIR,
        output_dir=CAPI_DTOS_DIR,
        class_prefix="Capi",
    )
    print(f"Successfully compiled {len(compiled_paths)} CAPI DTO modules in {CAPI_DTOS_DIR}")
    return tuple(Path(p) for p in compiled_paths)


def main() -> None:
    generate_capi_schemas()
    compile_capi_dtos()


if __name__ == "__main__":
    main()
