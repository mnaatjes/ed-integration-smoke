"""Batch compilation and verification script for all canonical EDDN schemas."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

from ed_schema import SchemaEngine, create_schema_engine


def run_batch_compilation() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    schemas_dir = root_dir / "schemas" / "eddn"
    generated_dtos_dir = root_dir / "generated_dtos" / "eddn"

    print("=" * 70)
    print("EDDN Batch Schema Compilation & AST Verification Pipeline")
    print("=" * 70)

    schema_files = sorted(schemas_dir.glob("*.json"))
    print(f"\nDiscovered {len(schema_files)} canonical EDDN JSON schemas in {schemas_dir.name}/")

    engine: SchemaEngine = create_schema_engine()

    print(f"\nCompiling all schemas -> {generated_dtos_dir.relative_to(root_dir)}/...")
    compiled_paths = engine.compile_models(
        schema_dir=schemas_dir,
        output_dir=generated_dtos_dir,
        class_prefix="Eddn",
    )
    print(f"Successfully generated {len(compiled_paths)} Python module files.\n")

    print("-" * 70)
    print(f"{'Schema File':<32} | {'Compiled Module':<28} | {'Status'}")
    print("-" * 70)

    success_count = 0
    failure_count = 0

    for schema_file in schema_files:
        expected_stem = schema_file.stem.replace(".", "_").replace("-", "_")
        module_file = generated_dtos_dir / f"{expected_stem}.py"

        if not module_file.exists():
            print(f"{schema_file.name:<32} | {'MISSING':<28} | FAILED")
            failure_count += 1
            continue

        module_name = f"generated_dtos.eddn.{expected_stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Spec loader could not be created for {module_file}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Check that exported classes exist and can be inspected
            exported = getattr(module, "__all__", ())
            if not exported:
                raise RuntimeError(f"No classes exported in __all__ for {module_file.name}")

            print(f"{schema_file.name:<32} | {module_file.name:<28} | OK ({len(exported)} classes)")
            success_count += 1
        except Exception as exc:
            print(f"{schema_file.name:<32} | {module_file.name:<28} | ERROR: {exc}")
            failure_count += 1

    print("-" * 70)
    print(f"Summary: {success_count} passed, {failure_count} failed out of {len(schema_files)} schemas.")
    print("=" * 70)

    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_batch_compilation()
