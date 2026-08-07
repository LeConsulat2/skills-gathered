from __future__ import annotations

import pytest
from mcp import Client
from university_insights_mcp.server import mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_snapshot_is_structured_and_synthetic() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_application_snapshot", {"reporting_period": "2026-S1"}
        )
    assert result.is_error is False
    payload = result.structured_content
    assert payload is not None
    assert payload["classification"] == "PUBLIC_SYNTHETIC"
    assert payload["unique_application_count"] == 13
    assert payload["raw_row_count"] == 14


@pytest.mark.anyio
async def test_invalid_period_is_a_tool_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_application_snapshot", {"reporting_period": "not-a-period"}
        )
    assert result.is_error is True
