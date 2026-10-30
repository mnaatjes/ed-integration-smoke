"""Pytest configuration and shared fixtures for ed-integration-smoke."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from tests.fixtures.mock_eddn_gateway import MockEddnGateway


@pytest.fixture
def mock_eddn_gateway() -> Generator[MockEddnGateway, None, None]:
    """Provides a synthetic EDDN Gateway test double running on localhost."""
    gateway = MockEddnGateway()
    try:
        yield gateway
    finally:
        gateway.close()
