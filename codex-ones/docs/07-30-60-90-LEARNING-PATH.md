# A 30/60/90-day path from prototype maker to agent product owner

The target is not to consume every framework. It is to produce one small, governed system that colleagues can understand and challenge.

## Days 1–30: make facts and boundaries boring

### Build

- Complete lessons 1, 2, 4, 8, and 9.
- Recreate the deterministic evidence packet from a different fully synthetic domain.
- Write ten eval cases from real structural problems, with all details fictionalised.
- Fill in `PRODUCT-BRIEF.md`, `TOOL-CARD.md`, and `DECISION-LOG.md`.

### Learn

- Responses function-calling loop.
- Strict structured outputs.
- SQL/Python ownership of facts.
- Data classification and decision rights.
- SQLite state transitions, idempotency, and recovery.

### Prove

- Another analyst can explain every metric from the artifact.
- Unknown and conflicting data cannot become a confident answer.
- The workflow survives restart and shows a useful status.
- Tests run without a model or network.

### Deliverable

An evidence-only prototype and a two-page architecture/purpose brief. No multi-agent system yet.

## Days 31–60: add bounded model judgment and MCP

### Build

- Complete lessons 3, 5, 6, and 10.
- Run the MCP server in memory, over stdio, and on loopback HTTP.
- Build one additional read-only tool over synthetic data.
- Add 20 model cases: normal, ambiguous, stale, conflicting, injection, and out-of-scope.
- Compare Terra and Sol on the same frozen cases; optionally test Luna on narrow tasks.

### Learn

- Agents SDK runtime, tools, tracing, and serializable approvals.
- Why guardrails differ from authorization.
- MCP tools versus resources versus prompts.
- Tool error semantics and least-privilege identities.
- Parallel review without forced consensus.

### Prove

- The model selects only the allowed read tool.
- A write pauses, displays the exact action, survives serialization, and can be rejected.
- No model-generated identity or path reaches an authorization boundary.
- The smaller model is used whenever it clears hard gates.

### Deliverable

A local read-only MCP capability, an evaluated agent client, and a live approval demonstration—all synthetic.

## Days 61–90: design a bounded organisational pilot

### Discover

- Observe five target users doing the current job.
- Capture recent behaviour, exception paths, workarounds, and verification habits.
- Identify the metric/domain owner, data owner, service owner, and decision owner.

### Design

- Choose one wedge that avoids automated high-stakes decisions.
- Create the approved data view and field-level boundary with the relevant teams.
- Select the organisation's existing runtime, identity, secrets, logging, and support path.
- Define success, serious-error, stop, and expiry criteria before launch.

### Drill

- stale and conflicting data;
- provider/model failure;
- worker crash and retry;
- approval rejection and later resume;
- prompt injection in retrieved content;
- revoked user access;
- incorrect publication attempt;
- kill switch and rollback.

### Deliverable

A review pack, not just an app:

- product brief;
- architecture and data-flow diagram;
- threat/decision-rights model;
- agent and tool contracts;
- eval report and model selection evidence;
- pilot runbook;
- support and rollback ownership;
- demo using synthetic data;
- explicit request for the next approval.

## Weekly practice rhythm

Use a four-part loop:

1. **Observe:** one real workflow moment or failure pattern.
2. **Encode:** turn it into a contract, synthetic fixture, or eval.
3. **Build:** make the smallest implementation change.
4. **Teach:** explain the artifact to a non-technical colleague and record what confused them.

Teaching is an eval. If the person cannot see where a number came from or who decides, the product contract is incomplete.

## Three portfolio tracks

### University insights

Build a definition-aware evidence and reconciliation service. Keep the first pilot aggregate, read-only, and human-reviewed.

### Golf

Build a session evidence packet from synthetic launch-monitor/shot data, then a coach-reviewable practice draft. Separate measured ball-flight data, player report, video inference, coaching hypothesis, and selected drill.

### Counselling support

Begin with non-clinical synthetic workflow artifacts such as appointment preparation or practitioner-controlled template assistance. Before any sensitive or clinical data, obtain professional, privacy, security, records, and safety review. The domain boundary—not code reuse—is the main work.

## What mastery looks like

You can explain, implement, and defend:

- why a component is deterministic, model-assisted, agentic, or MCP;
- what data crosses each boundary;
- which person retains each decision right;
- what the system does when it does not know;
- how a failure becomes a regression case;
- how the work resumes after interruption;
- how the service is stopped, supported, and retired.

That is the skill set teams rely on when prototypes become real organisational systems.

