# Codex Ones working agreement

This directory is a learning laboratory and a portable reference implementation.

## Non-negotiables

- Use only synthetic data in examples, tests, prompts, traces, screenshots, and committed outputs.
- Never turn an example into automated admission, enrolment, eligibility, counselling, or clinical decision-making. The software may assemble evidence and drafts; an authorised person decides.
- Keep deterministic calculation outside the model. Let models explain or review computed evidence, not invent counts.
- Separate read capabilities from write capabilities. Put approval in front of consequential writes.
- Preserve source, provenance, freshness, caveats, and unresolved exceptions in every decision-support artifact.
- Prefer an exception queue to a confident guess.

## Code conventions

- Keep the numbered examples independently readable.
- Put reusable deterministic logic in `src/codex_ones`; do not copy business logic into examples or the MCP server.
- Import paid/network SDKs lazily or only in examples. Offline tests must not call an API.
- Use strict schemas for model and tool boundaries.
- Bound agent turns, tool calls, inputs, outputs, and file paths.
- Do not log secrets, raw records, prompts, or tool payloads by default.
- Use `pathlib`, type hints, and clear domain names. Avoid framework-shaped abstractions until two examples need them.

## Documentation conventions

- Distinguish measured facts, assumptions, proposals, and decisions.
- Date claims about model names, package versions, APIs, or deployment behaviour.
- Explain why a pattern exists and show the smallest runnable version.
- If code and prose disagree, fix both in the same change.

## Validation

From this directory, run:

```powershell
python -m compileall -q src examples tests mcp-server/src mcp-server/tests
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python scripts\check_repo.py
```

Do not run paid API examples unless the user explicitly asks.
