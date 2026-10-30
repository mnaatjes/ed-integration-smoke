"""Live integration script validating and dispatching an EDDN journal payload to the /test gateway."""

from __future__ import annotations

import dataclasses
import datetime
import json
from pathlib import Path
import sys

# Ensure repository root is on sys.path for direct imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaEngine,
    SchemaKey,
    create_schema_engine,
)
from ed_transport import (
    HttpResponseDTO,
    TransportClient,
    create_transport_client,
)
from generated_dtos.eddn.journal_v1_0 import (
    EddnJournalV10DTO,
    EddnJournalV10HeaderDTO,
    EddnJournalV10MessageDTO,
)

EDDN_GATEWAY_URL = "https://eddn.edcd.io:4430/upload/"
EDDN_TEST_SCHEMA_REF = "https://eddn.edcd.io/schemas/journal/1/test"


def run_live_test_dispatch() -> None:
    root_dir = Path(__file__).resolve().parent.parent
    schemas_dir = root_dir / "schemas" / "eddn"

    print("=" * 70)
    print("EDDN Live Integration Test: Journal Schema Validation & Dispatch")
    print("=" * 70)

    # 1. Initialize Hexagonal Schema Engine & Register Contract
    print("\n[Step 1/4] Registering canonical EDDN Journal contract...")
    engine: SchemaEngine = create_schema_engine()

    class EddnLiveManifest:
        name = "eddn"
        schema_dir = schemas_dir
        endpoints = (
            EndpointContract(
                route="/schemas/journal/1",
                schema_file="journal-v1.0.json",
                model_cls=EddnJournalV10DTO,
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

    engine.load_manifests([EddnLiveManifest])
    key = SchemaKey(namespace="eddn", endpoint="/schemas/journal/1")
    descriptor = engine.resolve_descriptor(key)
    assert descriptor is not None
    print(f"           - Contract registered for route: {descriptor.key.endpoint}")
    print(f"           - Bound Root DTO: {descriptor.model_cls.__name__}")

    # 2. Instantiate Strongly Typed Dataclass Tree
    print("\n[Step 2/4] Constructing typed DTO payload using test schemaRef...")
    current_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    header_dto = EddnJournalV10HeaderDTO(
        uploaderID="ed-integration-smoke-probe",
        softwareName="ed-integration-smoke",
        softwareVersion="1.1.0",
        gameversion="4.0.0.100",
        gamebuild="r291245",
    )

    message_dto = EddnJournalV10MessageDTO(
        timestamp=current_timestamp,
        event="FSDJump",
        StarSystem="Sol",
        StarPos=[0.0, 0.0, 0.0],
        SystemAddress=10477373803,
        horizons=True,
        odyssey=True,
    )

    root_dto = EddnJournalV10DTO(
        schemaRef=EDDN_TEST_SCHEMA_REF,
        header=header_dto,
        message=message_dto,
    )
    print(f"           - Instantiated Root DTO: {root_dto.__class__.__name__}")
    print(f"           - Schema Reference:      {root_dto.schemaRef}")
    print(f"           - Star System:           {root_dto.message.StarSystem}")

    # 3. Serialize & Execute Pre-Flight Contract Validation
    print("\n[Step 3/4] Performing local pre-flight contract validation via ed-schema...")
    # Convert dataclasses to dict, re-introducing the wire key '$schemaRef'
    raw_payload = {
        "$schemaRef": root_dto.schemaRef,
        "header": {
            k: v for k, v in dataclasses.asdict(root_dto.header).items() if v is not None
        },
        "message": {
            k: v for k, v in dataclasses.asdict(root_dto.message).items() if v is not None
        },
    }

    # For validation against canonical Draft-04 schema, remove /test suffix temporarily if needed,
    # or validate with live schemaRef
    canonical_payload = dict(raw_payload)
    canonical_payload["$schemaRef"] = "https://eddn.edcd.io/schemas/journal/1"

    headers = {"Content-Type": "application/json"}
    validation = engine.validate_call(key=key, headers=headers, payload=canonical_payload)
    print(f"           - Local Schema Validation Result: is_valid={validation.is_valid}")
    if not validation.is_valid:
        print(f"           - Validation Errors: {validation.payload_errors}")
        sys.exit(1)

    # 4. Dispatch to EDDN Test Gateway via ed-transport
    print(f"\n[Step 4/4] Dispatching payload to live EDDN Gateway via ed-transport...")
    print(f"           - Target Endpoint: {EDDN_GATEWAY_URL}")
    print(f"           - Wire $schemaRef: {raw_payload['$schemaRef']}")

    transport: TransportClient = create_transport_client()
    body_bytes = json.dumps(raw_payload).encode("utf-8")

    response: HttpResponseDTO = transport.post(
        url=EDDN_GATEWAY_URL,
        headers=headers,
        body=body_bytes,
        timeout=15.0,
    )

    print(f"           - Gateway HTTP Status: {response.status_code}")
    response_text = response.body.decode("utf-8", errors="replace").strip()
    print(f"           - Gateway Response:    {response_text}")

    assert response.status_code == 200, f"Expected HTTP 200 from EDDN, got {response.status_code}: {response_text}"
    assert response_text == "OK", f"Expected 'OK' response from EDDN, got: {response_text}"

    print("\n" + "=" * 70)
    print("SUCCESS: EDDN Live Gateway accepted and validated test payload!")
    print("=" * 70)


if __name__ == "__main__":
    run_live_test_dispatch()
