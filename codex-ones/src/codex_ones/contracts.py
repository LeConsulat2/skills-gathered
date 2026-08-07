"""Strict model-boundary contracts for the API lessons."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceFinding(StrictModel):
    metric: str = Field(description="Metric name exactly as supplied in the evidence packet.")
    observation: str = Field(description="A concise statement of the measured result.")
    evidence_value: str = Field(description="The exact supplied value supporting the observation.")
    interpretation: str = Field(
        description="A cautious interpretation, clearly distinct from fact."
    )
    confidence: Literal["high", "medium", "low"]


class AnalystBrief(StrictModel):
    reporting_period: str
    headline: str
    findings: list[EvidenceFinding]
    caveats: list[str]
    recommended_checks: list[str]
    decision_status: Literal["draft_for_human_review"]


class ReviewReport(StrictModel):
    lens: Literal["data_quality", "domain_grounding", "decision_rights"]
    verdict: Literal["pass", "revise", "stop"]
    findings: list[str]
    evidence_gaps: list[str]
    required_actions: list[str]
