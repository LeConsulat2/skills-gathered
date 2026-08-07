"""
LESSON 3 — Your first MULTI-agent system: generator + critic.

Everything so far was ONE model with ONE job. Real leverage shows up when you give
different roles to different calls and let them check each other — the same reason
a second pair of human eyes catches things the writer can't see in their own work.

The pattern:
    1. GENERATOR writes a first draft of something (here: a short client-facing
       incident summary from raw notes).
    2. CRITIC — a SEPARATE call, with a DIFFERENT system prompt, that has never
       seen the generator's reasoning — reviews the draft against a rubric and
       returns either "APPROVED" or a specific list of problems.
    3. If the critic found problems, they go back to the generator as feedback,
       and we loop, up to a max number of rounds. If the critic approves, we stop.

This is the "adversarial pair" / "writer-verifier" pattern. It matters because a
single model reviewing its own output is checking its own homework — it tends to
agree with itself. A SEPARATE call with a narrower, skeptical job description
catches real problems more often, because that's its ONLY job and its context
isn't anchored on "I already decided this is good."

Run:
    python 03_generator_critic_pipeline.py
"""

import anthropic

client = anthropic.Anthropic()

MAX_ROUNDS = 3

GENERATOR_SYSTEM = """\
You write short, clear incident summaries for non-technical stakeholders from
raw engineering notes. Be factual. Never invent a cause, a timeline, or an
impact number that isn't in the notes. If the notes don't say something,
say it's not yet known rather than guessing."""

CRITIC_SYSTEM = """\
You are a skeptical fact-checker reviewing an incident summary against the
original raw notes it was supposedly built from. Your ONLY job is to find
problems — you do not write summaries yourself.

Check specifically for:
1. Any claim in the summary NOT supported by the raw notes (fabrication).
2. Any important fact IN the raw notes that the summary left out.
3. Jargon a non-technical reader would not understand.

Respond with EXACTLY one of two formats:
- The single word APPROVED, if you find nothing wrong.
- A numbered list of specific problems, each one sentence, if you find any.
Do not soften real problems to be polite. Do not approve to save time."""

RAW_NOTES = """\
14:02 UTC - alerts fired for elevated 500s on checkout-api, ~8% error rate
14:05 - on-call confirmed, checkout-api pods CPU-throttled after a deploy at 13:58
14:11 - rolled back the 13:58 deploy
14:14 - error rate back to baseline (<0.1%)
root cause: new deploy set CPU request too low for the pod, throttling under load
no customer data was affected. no payments were double-charged.
about 40 checkout attempts failed during the window; customers who retried succeeded.
"""


def generate_draft(feedback: str | None = None) -> str:
    user_content = f"Raw notes:\n{RAW_NOTES}"
    if feedback:
        user_content += (
            f"\n\nA reviewer found problems with your last draft. Fix these "
            f"specific issues and write a new draft:\n{feedback}"
        )

    response = client.messages.create(
        model="claude-sonnet-5",  # good writing quality at lower cost than Opus
        max_tokens=1024,
        system=GENERATOR_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
    )
    return next(b.text for b in response.content if b.type == "text")


def review_draft(draft: str) -> str:
    response = client.messages.create(
        # The critic gets the STRONGER model. This is a deliberate cost choice:
        # spend your best judgment on catching mistakes, not on first drafts.
        model="claude-opus-5",
        max_tokens=1024,
        system=CRITIC_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Raw notes:\n{RAW_NOTES}\n\nSummary to review:\n{draft}"
                ),
            }
        ],
    )
    return next(b.text for b in response.content if b.type == "text")


def run_pipeline() -> str:
    feedback = None
    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"\n=== round {round_num}: generating ===")
        draft = generate_draft(feedback)
        print(draft)

        print(f"\n=== round {round_num}: reviewing ===")
        verdict = review_draft(draft)
        print(verdict)

        if verdict.strip().upper().startswith("APPROVED"):
            return draft

        feedback = verdict  # feed the critic's exact complaints back in

    # Ran out of rounds without approval — a real pipeline should surface this
    # as "needs human review" rather than silently shipping an unapproved draft.
    print("\n=== max rounds reached without approval — flagging for a human ===")
    return draft


if __name__ == "__main__":
    final = run_pipeline()
    print("\n--- final draft ---")
    print(final)

# ---------------------------------------------------------------------------
# WHY THIS IS "AGENT DESIGN", NOT JUST TWO API CALLS IN A ROW
#
# The design decisions ARE the skill here, and they transfer to any client
# engagement built on this pattern:
#   - The critic's system prompt is narrow and adversarial ON PURPOSE. A vague
#     "please review this" critic tends to just say "looks good" — you have to
#     tell it explicitly what kinds of problems to hunt for.
#   - The critic never sees the generator's private reasoning, only the raw
#     inputs and the output — exactly what a real second reviewer would see.
#   - There's a hard round cap with an explicit "give up and flag a human"
#     path. An agent loop with no exit condition is a production incident
#     waiting to happen (infinite spend, infinite latency).
#   - Model tiers are assigned by JOB, not uniformly: cheaper/faster for the
#     first draft, stronger for the judgment call that decides whether to
#     ship. This is the same cost-engineering idea as Lesson 4, applied to
#     quality instead of throughput.
# ---------------------------------------------------------------------------
