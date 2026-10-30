"""End-to-end integration script compiling EDDN JSON schema into DTOs and validating data flow."""

import json
from pathlib import Path

from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaEngine,
    SchemaKey,
    create_schema_engine,
)
from ed_transport import (
    HttpRequestDTO,
    create_transport_client,
)


def run() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    schemas_dir = root_dir / "schemas" / "eddn"
    generated_dtos_dir = root_dir / "generated_dtos" / "eddn"

    print("=" * 60)
    print("EDDN Schema Compilation & Interoperability Pipeline")
    print("=" * 60)

    # 1. Initialize Hexagonal Engine
    print("\n[Step 1/5] Initializing SchemaEngine...")
    engine: SchemaEngine = create_schema_engine()

    # 2. Compile Models
    print(f"[Step 2/5] Compiling JSON Schemas from {schemas_dir} -> {generated_dtos_dir}...")
    compiled_files = engine.compile_models(
        schema_dir=schemas_dir,
        output_dir=generated_dtos_dir,
        class_prefix="Eddn",
    )
    for p in compiled_files:
        print(f"           - Compiled: {p.relative_to(root_dir)}")

    # 3. Dynamic Import of the Compiled Model
    print("\n[Step 3/5] Dynamically loading compiled model DTO...")
    import importlib.util
    import sys

    target_module_file = generated_dtos_dir / "journal_v1_0.py"
    assert target_module_file.exists(), f"Expected compiled file not found: {target_module_file}"

    module_name = "generated_dtos.eddn.journal_v1_0"
    spec = importlib.util.spec_from_file_location(module_name, target_module_file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Find the root Model class
    model_cls = getattr(module, "EddnJournalDTO", None) or getattr(
        module, "EddnJournalV10DTO", None
    )
    if not model_cls:
        for attr_name in dir(module):
            if attr_name.startswith("Eddn") and isinstance(getattr(module, attr_name), type):
                model_cls = getattr(module, attr_name)
                break
    assert model_cls is not None, f"Could not locate compiled Eddn DTO in {module}"
    print(f"           - Successfully resolved compiled DTO class: {model_cls.__name__}")

    # 4. Define Manifest & Load Contract
    print("\n[Step 4/5] Declaring and registering EDDN Endpoint Contract with bound model_cls...")

    class EddnManifest:
        name = "eddn"
        schema_dir = schemas_dir
        endpoints = (
            EndpointContract(
                route="/schemas/journal/1",
                schema_file="journal-v1.0.json",
                model_cls=model_cls,
                header_contract=HeaderContract(
                    parameters=(
                        HeaderParameterContract(
                            name="Content-Type",
                            required=True,
                            regex_pattern=r"^application/json.*$",
                        ),
                    )
                ),
            ),
        )

    loaded_count = engine.load_manifests([EddnManifest])
    print(f"           - Ingested {loaded_count} endpoint descriptor(s) into SchemaEngine.")

    # 5. Contract Validation & Hydration Simulation
    print("\n[Step 5/5] Validating outbound contract & simulating pipeline hydration...")
    key = SchemaKey(namespace="eddn", endpoint="/schemas/journal/1")
    descriptor = engine.resolve_descriptor(key)
    assert descriptor is not None
    assert descriptor.model_cls is model_cls

    # Simulate realistic EDDN payload conforming to official journal-v1.0.json
    eddn_payload = {
        "$schemaRef": "https://eddn.edcd.io/schemas/journal/1",
        "header": {
            "uploaderID": "a1b2c3d4e5f6g7h8",
            "softwareName": "EDMarketConnector-Test",
            "softwareVersion": "5.1.0",
        },
        "message": {
            "timestamp": "2026-10-30T02:18:00Z",
            "event": "FSDJump",
            "StarSystem": "Sol",
            "SystemAddress": 10477373803,
            "StarPos": [0.0, 0.0, 0.0],
        },
    }

    headers = {"Content-Type": "application/json"}
    val_res = engine.validate_call(key=key, headers=headers, payload=eddn_payload)
    print(
        f"           - Pre-flight validation result: valid={val_res.is_valid}, "
        f"payload_errors={val_res.payload_errors}, header_errors={val_res.header_errors}"
    )
    assert val_res.is_valid, f"Validation failed: {val_res.payload_errors} {val_res.header_errors}"

    # Transport request construction
    transport = create_transport_client()
    request_dto = HttpRequestDTO(
        url="https://eddn.edcd.io:4430/upload/",
        method="POST",
        headers=headers,
        body=json.dumps(eddn_payload).encode("utf-8"),
    )
    assert request_dto.headers["Content-Type"] == "application/json"
    assert transport is not None

    # Model instantiation
    # Using the bound model_cls directly; schemaRef is cleanly sanitized from $schemaRef.
    # Instantiate child DTOs recursively synthesized by ed-schema v1.1.0:
    header_cls = getattr(module, "EddnJournalV10HeaderDTO")
    message_cls = getattr(module, "EddnJournalV10MessageDTO")

    header_instance = header_cls(
        uploaderID=eddn_payload["header"]["uploaderID"],
        softwareName=eddn_payload["header"]["softwareName"],
        softwareVersion=eddn_payload["header"]["softwareVersion"],
    )
    message_instance = message_cls(
        timestamp=eddn_payload["message"]["timestamp"],
        event=eddn_payload["message"]["event"],
        StarSystem=eddn_payload["message"]["StarSystem"],
        SystemAddress=eddn_payload["message"]["SystemAddress"],
        StarPos=eddn_payload["message"]["StarPos"],
    )

    field_kwargs = {
        "schemaRef": eddn_payload["$schemaRef"],
        "header": header_instance,
        "message": message_instance,
    }
    dto_instance = descriptor.model_cls(**field_kwargs)
    print(f"           - Hydrated Root DTO:    {type(dto_instance).__name__}")
    print(f"           - Schema Ref:           {dto_instance.schemaRef}")
    print(f"           - Child Header DTO:     {type(dto_instance.header).__name__}")
    print(f"           - Software Name (attr): {dto_instance.header.softwareName}")
    print(f"           - Child Message DTO:    {type(dto_instance.message).__name__}")
    print(f"           - Star System (attr):   {dto_instance.message.StarSystem}")

    print("\n" + "=" * 60)
    print("EDDN Pipeline Simulation Completed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run()
