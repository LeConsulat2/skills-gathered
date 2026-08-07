from __future__ import annotations

import unittest

from codex_ones.analytics import available_periods, build_evidence_packet, load_application_records
from codex_ones.config import DEFAULT_DATA_PATH, PROJECT_ROOT
from codex_ones.evals import load_eval_cases, run_eval_cases


class EvalHarnessTests(unittest.TestCase):
    def test_all_committed_cases_pass(self) -> None:
        records = load_application_records(DEFAULT_DATA_PATH)
        packets = {
            period: build_evidence_packet(records, period)
            for period in available_periods(records)
        }
        cases = load_eval_cases(PROJECT_ROOT / "data" / "eval_cases.jsonl")
        results = run_eval_cases(cases, packets)
        failures = [result for result in results if not result.passed]
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()

