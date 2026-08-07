"""Payload-minimising audit events for local demonstrations."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_DETAIL_KEYS = {
    "actor",
    "action",
    "artifact_id",
    "classification",
    "evidence_digest",
    "outcome",
    "reporting_period",
}


def stable_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append_audit_event(path: Path, event_type: str, details: Mapping[str, Any]) -> dict[str, Any]:
    disallowed = set(details) - ALLOWED_DETAIL_KEYS
    if disallowed:
        raise ValueError(
            "Audit details contain non-allowlisted keys: "
            f"{sorted(disallowed)}. Store references or digests, not payloads."
        )
    event = {
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "details": dict(details),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event

