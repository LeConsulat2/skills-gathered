"""Provider-independent deterministic eval cases."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .analytics import EvidencePacket, metric_value
from .privacy import DataBoundaryError, assert_learning_model_payload


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    passed: bool
    observed: Any
    expected: Any
    note: str


def load_eval_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            case = json.loads(line)
            if "id" not in case or "kind" not in case:
                raise ValueError(f"Invalid eval case on line {line_number}")
            cases.append(case)
    return cases


def evaluate_case(
    case: dict[str, Any],
    packets: dict[str, EvidencePacket],
) -> EvalResult:
    kind = case["kind"]
    expected = case["expected"]

    if kind == "metric_equals":
        packet = packets[case["period"]]
        observed = metric_value(packet, case["metric"])
    elif kind == "quality_issue_present":
        packet = packets[case["period"]]
        observed = any(issue.code == case["code"] for issue in packet.quality_issues)
    elif kind == "model_boundary":
        try:
            assert_learning_model_payload(case["payload"])
            observed = True
        except DataBoundaryError:
            observed = False
    else:
        raise ValueError(f"Unsupported eval kind: {kind}")

    return EvalResult(
        case_id=case["id"],
        passed=observed == expected,
        observed=observed,
        expected=expected,
        note=case.get("note", ""),
    )


def run_eval_cases(
    cases: Iterable[dict[str, Any]],
    packets: dict[str, EvidencePacket],
) -> list[EvalResult]:
    return [evaluate_case(case, packets) for case in cases]

