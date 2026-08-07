from __future__ import annotations

import unittest

from codex_ones.analytics import (
    available_periods,
    build_evidence_packet,
    compare_periods,
    load_application_records,
    metric_value,
)
from codex_ones.config import DEFAULT_DATA_PATH


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = load_application_records(DEFAULT_DATA_PATH)
        cls.s1 = build_evidence_packet(cls.records, "2026-S1")
        cls.s2 = build_evidence_packet(cls.records, "2026-S2")

    def test_periods(self) -> None:
        self.assertEqual(available_periods(self.records), ["2026-S1", "2026-S2"])

    def test_duplicate_is_visible_but_not_counted(self) -> None:
        self.assertEqual(self.s1.raw_row_count, 14)
        self.assertEqual(self.s1.unique_application_count, 13)
        self.assertEqual(metric_value(self.s1, "status:Offered"), 3)
        self.assertEqual(metric_value(self.s1, "quality:duplicate_application_id"), 1)

    def test_unknown_values_are_not_coerced(self) -> None:
        self.assertEqual(self.s1.counts_by_status["Needs review"], 1)
        codes = {issue.code for issue in self.s1.quality_issues}
        self.assertIn("unknown_application_status", codes)

    def test_date_and_freshness_issues(self) -> None:
        codes = {issue.code for issue in self.s2.quality_issues}
        self.assertIn("invalid_date_sequence", codes)
        self.assertIn("mixed_freshness", codes)

    def test_comparison_is_descriptive(self) -> None:
        comparison = compare_periods(self.s1, self.s2)
        self.assertEqual(comparison["unique_application_delta"], -3)
        self.assertIn("does not explain causation", comparison["warning"])

    def test_unknown_period_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown reporting period"):
            build_evidence_packet(self.records, "not-a-period")


if __name__ == "__main__":
    unittest.main()

