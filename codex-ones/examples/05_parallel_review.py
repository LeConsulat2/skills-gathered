"""Lesson 5: parallel specialist review that preserves disagreement."""

import asyncio
import json
import os
from dataclasses import dataclass

os.environ.setdefault("OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA", "0")

from agents import Agent, Runner  # noqa: E402

from codex_ones.analytics import build_evidence_packet, load_application_records  # noqa: E402
from codex_ones.config import PROJECT_ROOT, load_settings, require_api_key  # noqa: E402
from codex_ones.contracts import ReviewReport  # noqa: E402
from codex_ones.privacy import assert_learning_model_payload  # noqa: E402


@dataclass(frozen=True)
class Lens:
    name: str
    instructions: str


LENSES = [
    Lens(
        "data_quality",
        "Check definitions, duplicates, freshness, missingness, and whether conclusions "
        "outrun data.",
    ),
    Lens(
        "domain_grounding",
        "Check whether language matches what an applications analyst can actually know and use.",
    ),
    Lens(
        "decision_rights",
        "Check privacy, human authority, approval boundaries, auditability, and harmful "
        "automation.",
    ),
]


async def run_lens(model: str, lens: Lens, evidence: str) -> ReviewReport:
    agent = Agent(
        name=f"{lens.name} reviewer",
        model=model,
        instructions=(
            f"You are the {lens.name} reviewer. {lens.instructions} "
            f"Set lens to {lens.name}. Be concrete. A stop verdict means the artifact should not "
            "enter a pilot until the stated issue is resolved. Do not rewrite another lens's "
            "concerns."
        ),
        output_type=ReviewReport,
    )
    result = await Runner.run(
        agent,
        "Review this frozen synthetic evidence packet:\n" + evidence,
        max_turns=3,
    )
    report = result.final_output
    if report.lens != lens.name:
        report = report.model_copy(update={"lens": lens.name})
    return report


async def async_main() -> None:
    require_api_key()
    settings = load_settings()
    records = load_application_records(settings.data_path)
    packet = build_evidence_packet(records, "2026-S2").to_dict()
    assert_learning_model_payload(packet)
    frozen_evidence = json.dumps(packet, sort_keys=True, indent=2)

    reports = await asyncio.gather(
        *(run_lens(settings.model, lens, frozen_evidence) for lens in LENSES)
    )
    ledger = {
        "evidence_period": packet["reporting_period"],
        "reconciliation_status": "human_review_required",
        "rule": "Findings remain separate; disagreement is not averaged away.",
        "reviews": [report.model_dump() for report in reports],
    }
    output_path = PROJECT_ROOT / "outputs" / "review-ledger.json"
    output_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(json.dumps(ledger, indent=2))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    asyncio.run(async_main())
