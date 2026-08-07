"""Configuration with conservative learning defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PACKAGE_ROOT / "sample_data" / "applications.csv"
ALLOWED_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(PROJECT_ROOT / ".env")


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    model: str
    reasoning_effort: str
    data_path: Path
    synthetic_only: bool


def load_settings() -> Settings:
    _load_dotenv_if_available()
    effort = os.getenv("OPENAI_REASONING_EFFORT", "medium").strip().lower()
    if effort not in ALLOWED_REASONING_EFFORTS:
        allowed = ", ".join(sorted(ALLOWED_REASONING_EFFORTS))
        raise ValueError(f"OPENAI_REASONING_EFFORT must be one of: {allowed}")

    data_path = Path(os.getenv("CODEX_ONES_DATA_PATH", str(DEFAULT_DATA_PATH))).expanduser()
    return Settings(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-terra").strip(),
        reasoning_effort=effort,
        data_path=data_path.resolve(),
        synthetic_only=_env_flag("CODEX_ONES_SYNTHETIC_ONLY", True),
    )


def require_api_key() -> None:
    _load_dotenv_if_available()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add a key, "
            "or run one of the offline lessons."
        )
