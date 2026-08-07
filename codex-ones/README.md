# Codex Ones

This is a portable learning and delivery kit for building useful AI-assisted products—not a bag of impressive demos.

It starts with a synthetic university-insights scenario because that makes the hard questions visible: What is a fact? Who is allowed to decide? What can leave the machine? What happens when data is incomplete? How does a colleague verify the result? The same architecture transfers to counselling support, golf analysis, operations, and other domains.

The core rule is:

> Use code for facts, models for bounded judgment, and people for accountable decisions.

Start with [00-START-HERE.md](00-START-HERE.md). It gives the lesson order, setup commands, and the purpose of every example.

## What is included

- A ten-step path from deterministic Python to tools, agents, approvals, durable jobs, evals, and MCP.
- Reusable Python modules with offline tests.
- Synthetic application data with deliberate quality problems.
- Three Codex-native skills under `.agents/skills`.
- A read-only MCP server that works locally with no Cloudflare account.
- Architecture, governance, eval, deployment, and 30/60/90-day learning guides.
- Templates for product briefs, tool contracts, decision logs, and pilot runbooks.

## Fastest useful proof

No API key is needed:

```powershell
cd codex-ones
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python examples\01_deterministic_evidence.py
python examples\08_durable_job.py
python examples\09_local_evals.py
python scripts\check_repo.py
```

Then install the API lessons when you are ready:

```powershell
python -m pip install -e ".[learn,dev]"
Copy-Item .env.example .env
# Put OPENAI_API_KEY in .env; never commit it.
```

The MCP server deliberately uses a separate environment. See [MCP-WITHOUT-CLOUDFLARE.md](docs/03-MCP-WITHOUT-CLOUDFLARE.md).

## Repository map

```text
codex-ones/
├── 00-START-HERE.md       learning route
├── examples/              one runnable lesson per concept
├── src/codex_ones/        reusable deterministic core
├── data/                  synthetic input and local eval cases
├── tests/                 offline unit tests
├── mcp-server/            separately versioned MCP v2 service
├── .agents/skills/        portable Codex judgment workflows
├── templates/             artifacts for real pilots
└── docs/                  architecture and operational guidance
```

This repository is intentionally vendor-aware but not vendor-trapped. The evidence core is ordinary Python. Responses API and Agents SDK examples sit at the edges. MCP provides a protocol boundary that can be hosted wherever the organisation approves.
