"""A small SQLite job state machine with references instead of raw payloads."""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

TERMINAL_STATUSES = {"succeeded", "failed", "cancelled"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Job:
    job_id: str
    kind: str
    input_ref: str
    status: str
    attempts: int
    worker_id: str | None
    result_ref: str | None
    error_code: str | None
    created_at: str
    updated_at: str
    started_at: str | None
    finished_at: str | None


class JobStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    input_ref TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')
                    ),
                    attempts INTEGER NOT NULL DEFAULT 0,
                    worker_id TEXT,
                    result_ref TEXT,
                    error_code TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                )
                """
            )

    @staticmethod
    def _row_to_job(row: sqlite3.Row) -> Job:
        return Job(**dict(row))

    def enqueue(self, kind: str, input_ref: str) -> Job:
        if not kind.strip() or not input_ref.strip():
            raise ValueError("kind and input_ref are required")
        job_id = str(uuid.uuid4())
        now = _now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    job_id, kind, input_ref, status, attempts, created_at, updated_at
                ) VALUES (?, ?, ?, 'queued', 0, ?, ?)
                """,
                (job_id, kind, input_ref, now, now),
            )
        return self.get(job_id)

    def get(self, job_id: str) -> Job:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        if row is None:
            raise KeyError(job_id)
        return self._row_to_job(row)

    def claim_next(self, worker_id: str) -> Job | None:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at LIMIT 1"
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            now = _now()
            changed = connection.execute(
                """
                UPDATE jobs
                SET status = 'running', attempts = attempts + 1, worker_id = ?,
                    started_at = ?, updated_at = ?
                WHERE job_id = ? AND status = 'queued'
                """,
                (worker_id, now, now, row["job_id"]),
            ).rowcount
            if changed != 1:
                connection.rollback()
                return None
            connection.commit()
            return self.get(row["job_id"])
        finally:
            connection.close()

    def succeed(self, job_id: str, result_ref: str) -> Job:
        return self._finish(job_id, "succeeded", result_ref=result_ref)

    def fail(self, job_id: str, error_code: str) -> Job:
        return self._finish(job_id, "failed", error_code=error_code)

    def _finish(
        self,
        job_id: str,
        status: str,
        *,
        result_ref: str | None = None,
        error_code: str | None = None,
    ) -> Job:
        if status not in TERMINAL_STATUSES:
            raise ValueError(f"Not a terminal status: {status}")
        now = _now()
        with self._connection() as connection:
            changed = connection.execute(
                """
                UPDATE jobs
                SET status = ?, result_ref = ?, error_code = ?, finished_at = ?, updated_at = ?
                WHERE job_id = ? AND status = 'running'
                """,
                (status, result_ref, error_code, now, now, job_id),
            ).rowcount
        if changed != 1:
            raise ValueError("Only a running job can enter a terminal state")
        return self.get(job_id)

    def reset_stale_running(self, older_than_seconds: int) -> int:
        if older_than_seconds <= 0:
            raise ValueError("older_than_seconds must be positive")
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=older_than_seconds)).isoformat()
        now = _now()
        with self._connection() as connection:
            return connection.execute(
                """
                UPDATE jobs
                SET status = 'queued', worker_id = NULL, started_at = NULL, updated_at = ?
                WHERE status = 'running' AND started_at < ?
                """,
                (now, cutoff),
            ).rowcount
