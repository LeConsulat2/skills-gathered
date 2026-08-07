"""Lesson 3: one bounded agent with one read-only deterministic tool."""

import os
from typing import Any

os.environ.setdefault("OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA", "0")

from agents import Agent, Runner, function_tool  # noqa: E402

from codex_ones.analytics import build_evidence_packet, load_application_records  # noqa: E402
from codex_ones.config import load_settings, require_api_key  # noqa: E402
from codex_ones.contracts import AnalystBrief  # noqa: E402

SETTINGS = load_settings()


@function_tool
def get_application_evidence(reporting_period: str) -> dict[str, Any]:
    """Return synthetic aggregate application evidence and quality exceptions for one period."""

    records = load_application_records(
        SETTINGS.data_path,
        require_synthetic=SETTINGS.synthetic_only,
    )
    return build_evidence_packet(records, reporting_period).to_dict()


def main() -> None:
    require_api_key()
    agent = Agent(
        name="Synthetic application evidence analyst",
        model=SETTINGS.model,
        instructions=(
            "Use get_application_evidence before answering. Report only supplied evidence. "
            "Separate measured observations from cautious interpretation. Carry every caveat "
            "and quality issue forward. Never assess applicants or make admission decisions. "
            "Return a draft_for_human_review."
        ),
        tools=[get_application_evidence],
        output_type=AnalystBrief,
    )
    result = Runner.run_sync(
        agent,
        "Prepare an analyst brief for reporting period 2026-S1.",
        max_turns=4,
    )
    print(result.final_output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

