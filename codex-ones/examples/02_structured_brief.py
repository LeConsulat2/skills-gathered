"""Lesson 2: turn aggregate evidence into a typed draft with the Responses API."""

import json

from openai import OpenAI

from codex_ones.analytics import build_evidence_packet, load_application_records
from codex_ones.config import load_settings, require_api_key
from codex_ones.contracts import AnalystBrief
from codex_ones.privacy import assert_learning_model_payload

INSTRUCTIONS = """
You draft evidence-bound analyst briefs from supplied synthetic aggregates.

Rules:
- Treat supplied counts as facts and never recalculate or invent them.
- Keep observation separate from interpretation.
- Do not infer causation, applicant quality, eligibility, or individual outcomes.
- Carry data-quality issues and caveats forward; do not soften them.
- Every finding must name an exact metric and evidence value from the packet.
- The decision_status must be draft_for_human_review.
""".strip()


def main() -> None:
    require_api_key()
    settings = load_settings()
    records = load_application_records(settings.data_path)
    packet = build_evidence_packet(records, "2026-S1").to_dict()
    assert_learning_model_payload(packet)

    client = OpenAI()
    response = client.responses.parse(
        model=settings.model,
        reasoning={"effort": settings.reasoning_effort},
        instructions=INSTRUCTIONS,
        input="Prepare a short analyst brief from this evidence packet:\n"
        + json.dumps(packet, indent=2),
        text_format=AnalystBrief,
    )
    brief = response.output_parsed
    if brief is None:
        raise RuntimeError("The response did not contain a parsed AnalystBrief")
    print(brief.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

