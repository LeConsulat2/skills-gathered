"""An MCP v2 server that exposes only deterministic, read-only evidence."""

from __future__ import annotations

import argparse
import logging
import os
from typing import Any

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from codex_ones.analytics import (
    available_periods,
    build_evidence_packet,
    compare_periods,
    load_application_records,
)
from codex_ones.config import load_settings

logger = logging.getLogger(__name__)
mcp = MCPServer(
    "synthetic-university-insights",
    instructions=(
        "Read-only synthetic aggregate evidence for learning. "
        "Never represent the data as real institutional information."
    ),
)


def _records():
    settings = load_settings()
    return load_application_records(
        settings.data_path,
        require_synthetic=settings.synthetic_only,
    )


@mcp.tool()
def list_reporting_periods() -> list[str]:
    """List reporting periods available in the synthetic evidence source."""

    return available_periods(_records())


@mcp.tool()
def get_application_snapshot(reporting_period: str) -> dict[str, Any]:
    """Get deduplicated counts, provenance, freshness, caveats, and exceptions for one period."""

    return build_evidence_packet(_records(), reporting_period).to_dict()


@mcp.tool()
def get_data_quality(reporting_period: str) -> dict[str, Any]:
    """Get only data-quality exceptions and the counting scope for one synthetic period."""

    packet = build_evidence_packet(_records(), reporting_period)
    return {
        "classification": packet.classification,
        "synthetic": packet.synthetic,
        "reporting_period": packet.reporting_period,
        "raw_row_count": packet.raw_row_count,
        "unique_application_count": packet.unique_application_count,
        "data_as_of": packet.data_as_of,
        "quality_issues": [
            {
                "code": issue.code,
                "severity": issue.severity,
                "count": issue.count,
                "detail": issue.detail,
            }
            for issue in packet.quality_issues
        ],
    }


@mcp.tool()
def compare_application_periods(first_period: str, second_period: str) -> dict[str, Any]:
    """Compare two synthetic periods descriptively without inferring a cause."""

    records = _records()
    first = build_evidence_packet(records, first_period)
    second = build_evidence_packet(records, second_period)
    return compare_periods(first, second)


@mcp.resource("methodology://application-metrics")
def application_metric_methodology() -> str:
    """Explain the scope and limitations of this synthetic metric service."""

    return """# Synthetic application metric methodology

- One unique application ID contributes one current-state row to headline counts.
- Duplicate IDs remain visible as quality exceptions and are excluded from counts.
- Unknown statuses remain separate; the server never guesses a mapping.
- Comparisons are descriptive and never establish causation.
- This server contains invented learning data and exposes no applicant decision capability.
"""


def _split_env_list(name: str, fallback: list[str]) -> list[str]:
    raw = os.getenv(name, "")
    values = [value.strip() for value in raw.split(",") if value.strip()]
    return values or fallback


def _http_security() -> TransportSecuritySettings:
    allowed_hosts = _split_env_list(
        "MCP_ALLOWED_HOSTS",
        ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*", "[::1]", "[::1]:*"],
    )
    allowed_origins = _split_env_list("MCP_ALLOWED_ORIGINS", [])
    return TransportSecuritySettings(
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("stdio", "http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    args = build_parser().parse_args()
    if args.transport == "stdio":
        logger.info("Starting read-only MCP server over stdio")
        mcp.run()
        return

    logger.info("Starting read-only MCP server at %s:%s/mcp", args.host, args.port)
    mcp.run(
        transport="streamable-http",
        host=args.host,
        port=args.port,
        stateless_http=True,
        json_response=True,
        transport_security=_http_security(),
    )


if __name__ == "__main__":
    main()

