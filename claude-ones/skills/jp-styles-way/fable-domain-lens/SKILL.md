---
name: fable-domain-lens
description: Activate explicitly on "fable domain lens" / "domain lens pass" / "behavior ledger". Also fits, unprompted, when starting a new feature or product area, when a feature request arrives ("can you add X"), or when prioritizing between features - anywhere the real question is what the user actually does, not what they asked for. Encodes the method for converting lived domain experience into falsifiable design requirements: behavior facts over stereotypes, the request-behind-the-request, and dating/testing each fact so it can be corrected by pilots.
---

# Fable Domain Lens

## Purpose

Technical skill tells you *how* to build. Domain knowledge tells you *what will actually
happen when a human meets the thing you built* — and that knowledge is the maker's real
moat, because it cannot be scraped or guessed. A former pro golfer knows what pressure
does to routine. A golf operations manager knows visitors arrive exactly on time and
ask everything at once. Seven years inside a university teaches the semester tide —
quiet weeks, then everyone drowning in the same fortnight. A year in insurance teaches
that the paper trail *is* the product when something goes wrong.

None of that appears in a requirements doc. All of it decides whether the product feels
like it was built by someone who has stood in the room.

This skill is the method for **cashing that knowledge in**: turning lived experience
into concrete, falsifiable design requirements — and keeping it honest, so a hunch from
2015 doesn't override what a 2026 pilot user shows you.

## Activation

Explicit triggers:
- "fable domain lens" / "domain lens pass" / "behavior ledger"

Self-activate, without being asked, when:
- scoping a new feature or product area from scratch
- a feature request arrives as a solution ("add a button that...") rather than a problem
- prioritizing a backlog where several items serve different user moments
- writing UI copy, defaults, or empty states (these are where domain knowledge shows
  most and costs least)

## The Method

### Step 1 — Write behavior facts, not personas

A behavior fact is one sentence, in the form **[who] does [observable action] because
[pressure/incentive]** — something you have personally watched happen, dated.

```markdown
- Counsellors write notes in a backlog batch at day's end, not per-session, because
  the next student is already at the door. (observed: pilot conversations, 2026)
- Visitors arrive exactly at their tee time and ask every question then, because
  arriving early feels like wasted time. (observed: golf ops, years of check-ins)
- University staff usage is tidal: near-zero, then everyone at once in the same two
  weeks. (observed: 7 years on campus)
- When an incident happens, the only thing that matters is what was recorded at the
  time — reconstruction after the fact is worth nothing. (observed: insurance)
- Under pressure, people abandon their trained routine and grab the shortest path.
  (observed: competitive golf — and every clinician at 5pm)
```

"Busy professionals value efficiency" is a stereotype, not a fact — it forbids nothing
and predicts nothing. A real behavior fact **predicts a specific user action** you must
design for, which is what makes it falsifiable.

### Step 2 — Convert each fact into a design consequence

One fact → one or more concrete requirements, each checkable in the built product:

| Behavior fact | Design consequence in this app |
|---|---|
| Notes are written in end-of-day batches | Batch beautify exists; drafts are first-class (`status='draft'`); Catch-Up Hub surfaces unlogged appointments |
| Arrive on time, ask everything at once | Cold start must reach the primary screen fast; auto-login; nothing heavy blocks reading data |
| Tidal usage | Peak-day performance is THE performance target; a queue that holds 10 items matters more than one that processes 1 item 20% faster |
| The record at the time is everything | Autosave as crash recovery; append-only activity log; backups on open/close/save — never only on demand |
| Pressure kills routine | The shortest path must also be the safe path — safety that requires discipline will be skipped exactly when it matters |

If a fact produces no consequence you can point to in the product, either the fact is
too vague (rewrite it) or the product has a gap (log it).

### Step 3 — Find the request behind the request

When a user asks for a feature, they are reporting a **moment of friction** wrapped in
their guess at a solution. Before building the guess, recover the moment:

```markdown
Request: "[what they asked for, verbatim]"
Moment: [where they were, what they were trying to do, what blocked them — ask if unknown]
Behavior fact it reveals: [add to the ledger]
Solution space: [their guess + at least one alternative that serves the same moment]
```

This codebase's own example: "reporting summaries" was first built as automatic-on-
complete — then the user correction (2026-06-11) revealed the real behavior fact:
*practitioners must control when the record is generated, because the record is theirs
professionally*. The feature was rebuilt practitioner-triggered. The request behind the
request was control, not automation.

### Step 4 — Date it, test it, let pilots overrule it

Every behavior fact carries its provenance (`observed: golf ops` vs `observed: pilot
user #2, 2026-07`). Rules:

- A fresh observation from a real user of THIS product **outranks** an old fact from an
  adjacent domain. The old fact got you to a good first guess; the pilot tells you if
  the guess landed.
- When a pilot contradicts the ledger, update the ledger in writing — don't quietly
  keep designing from the disproven fact.
- Facts from adjacent domains transfer at the level of **human pressure** (deadlines,
  arrival behavior, incident aftermath), not surface detail. "Golfers do X" doesn't
  transfer; "people under time pressure do X" might.

## Where Domain Knowledge Pays Most

In priority order — spend it here first:

1. **Defaults** — the default is what 90% of users live with forever. The domain expert
   knows which default matches the real workflow (e.g. draft-by-default, because notes
   are finished later).
2. **What NOT to build** — knowing counsellors won't tag/categorize manually kills a
   whole class of taxonomy features before they waste a month.
3. **Empty states and first-run** — the last-minute arriver judges the product in the
   first 90 seconds.
4. **Failure moments** — the insurance instinct: what exists as a record when things go
   wrong is worth more than any feature that works when things go right.
5. **Copy** — words the user's profession actually uses ("Higher Accuracy", never
   "Whisper"; "Support Diagnostic Log", never "telemetry").

## Verification Checklist

```markdown
[ ] Every design decision in the plan traces to a dated behavior fact, not a stereotype.
[ ] Every behavior fact predicts a specific action (falsifiable), names its source,
    and lives in the ledger where the next session can find it.
[ ] Every feature request was decomposed to its moment before its solution was accepted.
[ ] Adjacent-domain facts were transferred at the pressure level, not the surface level.
[ ] Pilot observations that contradict old facts updated the ledger in writing.
[ ] Defaults, empty states, and failure moments got domain attention before features did.
```

## Anti-Patterns

```markdown
- Persona documents full of adjectives ("busy", "tech-savvy") that forbid nothing.
- Building the requested solution without recovering the moment behind it.
- Treating your domain instinct as permanent truth after real users start disagreeing.
- Transferring surface details across domains ("golfers like leaderboards, so...").
- Spending domain knowledge on feature ideas while defaults and empty states stay generic.
- An undated behavior claim — if you can't say where it came from, you can't retire it.
```

## Key Principle

Your biography is a dataset nobody else has. The discipline is to treat it *as* a
dataset — extract facts, date them, design from them, and let newer data overrule older
data — instead of as a vibe. The maker who does this ships products that feel like they
were built by someone who has stood behind the counter, because they were.

Sibling skills: `fable-user-reality` (the universal behavior facts every product shares),
`fable-maker-compass` (which moments deserve a product at all), `fable-mode` (auditing
what got built).
