"""Lesson 6: pause, persist, approve or reject, and resume a consequential tool call."""

import asyncio
import json
import os
import re

os.environ.setdefault("OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA", "0")

from agents import Agent, Runner, RunState, function_tool  # noqa: E402

from codex_ones.analytics import (  # noqa: E402
    build_evidence_packet,
    load_application_records,
    render_evidence_markdown,
)
from codex_ones.config import PROJECT_ROOT, load_settings, require_api_key  # noqa: E402

SETTINGS = load_settings()
STATE_PATH = PROJECT_ROOT / ".runtime" / "pending-publication.json"
SAFE_REPORT_ID = re.compile(r"^synthetic-[a-z0-9-]{1,50}$")


@function_tool(needs_approval=True)
async def publish_synthetic_report(
    report_id: str,
    classification: str,
    markdown_body: str,
) -> str:
    """Publish an approved PUBLIC_SYNTHETIC report to the local outputs directory."""

    if classification != "PUBLIC_SYNTHETIC":
        raise ValueError("Only PUBLIC_SYNTHETIC reports are allowed in this lesson")
    if not SAFE_REPORT_ID.fullmatch(report_id):
        raise ValueError("report_id must start with synthetic- and contain safe characters")
    output_path = (PROJECT_ROOT / "outputs" / f"{report_id}.md").resolve()
    if output_path.parent != (PROJECT_ROOT / "outputs").resolve():
        raise ValueError("Output path escaped the allowed directory")
    output_path.write_text(markdown_body, encoding="utf-8")
    return f"Published approved synthetic report to {output_path}"


def ask_approval(name: str, arguments: str | None) -> bool:
    print(f"\nRequested tool: {name}\nArguments:\n{arguments}\n")
    answer = input("Publish exactly this synthetic draft? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


async def async_main() -> None:
    require_api_key()
    records = load_application_records(SETTINGS.data_path)
    packet = build_evidence_packet(records, "2026-S1")
    deterministic_draft = render_evidence_markdown(packet)

    agent = Agent(
        name="Controlled report publisher",
        model=SETTINGS.model,
        instructions=(
            "Request publish_synthetic_report exactly once using report_id synthetic-s1-evidence, "
            "classification PUBLIC_SYNTHETIC, and the supplied markdown unchanged. "
            "A tool request is not approval; wait for the runtime."
        ),
        tools=[publish_synthetic_report],
    )
    result = await Runner.run(
        agent,
        "Request publication of this synthetic draft:\n\n" + deterministic_draft,
        max_turns=4,
    )

    while result.interruptions:
        state = result.to_state()
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(state.to_string(), encoding="utf-8")

        stored = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        state = await RunState.from_json(agent, stored)
        for interruption in result.interruptions:
            if ask_approval(interruption.name or "unknown_tool", interruption.arguments):
                state.approve(interruption)
            else:
                state.reject(
                    interruption,
                    rejection_message="Publication was cancelled by the human reviewer.",
                )
        result = await Runner.run(agent, state)

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(async_main())

