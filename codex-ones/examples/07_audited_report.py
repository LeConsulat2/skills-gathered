"""Lesson 7: write an evidence artifact and a payload-minimising audit event."""

from codex_ones.analytics import (
    build_evidence_packet,
    load_application_records,
    render_evidence_markdown,
)
from codex_ones.audit import append_audit_event, stable_digest
from codex_ones.config import PROJECT_ROOT, load_settings


def main() -> None:
    settings = load_settings()
    records = load_application_records(settings.data_path)
    packet = build_evidence_packet(records, "2026-S1")

    artifact_id = "synthetic-s1-evidence"
    report_path = PROJECT_ROOT / "outputs" / f"{artifact_id}.md"
    report_path.write_text(render_evidence_markdown(packet), encoding="utf-8")

    event = append_audit_event(
        PROJECT_ROOT / ".runtime" / "audit.jsonl",
        "report_drafted",
        {
            "actor": "local-learning-example",
            "action": "draft",
            "artifact_id": artifact_id,
            "classification": packet.classification,
            "evidence_digest": stable_digest(packet.to_dict()),
            "outcome": "draft_for_human_review",
            "reporting_period": packet.reporting_period,
        },
    )
    print(f"Draft: {report_path}")
    print(f"Audit event (no report body): {event}")


if __name__ == "__main__":
    main()

