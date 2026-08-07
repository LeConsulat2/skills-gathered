# Skills Gathered

This repository is a personal learning and delivery library for building useful, inspectable AI-assisted products. It contains both the Claude-oriented material that shaped the approach and a Codex-native implementation designed for current, practical work.

The central principle is:

> Use code for facts, models for bounded judgment, and people for accountable decisions.

## Where to start

If you want to **learn and build with Codex, Python, the OpenAI API, agents, evals, and MCP**, begin with:

- [Codex Ones — Start Here](codex-ones/00-START-HERE.md)
- [Codex Ones overview](codex-ones/README.md)
- [30/60/90-day learning path](codex-ones/docs/07-30-60-90-LEARNING-PATH.md)

If you want to understand the **earlier ideas, experiments, and design influences**, begin with:

- [Claude programmatic agents — Start Here](<claude-ones/agents(programmatical)/00-START-HERE.md>)

## Repository map

```text
skills-gathered/
├── claude-ones/   original Claude-oriented skills, agents, and experiments
├── codex-ones/    Codex-native learning kit and reference implementation
├── AGENTS.md      working rules for contributors and coding agents
└── README.md      this orientation guide
```

### `claude-ones`

This is the source collection: conventional skills, agent definitions, programmatic examples, and product/design practices developed over time. Some files are portable patterns; others are historical, provider-specific, or intentionally one-off. Preserve that context when adapting them.

### `codex-ones`

This is the maintained learning path and practical reference implementation. It includes:

- deterministic evidence and data-quality code;
- structured-output and tool-calling examples;
- bounded single-agent and multi-reviewer patterns;
- human approval, auditing, durable jobs, and local evals;
- reusable Codex skills and delivery templates;
- a read-only MCP server that works without Cloudflare;
- university-focused safety and governance guidance.

All included application data is synthetic. The examples support evidence delivery and human decision-making; they do not automate admission, eligibility, enrolment, counselling, or clinical decisions.

## Quick start

The offline lessons require no API key:

```powershell
cd codex-ones
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python examples\01_deterministic_evidence.py
python examples\09_local_evals.py
python scripts\check_repo.py
```

For OpenAI API lessons, MCP setup, and deployment alternatives, follow [Codex Ones — Start Here](codex-ones/00-START-HERE.md) and [MCP without Cloudflare](codex-ones/docs/03-MCP-WITHOUT-CLOUDFLARE.md).

## How to use this repository

1. Learn the smallest deterministic version of a problem first.
2. Add a model only where bounded interpretation or tool selection creates value.
3. Turn domain expectations into executable eval cases.
4. Keep evidence, inference, recommendation, and decision visibly separate.
5. Design approval, exceptions, recovery, ownership, and shutdown before calling a prototype production-ready.

The goal is not to collect impressive demos. It is to create products and workflows that colleagues can understand, challenge, operate, and safely reuse.
