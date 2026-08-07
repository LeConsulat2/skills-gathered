"""
LESSON 6 — The tri-phase reviewer as PORTABLE Python, not a Claude Code agent.

The four files in `.claude/agents/` (see 08-real-agents-built-in-this-repo.md) do
the identical job, but they only work inside Claude Code — they're config, not
code. This file is the SDK-native version of the exact same idea: three
independent "lenses" checking the same target in parallel, then one call
synthesizing an honest, unsoftened verdict. This is what you'd actually hand a
client whose stack isn't Claude Code — it's Lesson 4's parallel-workers shape
(three lenses run concurrently) fused with Lesson 3's generator-critic idea
(the synthesizer isn't allowed to soften a real finding).

Each lens's system prompt below is a condensed, standalone version of the method
from the corresponding skill — not the skill file itself (a plain Python script
has no way to "load a Claude Code skill"), but the actual checklist logic written
out directly, so this script has zero dependency on Claude Code or this repo.

Run:
    python 09_tri_phase_review_pipeline.py
"""

import json
from concurrent.futures import ThreadPoolExecutor

import anthropic

client = anthropic.Anthropic()

# A stand-in "target" to review — in a real run this would be a diff, a plan
# section, or a description of the feature under review.
TARGET = """\
Feature: "Batch Export" button on the Reports page.

Behavior: clicking it disables the ENTIRE Reports page (a full-page spinner
overlay) while it generates PDFs for every client, one at a time, with no
progress indicator beyond the spinner. Takes 60-90 seconds for a large client
list. If the user navigates away or closes the tab, the export silently stops
partway through with no partial output and no way to resume — they have to
start over from zero. The button and spinner are plain white/grey, no styling
applied, sitting inside an otherwise glassmorphic page.
"""

# ---------------------------------------------------------------------------
# LENS 1 — user reality (condensed from the fable-user-reality method):
# does this survive a wandering user, and is every "disabled" justified?
# ---------------------------------------------------------------------------

UX_REALITY_SYSTEM = """\
You audit ONE thing: whether a described feature survives a user who wanders —
navigates away mid-operation, starts a second thing in parallel, switches to a
different record, or closes the app — mid-operation. For every operation over
~2 seconds, answer explicitly: what happens if the user does each of those four
things? For every "disabled" control, apply this test: complete the sentence
"if the user does X while this runs, then ___ is corrupted/lost." If nobody can
complete that sentence, the disable is unjustified — say so and name what it
should be instead (works fine as-is / queued for later / allowed with a warning).
Do not comment on visual style or on whether the underlying business decision
is grounded in real user behavior — only on interruption tolerance."""

# ---------------------------------------------------------------------------
# LENS 2 — domain grounding (condensed from the fable-domain-lens method):
# is this built on real observed behavior, or an untested assumption?
# ---------------------------------------------------------------------------

DOMAIN_LENS_SYSTEM = """\
You audit ONE thing: whether the design decisions in a described feature are
grounded in a real, checkable fact about how users actually behave, or whether
they're assumptions dressed up as requirements. For each design choice you can
identify (a default, a threshold, an interaction pattern, a claim about what
users want), ask: is there a dated, named source for this, or is it a guess?
Flag every undated claim and state the specific, falsifiable question that
would ground it — not "do more research," an actual answerable question. Do
not comment on visual style or on interruption tolerance — only on whether the
feature reflects real knowledge of the user versus a stereotype."""

# ---------------------------------------------------------------------------
# LENS 3 — style/design-system compliance (condensed, generic version of the
# antigravity-style-checker's method — swap this system prompt for your own
# project's actual design spec when you reuse this file elsewhere).
# ---------------------------------------------------------------------------

STYLE_SYSTEM = """\
You audit ONE thing: whether the described UI matches a premium, cohesive
design system — rich color/typography choices (not browser defaults), elevated
surfaces with real visual treatment (not flat/plain/unstyled elements), visible
progress feedback on anything asynchronous (not a bare spinner with no
information), and interactive/animated states rather than static ones. Flag
every element described as plain, default, unstyled, or uninformative, and say
what a properly styled and informative version would need instead. Do not
comment on interruption tolerance or on whether the feature is well-grounded in
user behavior — only on visual/interaction quality."""


def run_lens(system_prompt: str, label: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Review this:\n\n{TARGET}"}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return {"label": label, "report": text}


def run_all_lenses_in_parallel() -> list[dict]:
    # Same shape as Lesson 4: independent work, dispatched concurrently.
    # Three lenses on the same target have zero dependency on each other,
    # so there's no reason to run them one after another.
    lenses = [
        (UX_REALITY_SYSTEM, "user_reality"),
        (DOMAIN_LENS_SYSTEM, "domain_grounding"),
        (STYLE_SYSTEM, "style"),
    ]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(run_lens, sys_prompt, label) for sys_prompt, label in lenses]
        return [f.result() for f in futures]


def synthesize(lens_reports: list[dict]) -> str:
    # Same shape as Lesson 3's critic: told explicitly not to soften findings.
    response = client.messages.create(
        model="claude-opus-5",  # the judgment call gets the strongest model
        max_tokens=1024,
        system=(
            "You synthesize three independent review reports (user reality, "
            "domain grounding, style) into one ship/don't-ship verdict for a "
            "human. Never soften a real finding to make the summary sound "
            "better — if a lens found a real gap, say so plainly. If two "
            "lenses pull in different directions, name the conflict instead "
            "of silently picking a side. End with one of: SHIP AS-IS / SHIP "
            "AFTER FIXES (list them) / NEEDS REDESIGN."
        ),
        messages=[
            {
                "role": "user",
                "content": json.dumps(lens_reports, indent=2),
            }
        ],
    )
    return next(b.text for b in response.content if b.type == "text")


def main() -> None:
    print("Running three lenses in parallel...\n")
    reports = run_all_lenses_in_parallel()
    for r in reports:
        print(f"--- {r['label']} ---")
        print(r["report"])
        print()

    print("--- synthesized verdict ---")
    print(synthesize(reports))


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# HOW THIS DIFFERS FROM THE .claude/agents/*.md VERSION
#
# - No dependency on Claude Code, this repo, or the fable-* skill files — the
#   method each lens applies is written directly into its system prompt, so
#   this script is genuinely portable to a client's own infrastructure.
# - The lenses run in PARALLEL here (they're independent), where the Claude
#   Code orchestrator ran its three specialist agents in sequence — either
#   order is valid; parallel is strictly faster when nothing depends on
#   anything else, which is true here.
# - Swap STYLE_SYSTEM's content for whatever design spec a real client
#   actually has (their own brand guide, not Antigravity's) and this file
#   works unchanged for them — that's the entire point of writing the method
#   as a system prompt instead of hardcoding this project's specifics into
#   the Python logic itself.
# ---------------------------------------------------------------------------
