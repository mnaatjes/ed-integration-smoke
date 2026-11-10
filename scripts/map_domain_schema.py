#!/usr/bin/env python3
"""Pillar 1: Static Schema Key Correlation Engine.

Introspects all ed_models JournalEvent subclasses to build the canonical
Entity Relational Graph connected by shared primary/foreign keys.
Outputs:
  - architecture/reference/data/domain_entity_graph.json
  - architecture/reference/data/domain_entity_graph.mmd
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import ed_models.core.domain.events as ev_module

CANONICAL_FOREIGN_KEYS = {
    # Spatial
    "SystemAddress",
    "StarSystem",
    "BodyID",
    "Body",
    "BodyType",
    "StationName",
    "StationType",
    # Commercial & Asset
    "MarketID",
    "ShipID",
    "Ship",
    "CarrierID",
    "CarrierType",
    # Identity & Socio-Political
    "Commander",
    "FID",
    "Faction",
    "Power",
    "SquadronID",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extracts the canonical Entity Relational Graph from ed_models."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("architecture/reference/data"),
        help="Directory where output JSON and Mermaid graphs will be written.",
    )
    return parser.parse_args()


def discover_event_models() -> dict[str, dict[str, Any]]:
    """Introspects ed_models.core.domain.events to extract event metadata and field definitions."""
    models: dict[str, dict[str, Any]] = {}

    for name in dir(ev_module):
        obj = getattr(ev_module, name)
        # Filter for concrete classes that represent events
        if (
            isinstance(obj, type)
            and issubclass(obj, ev_module.JournalEvent)
            and obj is not ev_module.JournalEvent
        ):
            mod_name = getattr(obj, "__module__", "")
            # Domain package is the second to last part of the module path
            domain = mod_name.split(".")[-2] if len(mod_name.split(".")) >= 2 else "core"

            fields: list[str] = [
                f for f in dir(obj) if not f.startswith("_") and f not in ("event", "timestamp")
            ]
            foreign_keys = [f for f in fields if f in CANONICAL_FOREIGN_KEYS]

            models[name] = {
                "name": name,
                "domain": domain,
                "module": mod_name,
                "total_fields": len(fields),
                "fields": fields,
                "foreign_keys": sorted(foreign_keys),
            }

    return models


def build_key_inverted_index(models: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Builds an inverted index mapping each canonical key to the events that contain it."""
    index: dict[str, list[str]] = defaultdict(list)
    for model_name, info in models.items():
        for key in info["foreign_keys"]:
            index[key].append(model_name)
    return {
        k: sorted(v) for k, v in sorted(index.items(), key=lambda item: len(item[1]), reverse=True)
    }


def build_domain_affinity_matrix(
    models: dict[str, dict[str, Any]], key_index: dict[str, list[str]]
) -> dict[str, dict[str, int]]:
    """Calculates cross-domain coupling weights based on shared foreign keys."""
    domains = sorted({m["domain"] for m in models.values()})
    matrix: dict[str, dict[str, int]] = {d: {other: 0 for other in domains} for d in domains}

    for events in key_index.values():
        event_domains = [models[ev]["domain"] for ev in events]
        for i, d1 in enumerate(event_domains):
            for j, d2 in enumerate(event_domains):
                if i != j:
                    matrix[d1][d2] += 1

    return matrix


def generate_mermaid_er(key_index: dict[str, list[str]], top_n_keys: int = 8) -> str:
    """Generates a clean Mermaid ER diagram showing top canonical key hubs and domain
    relationships.
    """
    lines = [
        "erDiagram",
        "    %% Canonical Foreign Key Hubs in ed-models",
    ]

    for key, events in list(key_index.items())[:top_n_keys]:
        lines.append(f'    {key} ||--o{{ EVENT : "indexes {len(events)} events"')
        # Display top 4 exemplar events per key
        for ev in events[:4]:
            lines.append(f'    {key} ||--o{{ {ev} : "joins"')

    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    models = discover_event_models()
    key_index = build_key_inverted_index(models)
    affinity = build_domain_affinity_matrix(models, key_index)

    output_data = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "total_events_indexed": len(models),
        "total_canonical_keys": len(key_index),
        "canonical_keys": key_index,
        "domain_affinity_matrix": affinity,
        "models": models,
    }

    json_path = args.output_dir / "domain_entity_graph.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    mmd_path = args.output_dir / "domain_entity_graph.mmd"
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(generate_mermaid_er(key_index))

    print(
        f"Pillar 1 Complete: Indexed {len(models)} models across {len(key_index)} canonical keys."
    )
    print(f"  JSON Artifact: {json_path}")
    print(f"  Mermaid Graph: {mmd_path}")


if __name__ == "__main__":
    main()
