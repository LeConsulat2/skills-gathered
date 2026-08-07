"""Lesson 8: durable local job state, independent of a browser or model request."""

from codex_ones.analytics import (
    build_evidence_packet,
    load_application_records,
    render_evidence_markdown,
)
from codex_ones.config import PROJECT_ROOT, load_settings
from codex_ones.durable_jobs import JobStore


def main() -> None:
    store = JobStore(PROJECT_ROOT / ".runtime" / "jobs.sqlite")
    queued = store.enqueue("build_evidence_report", "evidence://applications/2026-S2")
    print(f"Queued {queued.job_id}: {queued.status}")

    job = store.claim_next("local-worker-1")
    if job is None:
        raise RuntimeError("No job was available to claim")
    print(f"Claimed {job.job_id}: {job.status}, attempt {job.attempts}")

    try:
        settings = load_settings()
        records = load_application_records(settings.data_path)
        packet = build_evidence_packet(records, "2026-S2")
        output_path = PROJECT_ROOT / "outputs" / f"{job.job_id}.md"
        output_path.write_text(render_evidence_markdown(packet), encoding="utf-8")
        finished = store.succeed(job.job_id, f"file://{output_path}")
    except Exception:
        store.fail(job.job_id, "report_generation_failed")
        raise

    print(f"Finished {finished.job_id}: {finished.status}")
    print(f"Result reference: {finished.result_ref}")


if __name__ == "__main__":
    main()

