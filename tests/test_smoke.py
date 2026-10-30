import json
from dataclasses import dataclass
from pathlib import Path

from ed_schema import (
    EndpointContract,
    HeaderContract,
    HeaderParameterContract,
    SchemaKey,
    create_schema_engine,
)
from ed_transport import HttpRequestDTO, create_transport_client


@dataclass(frozen=True)
class MockShipDTO:
    ship_id: int
    ship_type: str


def test_schema_and_transport_interoperability(tmp_path: Path) -> None:
    schema_engine = create_schema_engine()
    transport = create_transport_client()

    schema_file = tmp_path / "shipyard.json"
    schema_file.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": "Shipyard",
                "type": "object",
                "properties": {
                    "ship_id": {"type": "integer"},
                    "ship_type": {"type": "string"},
                },
            }
        ),
        encoding="utf-8",
    )

    class CapiManifest:
        name = "capi"
        schema_dir = tmp_path
        endpoints = (
            EndpointContract(
                route="/shipyard",
                schema_file="shipyard.json",
                model_cls=MockShipDTO,
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

    headers = {"Authorization": "Bearer token_xyz_123"}
    key = SchemaKey(namespace="capi", endpoint="/shipyard")
    validation = schema_engine.validate_call(key=key, headers=headers)
    assert validation.is_valid

    req = HttpRequestDTO(
        url="https://companion.orbis.frontier.co.uk/shipyard",
        method="GET",
        headers=headers,
        timeout=10.0,
    )
    assert req.method == "GET"
    assert transport is not None

    descriptor = schema_engine.resolve_descriptor(key)
    assert descriptor is not None
    assert descriptor.model_cls is MockShipDTO

    dto = descriptor.model_cls(ship_id=1, ship_type="Anaconda")
    assert dto.ship_type == "Anaconda"
