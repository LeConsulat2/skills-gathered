"""Lesson 1: calculate facts and surface exceptions without an LLM."""

from codex_ones.analytics import (
    available_periods,
    build_evidence_packet,
    load_application_records,
    render_evidence_markdown,
)
from codex_ones.config import load_settings


def main() -> None:
    settings = load_settings()
    records = load_application_records(
        settings.data_path,
        require_synthetic=settings.synthetic_only,
    )
    print(f"Available periods: {', '.join(available_periods(records))}\n")
    packet = build_evidence_packet(records, "2026-S1")
    print(render_evidence_markdown(packet))


if __name__ == "__main__":
    main()

