"""Lesson 4: own the Responses API function-calling loop."""

from typing import Any

from openai import OpenAI

from codex_ones.analytics import build_evidence_packet, load_application_records
from codex_ones.config import load_settings, require_api_key
from codex_ones.responses_loop import run_responses_tool_loop

TOOL = {
    "type": "function",
    "name": "get_application_evidence",
    "description": "Get synthetic aggregate evidence and quality issues for one reporting period.",
    "parameters": {
        "type": "object",
        "properties": {
            "reporting_period": {
                "type": "string",
                "enum": ["2026-S1", "2026-S2"],
                "description": "The reporting period to inspect.",
            }
        },
        "required": ["reporting_period"],
        "additionalProperties": False,
    },
    "strict": True,
}


def main() -> None:
    require_api_key()
    settings = load_settings()
    records = load_application_records(settings.data_path)

    def handle_evidence(arguments: dict[str, Any]) -> dict[str, Any]:
        return build_evidence_packet(records, arguments["reporting_period"]).to_dict()

    response = run_responses_tool_loop(
        OpenAI(),
        model=settings.model,
        instructions=(
            "Use the evidence tool. Lead with the unique application count, then status counts, "
            "quality exceptions, freshness, and caveats. Do not infer causation or make decisions."
        ),
        user_input="Explain the synthetic application picture for 2026-S2.",
        tools=[TOOL],
        handlers={"get_application_evidence": handle_evidence},
        max_turns=4,
        max_tool_calls=3,
    )
    print(response.output_text)


if __name__ == "__main__":
    main()

