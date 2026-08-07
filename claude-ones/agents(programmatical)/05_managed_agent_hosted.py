"""
LESSON 5 — Handing the whole loop off to Anthropic (Managed Agents).

Everything in Lessons 1-4 is a script: it runs on YOUR machine or YOUR server,
for as long as YOUR process stays alive. That's fine for a script you kick off
yourself. It stops being fine when a client needs:
    - a sandboxed workspace where the agent can run bash/read/write files
      WITHOUT you having to build and secure that sandbox yourself
    - a session that can run for a long time, survive your laptop closing
    - something that runs on a SCHEDULE (nightly, weekly) with no process of
      yours needing to be alive to trigger it
    - persisted, versioned agent configs you can roll back if a prompt change
      goes wrong in production

That's "Managed Agents" (CMA): Anthropic runs the agentic loop AND hosts the
container where its tools execute. You define an Agent (persisted, versioned)
and an Environment (the sandbox template), then create Sessions against them.

IMPORTANT — read before running:
    - This is a BETA surface and needs the `managed-agents-2026-04-01` beta
      header (the SDK sends it automatically for every client.beta.* call
      below) and your organization may need it enabled.
    - This costs real money per session (model tokens + container time) —
      don't loop-run this file. Run it once, watch the console URL it prints,
      then read the code.
    - Unlike Lessons 1-4, this genuinely needs a live account with access to
      the feature. If it errors on agents.create(), that's most likely why.

Run:
    python 05_managed_agent_hosted.py
"""

import anthropic

client = anthropic.Anthropic()


def main() -> None:
    # -----------------------------------------------------------------
    # STEP 1 (ONE-TIME SETUP): create the Environment — the sandbox template.
    # In production this is created ONCE, its ID saved, and reused across
    # every future session — never re-created per run. Same for the Agent
    # below. See 06-consulting-playbook.md for why "create once, reuse
    # forever" matters (it's the single most common mistake in this API).
    # -----------------------------------------------------------------
    environment = client.beta.environments.create(
        name="learning-agents-demo-env",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    print(f"environment created: {environment.id}")

    # -----------------------------------------------------------------
    # STEP 2 (ONE-TIME SETUP): create the Agent — model, system prompt,
    # and tools all live HERE, never on the session. This is the single
    # most common mistake people make with this API: trying to pass
    # `model=` or `system=` to sessions.create() instead of agents.create().
    # -----------------------------------------------------------------
    agent = client.beta.agents.create(
        name="Repo Summarizer Demo",
        model="claude-opus-5",
        system=(
            "You are given a small workspace. Read what's there and write "
            "a two-paragraph summary of what it contains to "
            "/mnt/session/outputs/summary.md."
        ),
        tools=[{"type": "agent_toolset_20260401"}],  # bash, read, write, glob, grep, web_*
    )
    print(f"agent created: {agent.id} (version {agent.version})")

    # -----------------------------------------------------------------
    # STEP 3 (EVERY RUN): create a Session that references the agent +
    # environment by ID, and kick it off with an initial message.
    # -----------------------------------------------------------------
    session = client.beta.sessions.create(
        agent={"type": "agent", "id": agent.id, "version": agent.version},
        environment_id=environment.id,
        title="Demo run",
        initial_events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "There's nothing mounted yet — just write a short "
                            "note explaining you're a demo agent with no real "
                            "workspace attached, then stop."
                        ),
                    }
                ],
            }
        ],
    )
    print(f"session created: {session.id} (status: {session.status})")
    # Watch it live in the Console — swap 'default' for your workspace ID if
    # the API key isn't in the org's Default workspace.
    print(
        f"watch live: https://platform.claude.com/workspaces/default/sessions/{session.id}"
    )

    # -----------------------------------------------------------------
    # STEP 4: stream events until the session is genuinely done.
    #
    # The break condition matters: `session.status_idle` fires MULTIPLE
    # times during a run (e.g. between parallel tool calls) — it does NOT
    # mean "finished". Only break on session.status_terminated, or on
    # status_idle whose stop_reason is anything other than "requires_action".
    # -----------------------------------------------------------------
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print("[agent]", block.text)
            elif event.type == "session.status_terminated":
                print("[session terminated]")
                break
            elif event.type == "session.status_idle":
                if event.stop_reason.type == "requires_action":
                    continue  # waiting on us for a tool confirmation/result — not done
                print(f"[session idle, done: {event.stop_reason.type}]")
                break


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# THE PART THAT MATTERS MOST FOR CLIENT WORK: SCHEDULING
#
# Everything above still needs YOU (or a caller) to hit "run" once. For a
# genuinely recurring deliverable — "run this every Friday at 5pm and email
# the result" — you don't build your own cron job that calls this script.
# You create a DEPLOYMENT: the same agent + environment, plus a cron schedule.
# Anthropic fires a new session automatically on that schedule; no process of
# yours needs to be running for it to happen. This is the one-time setup:
#
#   deployment = client.beta.deployments.create(
#       name="Weekly repo digest",
#       agent={"type": "agent", "id": agent.id, "version": agent.version},
#       environment_id=environment.id,
#       initial_events=[{
#           "type": "user.message",
#           "content": [{"type": "text", "text": "Summarize this week's changes."}],
#       }],
#       schedule={
#           "type": "cron",
#           "expression": "0 17 * * 5",       # 5pm every Friday
#           "timezone": "America/New_York",
#       },
#   )
#
# Every firing writes a `deployment_run` record you can audit later
# (client.beta.deployment_runs.list(deployment_id=deployment.id)) — this is
# the actual production answer to "make an agent that does X every week for
# a client", not a cron job wrapping one of the scripts in this folder.
# ---------------------------------------------------------------------------
