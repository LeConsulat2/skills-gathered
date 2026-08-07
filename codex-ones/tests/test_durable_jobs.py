from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codex_ones.durable_jobs import JobStore


class DurableJobTests(unittest.TestCase):
    def test_job_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JobStore(Path(directory) / "jobs.sqlite")
            queued = store.enqueue("draft_report", "evidence://2026-S1")
            self.assertEqual(queued.status, "queued")

            running = store.claim_next("worker-test")
            self.assertIsNotNone(running)
            assert running is not None
            self.assertEqual(running.job_id, queued.job_id)
            self.assertEqual(running.status, "running")
            self.assertEqual(running.attempts, 1)

            finished = store.succeed(running.job_id, "output://synthetic-report")
            self.assertEqual(finished.status, "succeeded")
            self.assertEqual(finished.result_ref, "output://synthetic-report")

            with self.assertRaisesRegex(ValueError, "Only a running job"):
                store.succeed(running.job_id, "output://second-result")

    def test_empty_queue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = JobStore(Path(directory) / "jobs.sqlite")
            self.assertIsNone(store.claim_next("worker-test"))


if __name__ == "__main__":
    unittest.main()

