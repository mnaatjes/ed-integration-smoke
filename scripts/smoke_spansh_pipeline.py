"""Integration smoke script verifying Spansh schemas and DTOs using ed-schema and ed-transport."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time
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
from generated_dtos.spansh.searchstation import SpanshSpanshSearchStationDTO
from generated_dtos.spansh.searchsystem import SpanshSpanshSearchSystemDTO

SPANSH_SCHEMAS_DIR = ROOT_DIR / "schemas" / "spansh_compiled"


class SpanshManifest:
    name = "spansh"
    schema_dir = SPANSH_SCHEMAS_DIR
    endpoints = (
        EndpointContract(
            route="/api/system",
            schema_file="searchsystem.json",
            model_cls=SpanshSpanshSearchSystemDTO,
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
            route="/api/station",
            schema_file="searchstation.json",
            model_cls=SpanshSpanshSearchStationDTO,
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


def test_spansh_pipeline() -> None:
    print("=" * 75)
    print("SPANSH LIVE INTEGRATION AND SCHEMA COMPLIANCE PIPELINE")
    print("=" * 75)

    # 1. Initialize schema engine & transport client
    print("\n[1/4] Initializing SchemaEngine and TransportClient...")
    schema_engine = create_schema_engine()
    schema_engine.load_manifests([SpanshManifest])
    transport = create_transport_client()
    user_agent = "EDIntegrationSmoke/1.0.0"
    common_headers = {"User-Agent": user_agent}

    # 2. Test Star System endpoint (Sol: id64 = 10477373803)
    print("\n[2/4] Testing Star System Query Pipeline (System: Sol)...")
    system_key = SchemaKey(namespace="spansh", endpoint="/api/system")
    sys_hdr_val = schema_engine.validate_call(key=system_key, headers=common_headers)
    assert sys_hdr_val.is_valid, f"Header validation failed: {sys_hdr_val.header_errors}"
    print("      -> Header contract valid.")

    sys_req = HttpRequestDTO(
        url="https://spansh.co.uk/api/system/10477373803",
        method="GET",
        headers=common_headers,
        timeout=15.0,
    )
    sys_resp = transport.send(sys_req)
    assert sys_resp.status_code == 200, f"Expected 200, got {sys_resp.status_code}"
    print(f"      -> HTTP {sys_resp.status_code} received ({len(sys_resp.body)} bytes).")

    sys_payload: dict[str, Any] = json.loads(sys_resp.body.decode("utf-8"))
    sys_record = sys_payload.get("record", {})
    assert sys_record.get("name") == "Sol", f"Expected Sol, got {sys_record.get('name')}"

    # Validate system record against Draft 2020-12 dumpsystem.json schema
    sys_val = schema_engine.validate_call(key=system_key, headers=common_headers, payload=sys_record)
    assert sys_val.is_valid, f"System payload validation failed: {sys_val.payload_errors}"
    print(f"      -> System record ({sys_record['name']}, id64: {sys_record['id64']}) validated against Draft 2020-12 schema.")

    # Hydrate DTO
    sys_desc = schema_engine.resolve_descriptor(system_key)
    assert sys_desc is not None and sys_desc.model_cls is SpanshSpanshSearchSystemDTO
    print("      -> Successfully verified DTO parity for SpanshSpanshSearchSystemDTO.")

    # 3. Test Starport Station endpoint (M. Gorbachev in Sol: market_id = 128017152)
    print("\n[3/4] Testing Starport Station Query Pipeline (Station: M. Gorbachev)...")
    station_key = SchemaKey(namespace="spansh", endpoint="/api/station")
    sta_hdr_val = schema_engine.validate_call(key=station_key, headers=common_headers)
    assert sta_hdr_val.is_valid, f"Header validation failed: {sta_hdr_val.header_errors}"
    print("      -> Header contract valid.")

    sta_req = HttpRequestDTO(
        url="https://spansh.co.uk/api/station/128017152",
        method="GET",
        headers=common_headers,
        timeout=15.0,
    )
    sta_resp = transport.send(sta_req)
    assert sta_resp.status_code == 200, f"Expected 200, got {sta_resp.status_code}"
    print(f"      -> HTTP {sta_resp.status_code} received ({len(sta_resp.body)} bytes).")

    sta_payload: dict[str, Any] = json.loads(sta_resp.body.decode("utf-8"))
    sta_record = sta_payload.get("record", {})
    assert "Gorbachev" in sta_record.get("name", ""), f"Expected Gorbachev station, got {sta_record.get('name')}"

    sta_val = schema_engine.validate_call(key=station_key, headers=common_headers, payload=sta_record)
    assert sta_val.is_valid, f"Station payload validation failed: {sta_val.payload_errors}"
    print(f"      -> Station record ({sta_record['name']}, MarketId: {sta_record['market_id']}) validated against Draft 2020-12 schema.")

    sta_desc = schema_engine.resolve_descriptor(station_key)
    assert sta_desc is not None and sta_desc.model_cls is SpanshSpanshSearchStationDTO
    print("      -> Successfully verified DTO parity for SpanshSpanshSearchStationDTO.")

    # 4. Test Asynchronous 2-Phase Neutron Route Plotter
    print("\n[4/4] Testing Asynchronous 2-Phase Neutron Route Pipeline (Sol -> Colonia)...")
    route_req = HttpRequestDTO(
        url="https://spansh.co.uk/api/route?efficiency=60&range=65&from=Sol&to=Colonia",
        method="GET",
        headers=common_headers,
        timeout=15.0,
    )
    route_resp = transport.send(route_req)
    assert route_resp.status_code in [200, 202], f"Expected 200/202, got {route_resp.status_code}"

    route_init = json.loads(route_resp.body.decode("utf-8"))
    job_id = route_init.get("job")
    assert job_id, "Expected job UUID in initial response"
    print(f"      -> Job enqueued successfully. Job ID: {job_id}")

    # Poll /api/results/{job_id} until completed
    max_retries = 10
    poll_success = False
    for attempt in range(1, max_retries + 1):
        time.sleep(1.5)
        poll_req = HttpRequestDTO(
            url=f"https://spansh.co.uk/api/results/{job_id}",
            method="GET",
            headers=common_headers,
            timeout=15.0,
        )
        poll_resp = transport.send(poll_req)
        if poll_resp.status_code == 200:
            job_data = json.loads(poll_resp.body.decode("utf-8"))
            status = job_data.get("status")
            if status == "ok":
                result = job_data.get("result", {})
                jumps = result.get("system_jumps", [])
                print(f"      -> Job completed! (Attempt {attempt}): Calculated {len(jumps)} waypoints across {result.get('distance')} ly.")
                poll_success = True
                break
            else:
                print(f"      -> Polling attempt {attempt}: status='{status}'...")

    assert poll_success, "Failed to retrieve route results within timeout window."

    print("\n" + "=" * 75)
    print("ALL SPANSH SCHEMAS AND ASYNC ROUTING PIPELINES VERIFIED SUCCESSFULLY!")
    print("=" * 75)


if __name__ == "__main__":
    test_spansh_pipeline()
