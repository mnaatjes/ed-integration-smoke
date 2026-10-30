"""Demonstration harness proving SchemaRegistry access to schemas and recursive DTO trees."""

from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path
import sys
from typing import Any, get_args, get_origin, get_type_hints

from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaEngine,
    SchemaKey,
    create_schema_engine,
)


def _render_dto_tree(cls: type, prefix: str = "", visited: set[type] | None = None) -> list[str]:
    """Recursively traverses a dataclass type hint graph and renders an ASCII tree."""
    if visited is None:
        visited = set()

    lines: list[str] = []
    if cls in visited:
        lines.append(f"{prefix}└── <circular reference to {cls.__name__}>")
        return lines
    visited.add(cls)

    hints = get_type_hints(cls)
    fields = list(dataclasses.fields(cls))

    for idx, field in enumerate(fields):
        is_last = idx == len(fields) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        f_type = hints.get(field.name, field.type)
        is_opt = field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING
        opt_str = " [optional]" if is_opt else " [required]"

        # Check for nested dataclass
        if dataclasses.is_dataclass(f_type):
            lines.append(f"{prefix}{connector}{field.name}: {f_type.__name__}{opt_str}")
            lines.extend(_render_dto_tree(f_type, child_prefix, visited.copy()))
        elif (
            get_origin(f_type) is list
            and get_args(f_type)
            and dataclasses.is_dataclass(get_args(f_type)[0])
        ):
            item_cls = get_args(f_type)[0]
            lines.append(f"{prefix}{connector}{field.name}: list[{item_cls.__name__}]{opt_str}")
            lines.extend(_render_dto_tree(item_cls, child_prefix, visited.copy()))
        else:
            type_repr = getattr(f_type, "__name__", str(f_type)).replace("typing.", "")
            lines.append(f"{prefix}{connector}{field.name}: {type_repr}{opt_str}")

    return lines


def run_proof() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    schemas_root = root_dir / "schemas"
    generated_dtos_root = root_dir / "generated_dtos"

    engine: SchemaEngine = create_schema_engine()
    namespaces = [d.name for d in sorted(schemas_root.iterdir()) if d.is_dir()]

    total_endpoints_count = 0
    namespace_endpoints: dict[str, list[tuple[Path, str, type | None]]] = {}

    for ns in namespaces:
        schemas_dir = schemas_root / ns
        generated_dtos_dir = generated_dtos_root / ns
        schema_files = sorted(schemas_dir.glob("*.json"))

        # Load compiled DTO modules into sys.modules and index root classes
        dto_map: dict[str, type] = {}
        for py_file in sorted(generated_dtos_dir.glob("*.py")):
            if py_file.stem == "__init__":
                continue
            mod_name = f"generated_dtos.{ns}.{py_file.stem}"
            spec = importlib.util.spec_from_file_location(mod_name, py_file)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
                all_classes = getattr(mod, "__all__", ())
                if all_classes:
                    root_class_name = all_classes[-1]
                    dto_map[py_file.stem] = getattr(mod, root_class_name)

        endpoints: list[EndpointContract] = []
        ns_records: list[tuple[Path, str, type | None]] = []

        for s_file in schema_files:
            clean_stem = s_file.stem.replace(".", "_").replace("-", "_").lower()
            root_dto = dto_map.get(clean_stem)
            route_name = f"/{s_file.stem}"

            endpoints.append(
                EndpointContract(
                    route=route_name,
                    schema_file=s_file.name,
                    model_cls=root_dto,
                    header_contract=HeaderContract(
                        parameters=(
                            HeaderParameterContract(
                                name="Content-Type",
                                required=True,
                                regex_pattern=r"^application/json.*$",
                            ),
                        )
                    ),
                )
            )
            ns_records.append((s_file, route_name, root_dto))

        class NamespaceManifest:
            name = ns
            schema_dir = schemas_dir
            endpoints: tuple[EndpointContract, ...] = ()

        NamespaceManifest.endpoints = tuple(endpoints)
        engine.load_manifests([NamespaceManifest])
        namespace_endpoints[ns] = ns_records
        total_endpoints_count += len(endpoints)

    print("=" * 80)
    print("MULTI-NAMESPACE SCHEMA REGISTRY RESOLUTION & DTO REFLECTION PROOF")
    print("=" * 80)
    print(f"Namespaces: {', '.join(namespaces)}")
    print(f"Total Registered Endpoints: {total_endpoints_count}\n")

    for ns, records in namespace_endpoints.items():
        print(f"\n{'#' * 80}")
        print(f"### NAMESPACE: [{ns}] ({len(records)} Schemas & Registered Endpoints)")
        print(f"{'#' * 80}\n")

        for s_file, route_name, expected_dto in records:
            key = SchemaKey(namespace=ns, endpoint=route_name)
            descriptor = engine.resolve_descriptor(key)

            assert descriptor is not None, f"Failed resolving key: {key}"
            assert descriptor.schema_definition is not None, "Schema definition not hydrated!"
            assert descriptor.model_cls is not None, f"Model class not bound for {s_file.name}!"

            schema_id = (
                descriptor.schema_definition.get("id")
                or descriptor.schema_definition.get("$id")
                or "N/A"
            )
            schema_title = descriptor.schema_definition.get("title", s_file.stem)
            root_cls = descriptor.model_cls

            print(f"┌─ Endpoint: [{ns}] {key.endpoint} (Schema: {s_file.name})")
            print(f"│  ├─ Canonical URI:     {schema_id}")
            print(f"│  ├─ Schema Title:      {schema_title}")
            print(f"│  ├─ Raw Schema Keys:   {tuple(descriptor.schema_definition.keys())}")
            print(f"│  ├─ Bound Root DTO:    {root_cls.__module__}.{root_cls.__name__}")
            print(f"│  └─ Recursive DTO Type Graph:")

            tree_lines = _render_dto_tree(root_cls, prefix="│     ")
            for line in tree_lines:
                print(line)
            print("└" + "─" * 79 + "\n")

    print("=" * 80)
    print(
        f"PROOF COMPLETE: All {total_endpoints_count} schemas across {len(namespaces)} "
        "namespaces successfully resolved and verified!"
    )
    print("=" * 80)


if __name__ == "__main__":
    run_proof()
