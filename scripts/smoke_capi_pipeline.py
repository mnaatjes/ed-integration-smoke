import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

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


@dataclass(frozen=True)
class CapiProfileDTO:
    commander_id: int
    commander_name: str
    credits: int


def run_pipeline() -> None:
    print("[1/4] Initializing SchemaEngine and TransportClient...")
    schema_engine = create_schema_engine()
    transport = create_transport_client()
    assert transport is not None

    with TemporaryDirectory() as tmp_dir:
        schema_path = Path(tmp_dir) / "profile.json"
        schema_path.write_text(
            json.dumps(
                {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "title": "CapiProfile",
                    "type": "object",
                    "properties": {
                        "commander_id": {"type": "integer"},
                        "commander_name": {"type": "string"},
                        "credits": {"type": "integer"},
                    },
                }
            ),
            encoding="utf-8",
        )

        print("[2/4] Registering CAPI Profile Manifest Contract...")

        class CapiManifest:
            name = "capi"
            schema_dir = Path(tmp_dir)
            endpoints = (
                EndpointContract(
                    route="/profile",
                    schema_file="profile.json",
                    model_cls=CapiProfileDTO,
                    header_contract=HeaderContract(
                        parameters=(
                            HeaderParameterContract(
                                name="Authorization",
                                required=True,
                                regex_pattern=r"^Bearer\s+[A-Za-z0-9_\-\.]+$",
                            ),
                        )
                    ),
                ),
            )

        schema_engine.load_manifests([CapiManifest])

        print("[3/4] Validating Outbound Request Headers...")
        outbound_headers = {"Authorization": "Bearer sample_mock_access_token_123"}
        key = SchemaKey(namespace="capi", endpoint="/profile")
        validation_res = schema_engine.validate_call(key=key, headers=outbound_headers)
        assert validation_res.is_valid, f"Validation failed: {validation_res.errors}"
        print("      Outbound headers verified contract compliant.")

        print("[4/4] Constructing Transport Request and Simulating Pipeline...")
        request = HttpRequestDTO(
            url="https://companion.orbis.frontier.co.uk/profile",
            method="GET",
            headers=outbound_headers,
            timeout=10.0,
        )
        assert request.headers["Authorization"].startswith("Bearer ")

        # Inbound response mock
        mock_response_payload: dict[str, Any] = {
            "commander_id": 987654,
            "commander_name": "Commander Jameson",
            "credits": 42000000,
        }

        # Model resolution and instantiation via bound model_cls
        descriptor = schema_engine.resolve_descriptor(key)
        assert descriptor is not None
        assert descriptor.model_cls is CapiProfileDTO

        dto: CapiProfileDTO = descriptor.model_cls(**mock_response_payload)
        print(f"      Hydrated DTO: {dto}")
        print("\nSmoke pipeline executed successfully.")


if __name__ == "__main__":
    run_pipeline()
