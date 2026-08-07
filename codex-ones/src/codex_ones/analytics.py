"""Deterministic evidence calculations over a deliberately synthetic dataset."""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .privacy import Classification

KNOWN_STATUSES = {"Submitted", "Offered", "Accepted", "Declined", "Withdrawn"}
REQUIRED_COLUMNS = {
    "is_synthetic",
    "application_id",
    "reporting_period",
    "faculty",
    "study_level",
    "residency_group",
    "application_status",
    "submitted_at",
    "decision_at",
    "source_system",
    "data_as_of",
}


@dataclass(frozen=True)
class ApplicationRecord:
    is_synthetic: bool
    application_id: str
    reporting_period: str
    faculty: str
    study_level: str
    residency_group: str
    application_status: str
    submitted_at: str
    decision_at: str
    source_system: str
    data_as_of: str


@dataclass(frozen=True)
class QualityIssue:
    code: str
    severity: str
    count: int
    detail: str


@dataclass(frozen=True)
class EvidencePacket:
    reporting_period: str
    classification: str
    synthetic: bool
    source: str
    source_systems: list[str]
    data_as_of: list[str]
    raw_row_count: int
    unique_application_count: int
    counts_by_status: dict[str, int]
    counts_by_faculty: dict[str, int]
    quality_issues: list[QualityIssue]
    caveats: list[str]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["quality_issues"] = [asdict(issue) for issue in self.quality_issues]
        return result


def _parse_date(raw: str) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def load_application_records(
    path: Path,
    *,
    require_synthetic: bool = True,
) -> list[ApplicationRecord]:
    """Load CSV rows and fail closed if the learning boundary is violated."""

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

        records: list[ApplicationRecord] = []
        for row_number, row in enumerate(reader, start=2):
            synthetic = row["is_synthetic"].strip().lower() == "true"
            if require_synthetic and not synthetic:
                raise ValueError(
                    f"Row {row_number} is not declared synthetic. "
                    "Real records are outside this learning repository's boundary."
                )
            records.append(
                ApplicationRecord(
                    is_synthetic=synthetic,
                    application_id=row["application_id"].strip(),
                    reporting_period=row["reporting_period"].strip(),
                    faculty=row["faculty"].strip(),
                    study_level=row["study_level"].strip(),
                    residency_group=row["residency_group"].strip(),
                    application_status=row["application_status"].strip(),
                    submitted_at=row["submitted_at"].strip(),
                    decision_at=row["decision_at"].strip(),
                    source_system=row["source_system"].strip(),
                    data_as_of=row["data_as_of"].strip(),
                )
            )
    if not records:
        raise ValueError("Dataset contains no records")
    return records


def available_periods(records: Iterable[ApplicationRecord]) -> list[str]:
    return sorted({record.reporting_period for record in records})


def _deduplicate(
    records: list[ApplicationRecord],
) -> tuple[list[ApplicationRecord], list[str]]:
    first_by_id: dict[str, ApplicationRecord] = {}
    duplicates: list[str] = []
    for record in records:
        if record.application_id in first_by_id:
            duplicates.append(record.application_id)
            continue
        first_by_id[record.application_id] = record
    return list(first_by_id.values()), duplicates


def build_evidence_packet(
    records: Iterable[ApplicationRecord],
    reporting_period: str,
    *,
    source: str = "codex_ones/sample_data/applications.csv",
) -> EvidencePacket:
    period_rows = [record for record in records if record.reporting_period == reporting_period]
    if not period_rows:
        raise ValueError(f"Unknown reporting period: {reporting_period}")

    unique_rows, duplicate_ids = _deduplicate(period_rows)
    unknown_statuses = [
        record.application_status
        for record in unique_rows
        if record.application_status not in KNOWN_STATUSES
    ]
    invalid_dates = []
    for record in unique_rows:
        submitted = _parse_date(record.submitted_at)
        decided = _parse_date(record.decision_at)
        if submitted is None or (record.decision_at and decided is None):
            invalid_dates.append(record.application_id)
        elif decided is not None and decided < submitted:
            invalid_dates.append(record.application_id)

    as_of_values = sorted({record.data_as_of for record in unique_rows})
    issues: list[QualityIssue] = []
    if duplicate_ids:
        issues.append(
            QualityIssue(
                code="duplicate_application_id",
                severity="high",
                count=len(duplicate_ids),
                detail="Duplicate rows were excluded from metric counts.",
            )
        )
    if unknown_statuses:
        issues.append(
            QualityIssue(
                code="unknown_application_status",
                severity="medium",
                count=len(unknown_statuses),
                detail="Unknown statuses remain visible and require a definition owner.",
            )
        )
    if invalid_dates:
        issues.append(
            QualityIssue(
                code="invalid_date_sequence",
                severity="high",
                count=len(invalid_dates),
                detail="A date is invalid or a decision predates submission.",
            )
        )
    if len(as_of_values) > 1:
        issues.append(
            QualityIssue(
                code="mixed_freshness",
                severity="medium",
                count=len(as_of_values),
                detail="Rows have more than one data-as-of date.",
            )
        )

    caveats = [
        "Counts describe synthetic current-state rows, not people or offers accepted over time.",
        "Duplicate application IDs are retained as evidence but excluded from metric counts.",
        "Unknown statuses are not silently mapped into a known category.",
    ]
    return EvidencePacket(
        reporting_period=reporting_period,
        classification=Classification.PUBLIC_SYNTHETIC,
        synthetic=all(record.is_synthetic for record in period_rows),
        source=source,
        source_systems=sorted({record.source_system for record in unique_rows}),
        data_as_of=as_of_values,
        raw_row_count=len(period_rows),
        unique_application_count=len(unique_rows),
        counts_by_status=dict(sorted(Counter(r.application_status for r in unique_rows).items())),
        counts_by_faculty=dict(sorted(Counter(r.faculty for r in unique_rows).items())),
        quality_issues=issues,
        caveats=caveats,
    )


def compare_periods(first: EvidencePacket, second: EvidencePacket) -> dict[str, Any]:
    statuses = sorted(set(first.counts_by_status) | set(second.counts_by_status))
    return {
        "classification": Classification.PUBLIC_SYNTHETIC,
        "synthetic": first.synthetic and second.synthetic,
        "first_period": first.reporting_period,
        "second_period": second.reporting_period,
        "unique_application_delta": (
            second.unique_application_count - first.unique_application_count
        ),
        "status_deltas": {
            status: second.counts_by_status.get(status, 0)
            - first.counts_by_status.get(status, 0)
            for status in statuses
        },
        "warning": "A period delta is descriptive; it does not explain causation.",
    }


def quality_issue_count(packet: EvidencePacket, code: str) -> int:
    return next((issue.count for issue in packet.quality_issues if issue.code == code), 0)


def metric_value(packet: EvidencePacket, metric: str) -> int:
    if metric == "unique_application_count":
        return packet.unique_application_count
    if metric == "raw_row_count":
        return packet.raw_row_count
    if metric.startswith("status:"):
        return packet.counts_by_status.get(metric.removeprefix("status:"), 0)
    if metric.startswith("faculty:"):
        return packet.counts_by_faculty.get(metric.removeprefix("faculty:"), 0)
    if metric.startswith("quality:"):
        return quality_issue_count(packet, metric.removeprefix("quality:"))
    raise ValueError(f"Unsupported metric: {metric}")


def render_evidence_markdown(packet: EvidencePacket) -> str:
    statuses = "\n".join(
        f"- {status}: {count}" for status, count in packet.counts_by_status.items()
    )
    faculties = "\n".join(
        f"- {faculty}: {count}" for faculty, count in packet.counts_by_faculty.items()
    )
    issues = "\n".join(
        f"- [{issue.severity}] {issue.code}: {issue.count} — {issue.detail}"
        for issue in packet.quality_issues
    ) or "- None detected"
    caveats = "\n".join(f"- {caveat}" for caveat in packet.caveats)
    return f"""# Application evidence: {packet.reporting_period}

Classification: `{packet.classification}`  
Source: `{packet.source}`  
Data as of: {", ".join(packet.data_as_of)}

## Scope

- Raw rows: {packet.raw_row_count}
- Unique application IDs used for counts: {packet.unique_application_count}

## Status counts

{statuses}

## Faculty counts

{faculties}

## Data-quality exceptions

{issues}

## Caveats

{caveats}
"""
