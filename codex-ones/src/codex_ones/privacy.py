"""Explicit trust-boundary checks; not a pretend PII detector."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any


class Classification(str, Enum):
    PUBLIC_SYNTHETIC = "PUBLIC_SYNTHETIC"
    INTERNAL_AGGREGATE = "INTERNAL_AGGREGATE"
    RESTRICTED_ROW_LEVEL = "RESTRICTED_ROW_LEVEL"


class DataBoundaryError(ValueError):
    """Raised when a payload crosses a boundary it was not approved to cross."""


def assert_learning_model_payload(payload: Mapping[str, Any]) -> None:
    """Fail closed: learning examples may send only declared synthetic aggregates."""

    classification = payload.get("classification")
    synthetic = payload.get("synthetic")
    if classification != Classification.PUBLIC_SYNTHETIC or synthetic is not True:
        raise DataBoundaryError(
            "This learning example sends only PUBLIC_SYNTHETIC aggregate evidence. "
            "Do not bypass this check for real university or client data."
        )
