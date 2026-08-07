"""Verify that the Agents SDK MCP client can discover the separate v2 server."""

from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path

from agents.mcp import MCPServerStdio

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TOOLS = {
    "list_reporting_periods",
    "get_application_snapshot",
    "get_data_quality",
    "compare_application_periods",
}


def server_params() -> dict[str, object]:
    server_python = os.getenv("MCP_SERVER_PYTHON", "").strip()
    if server_python:
        return {
            "command": server_python,
            "args": ["-m", "university_insights_mcp.server", "--transport", "stdio"],
        }

    uv = shutil.which("uv")
    if uv:
        return {
            "command": uv,
            "args": [
                "run",
                "--isolated",
                "--project",
                str(ROOT / "mcp-server"),
                "python",
                "-m",
                "university_insights_mcp.server",
                "--transport",
                "stdio",
            ],
        }
    raise SystemExit("Set MCP_SERVER_PYTHON or install uv before running this bridge check")


async def async_main() -> None:
    async with MCPServerStdio(
        params=server_params(),
        name="MCP v1-client to v2-server bridge check",
        client_session_timeout_seconds=60,
        require_approval="never",
    ) as server:
        tools = await server.list_tools()
    discovered = {tool.name for tool in tools}
    missing = EXPECTED_TOOLS - discovered
    if missing:
        raise SystemExit(f"FAIL: MCP bridge did not discover tools: {sorted(missing)}")
    print(f"PASS: MCP bridge discovered {', '.join(sorted(discovered))}")


if __name__ == "__main__":
    asyncio.run(async_main())
