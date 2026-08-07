"""Lesson 10: let an Agents SDK client use the read-only MCP capability."""

import asyncio
import os

os.environ.setdefault("OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA", "0")

from agents import Agent, Runner  # noqa: E402
from agents.mcp import (  # noqa: E402
    MCPServerStdio,
    MCPServerStreamableHttp,
    create_static_tool_filter,
)

from codex_ones.config import load_settings, require_api_key  # noqa: E402

TOOL_FILTER = create_static_tool_filter(
    allowed_tool_names=[
        "list_reporting_periods",
        "get_application_snapshot",
        "get_data_quality",
        "compare_application_periods",
    ]
)


async def async_main() -> None:
    require_api_key()
    settings = load_settings()
    server_url = os.getenv("MCP_SERVER_URL", "").strip()
    server_python = os.getenv("MCP_SERVER_PYTHON", "").strip()

    if server_url:
        server = MCPServerStreamableHttp(
            name="Synthetic university insights over HTTP",
            params={"url": server_url},
            tool_filter=TOOL_FILTER,
            use_structured_content=True,
            require_approval="never",
        )
    else:
        if not server_python:
            raise SystemExit(
                "Set MCP_SERVER_PYTHON to the Python executable in .venv-mcp, "
                "or set MCP_SERVER_URL to a running Streamable HTTP endpoint."
            )
        server = MCPServerStdio(
            name="Synthetic university insights over stdio",
            params={
                "command": server_python,
                "args": ["-m", "university_insights_mcp.server", "--transport", "stdio"],
            },
            tool_filter=TOOL_FILTER,
            use_structured_content=True,
            require_approval="never",
        )

    async with server:
        agent = Agent(
            name="MCP evidence analyst",
            model=settings.model,
            instructions=(
                "Use the MCP tools to compare 2026-S1 with 2026-S2. Report measured changes, "
                "quality exceptions, freshness, and caveats. Never infer causes or make applicant "
                "decisions. These tools are read-only, which is why tool approval is set to never."
            ),
            mcp_servers=[server],
        )
        result = await Runner.run(
            agent,
            "Prepare a concise comparison for human review.",
            max_turns=6,
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(async_main())
