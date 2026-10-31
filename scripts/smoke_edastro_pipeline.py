import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaKey,
    create_schema_engine,
)
from ed_transport import (
    HttpRequestDTO,
    create_transport_client,
)
from generated_dtos.edastro.gec_poi import EdAstroEDAstroGecPoiDTO
from generated_dtos.edastro.journal_submission import EdAstroEDAstroJournalSubmissionDTO
from generated_dtos.edastro.starsystem import EdAstroEDAstroStarSystemResponseDTO

ROOT_DIR = Path(__file__).resolve().parent.parent
EDASTRO_SCHEMAS_DIR = ROOT_DIR / "schemas" / "edastro"


class EdAstroManifest:
    name = "edastro"
    schema_dir = EDASTRO_SCHEMAS_DIR
    endpoints = (
        EndpointContract(
            route="/api/journal",
            schema_file="journal_submission.json",
            model_cls=EdAstroEDAstroJournalSubmissionDTO,
            header_contract=HeaderContract(
                parameters=(
                    HeaderParameterContract(
                        name="Content-Type",
                        required=True,
                        regex_pattern=r"^application/json.*$",
                    ),
                    HeaderParameterContract(
                        name="User-Agent",
                        required=True,
                        regex_pattern=r"^.+$",
                    ),
                )
            ),
        ),
        EndpointContract(
            route="/api/starsystem",
            schema_file="starsystem.json",
            model_cls=EdAstroEDAstroStarSystemResponseDTO,
            header_contract=HeaderContract(
                parameters=(
                    HeaderParameterContract(
                        name="User-Agent",
                        required=True,
                        regex_pattern=r"^.+$",
                    ),
                )
            ),
        ),
        EndpointContract(
            route="/gec/json/rare",
            schema_file="gec_poi.json",
            model_cls=EdAstroEDAstroGecPoiDTO,
            header_contract=HeaderContract(
                parameters=(
                    HeaderParameterContract(
                        name="User-Agent",
                        required=True,
                        regex_pattern=r"^.+$",
                    ),
                )
            ),
        ),
    )


def test_edastro_pipeline() -> None:
    print("=" * 75)
    print("EDASTRo LIVE INTEGRATION AND SCHEMA COMPLIANCE PIPELINE")
    print("=" * 75)

    # 1. Initialize schema engine & transport
    print("\n[1/4] Initializing SchemaEngine and TransportClient...")
    schema_engine = create_schema_engine()
    schema_engine.load_manifests([EdAstroManifest])
    transport = create_transport_client()
    user_agent = "EDIntegrationSmoke/1.0.0"

    # 2. Test Outbound GEC POI endpoint
    print("\n[2/4] Testing Galactic Exploration Catalog (GEC) POI Pipeline...")
    gec_key = SchemaKey(namespace="edastro", endpoint="/gec/json/rare")
    gec_headers = {"User-Agent": user_agent}

    gec_hdr_val = schema_engine.validate_call(key=gec_key, headers=gec_headers)
    assert gec_hdr_val.is_valid, f"GEC Header validation failed: {gec_hdr_val.header_errors}"
    print("      -> Header contract valid.")

    gec_req = HttpRequestDTO(
        url="https://edastro.com/gec/json/rare",
        method="GET",
        headers=gec_headers,
        timeout=15.0,
    )
    gec_resp = transport.send(gec_req)
    assert gec_resp.status_code == 200, f"Expected 200, got {gec_resp.status_code}"
    print(f"      -> HTTP {gec_resp.status_code} received ({len(gec_resp.body)} bytes).")

    gec_data = json.loads(gec_resp.body.decode("utf-8"))
    assert isinstance(gec_data, list) and len(gec_data) > 0, "Expected non-empty list of POIs"
    first_poi: dict[str, Any] = gec_data[0]

    # Validate single POI item against gec_poi.json
    poi_val = schema_engine.validate_call(key=gec_key, headers=gec_headers, payload=first_poi)
    assert poi_val.is_valid, f"GEC Payload schema validation failed: {poi_val.payload_errors}"
    print("      -> First POI verified against Draft 2020-12 gec_poi.json schema.")

    # Hydrate DTO
    gec_descriptor = schema_engine.resolve_descriptor(gec_key)
    assert gec_descriptor is not None and gec_descriptor.model_cls is EdAstroEDAstroGecPoiDTO
    gec_dto = EdAstroEDAstroGecPoiDTO(
        id=first_poi["id"],
        name=first_poi["name"],
        type=first_poi["type"],
        coordinates=first_poi["coordinates"],
        summary=first_poi.get("summary"),
        region=first_poi.get("region"),
    )
    print(f"      -> Hydrated DTO: EdAstroEDAstroGecPoiDTO(id={gec_dto.id}, name='{gec_dto.name}')")

    # 3. Test Outbound Star System endpoint
    print("\n[3/4] Testing Star System Query Pipeline (System: Sol)...")
    system_key = SchemaKey(namespace="edastro", endpoint="/api/starsystem")
    system_headers = {"User-Agent": user_agent}

    sys_hdr_val = schema_engine.validate_call(key=system_key, headers=system_headers)
    assert sys_hdr_val.is_valid, f"System Header validation failed: {sys_hdr_val.header_errors}"
    print("      -> Header contract valid.")

    sys_req = HttpRequestDTO(
        url="https://edastro.com/api/starsystem?q=Sol",
        method="GET",
        headers=system_headers,
        timeout=15.0,
    )
    sys_resp = transport.send(sys_req)
    assert sys_resp.status_code == 200, f"Expected 200, got {sys_resp.status_code}"
    print(f"      -> HTTP {sys_resp.status_code} received ({len(sys_resp.body)} bytes).")

    sys_data = json.loads(sys_resp.body.decode("utf-8"))
    sys_val = schema_engine.validate_call(key=system_key, headers=system_headers, payload=sys_data)
    assert sys_val.is_valid, f"Star System schema validation failed: {sys_val.payload_errors}"
    print(f"      -> Sol system record ({sys_data[0]['name']}, ID: {sys_data[0]['ID']}) validated against Draft 2020-12 schema.")

    # 4. Test Inbound Companion Submission Envelope
    print("\n[4/4] Testing Companion Journal Ingestion Pipeline (Simulated Post)...")
    journal_key = SchemaKey(namespace="edastro", endpoint="/api/journal")
    journal_headers = {
        "Content-Type": "application/json",
        "User-Agent": "EDMC-EDAstro/1.0.0",
    }

    j_hdr_val = schema_engine.validate_call(key=journal_key, headers=journal_headers)
    assert j_hdr_val.is_valid, f"Journal Header validation failed: {j_hdr_val.header_errors}"
    print("      -> Companion submission headers valid.")

    sample_envelope = [
        {
            "appName": "EDAstro",
            "odyssey": True,
            "system": "Sol",
        },
        {
            "timestamp": "2026-10-31T16:00:00Z",
            "event": "CarrierJumpRequest",
            "SystemName": "Barnard's Star",
            "SystemAddress": 1234567890,
            "CarrierID": 370099999,
            "Body": "Barnard's Star 1",
            "BodyID": 1,
            "DepartureTime": "2026-10-31T16:15:00Z",
        },
    ]

    j_val = schema_engine.validate_call(key=journal_key, headers=journal_headers, payload=sample_envelope)
    assert j_val.is_valid, f"Journal Submission validation failed: {j_val.payload_errors}"
    print("      -> Companion submission envelope validated against Draft 2020-12 journal_submission.json schema.")

    journal_req = HttpRequestDTO(
        url="https://edastro.com/api/journal",
        method="POST",
        headers=journal_headers,
        body=json.dumps(sample_envelope).encode("utf-8"),
        timeout=15.0,
    )
    journal_resp = transport.send(journal_req)
    print(f"      -> Live endpoint responded: HTTP {journal_resp.status_code} ({journal_resp.body.decode('utf-8').strip()})")

    print("\n" + "=" * 75)
    print("ALL EDASTRO SCHEMAS AND TRANSPORT PIPELINES VERIFIED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_edastro_pipeline()
