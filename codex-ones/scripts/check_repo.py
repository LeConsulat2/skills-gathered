"""Run the offline release gate with only the Python standard library."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    ROOT / "00-START-HERE.md",
    ROOT / "src" / "codex_ones" / "analytics.py",
    ROOT / "src" / "codex_ones" / "sample_data" / "applications.csv",
    ROOT / "data" / "eval_cases.jsonl",
    ROOT / "mcp-server" / "src" / "university_insights_mcp" / "server.py",
]
IGNORED_TREE_NAMES = {".git", ".pytest_cache", ".ruff_cache", ".uv-cache", ".venv", ".venv-mcp"}


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def run_command(arguments: list[str], env: dict[str, str]) -> None:
    print(f"RUN: {' '.join(arguments)}", flush=True)
    completed = subprocess.run(arguments, cwd=ROOT, env=env, check=False)
    if completed.returncode != 0:
        fail(f"Command exited with {completed.returncode}")


def validate_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        fail(f"Missing required paths: {missing}")
    if (ROOT / ".env").exists():
        fail("A real .env file is present in the repository root")


def validate_synthetic_rows() -> None:
    path = ROOT / "src" / "codex_ones" / "sample_data" / "applications.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        fail("Synthetic application fixture is empty")
    non_synthetic = [
        row.get("application_id", "<unknown>")
        for row in rows
        if row.get("is_synthetic") != "true"
    ]
    if non_synthetic:
        fail(f"Rows are not explicitly synthetic: {non_synthetic}")


def validate_json() -> None:
    json.loads((ROOT / "templates" / "EVAL-CASE.json").read_text(encoding="utf-8"))
    json.loads((ROOT / "templates" / "EVIDENCE-PACKET.json").read_text(encoding="utf-8"))
    with (ROOT / "data" / "eval_cases.jsonl").open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"Invalid eval JSON on line {line_number}: {exc}")


def validate_skills() -> None:
    skill_root = ROOT / ".agents" / "skills"
    skills = sorted(skill_root.glob("*/SKILL.md"))
    if not skills:
        fail("No Codex skills found")
    for path in skills:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) < 5 or lines[0] != "---" or "---" not in lines[1:]:
            fail(f"Invalid frontmatter delimiters: {path}")
        closing = lines[1:].index("---") + 1
        frontmatter = lines[1:closing]
        name_lines = [line for line in frontmatter if line.startswith("name: ")]
        description_lines = [line for line in frontmatter if line.startswith("description: ")]
        if name_lines != [f"name: {path.parent.name}"] or len(description_lines) != 1:
            fail(f"Invalid skill name or description: {path}")
        if "TODO" in text or "[TODO" in text:
            fail(f"Placeholder remains in skill: {path}")

        interface_path = path.parent / "agents" / "openai.yaml"
        interface = interface_path.read_text(encoding="utf-8")
        if f"${path.parent.name}" not in interface:
            fail(f"Skill default prompt does not mention its skill: {interface_path}")


def validate_local_markdown_links() -> None:
    pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in ROOT.rglob("*.md"):
        if any(part in IGNORED_TREE_NAMES for part in path.relative_to(ROOT).parts):
            continue
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            target = target.strip().strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                fail(f"Broken local link in {path.relative_to(ROOT)}: {target}")


def main() -> None:
    validate_files()
    validate_synthetic_rows()
    validate_json()
    validate_skills()
    validate_local_markdown_links()

    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    run_command(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "src",
            "examples",
            "tests",
            "mcp-server/src",
            "mcp-server/tests",
        ],
        env,
    )
    run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], env)
    print("PASS: offline repository gate completed")


if __name__ == "__main__":
    main()
