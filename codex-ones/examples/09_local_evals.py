"""Lesson 9: execute domain invariants without a model or cloud eval service."""

from codex_ones.analytics import available_periods, build_evidence_packet, load_application_records
from codex_ones.config import PROJECT_ROOT, load_settings
from codex_ones.evals import load_eval_cases, run_eval_cases


def main() -> None:
    settings = load_settings()
    records = load_application_records(settings.data_path)
    packets = {
        period: build_evidence_packet(records, period)
        for period in available_periods(records)
    }
    cases = load_eval_cases(PROJECT_ROOT / "data" / "eval_cases.jsonl")
    results = run_eval_cases(cases, packets)

    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        print(
            f"{mark:4} {result.case_id}: observed={result.observed!r} "
            f"expected={result.expected!r}"
        )

    failures = [result for result in results if not result.passed]
    print(f"\n{len(results) - len(failures)}/{len(results)} cases passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

