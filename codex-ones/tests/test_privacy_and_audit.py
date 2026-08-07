from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codex_ones.audit import append_audit_event, stable_digest
from codex_ones.privacy import DataBoundaryError, assert_learning_model_payload


class PrivacyAndAuditTests(unittest.TestCase):
    def test_synthetic_aggregate_is_allowed(self) -> None:
        assert_learning_model_payload(
            {"classification": "PUBLIC_SYNTHETIC", "synthetic": True}
        )

    def test_restricted_payload_fails_closed(self) -> None:
        with self.assertRaises(DataBoundaryError):
            assert_learning_model_payload(
                {"classification": "RESTRICTED_ROW_LEVEL", "synthetic": False}
            )

    def test_audit_allowlist_rejects_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            with self.assertRaisesRegex(ValueError, "non-allowlisted"):
                append_audit_event(path, "drafted", {"raw_prompt": "do not store me"})

    def test_audit_writes_reference_and_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.jsonl"
            digest = stable_digest({"count": 13})
            append_audit_event(
                path,
                "report_drafted",
                {
                    "action": "draft",
                    "artifact_id": "synthetic-s1",
                    "classification": "PUBLIC_SYNTHETIC",
                    "evidence_digest": digest,
                    "outcome": "draft_for_human_review",
                    "reporting_period": "2026-S1",
                },
            )
            event = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(event["details"]["evidence_digest"], digest)
            self.assertNotIn("count", event["details"])


if __name__ == "__main__":
    unittest.main()

