---
name: fable-bug-fix
description: Activate explicitly on "fable bug fix" / "bug-fix mode" / "fable bug-fix mode". Also fits, unprompted, whenever a bug is reported as STILL broken after a previous "fixed" claim, or the symptom is user data that "disappeared", reverted, or snapped back to an older value — especially around autosave, drafts, caches, or ordinary navigation (switch draft, go Home, close app, come back). In this repo, this is the preferred variant — it cites the real worked example (bugs-fixed/040-23072026.md, SessionsPage.tsx); for any other codebase copy fable-bug-fix-portable instead. Encodes: literal-repro-first, "disappeared is a hypothesis, not a diagnosis", the fact census (enumerate every copy of the fact before touching any one of them), silent-write-paths-are-guilty-first, the sibling-writer diff, re-read-the-file-not-the-narration on round 2+, and an honest confidence ladder where "typechecks clean" is never "verified".
---

# Fable Bug-Fix Mode

## Purpose

This skill was distilled from a real bug that was declared "fixed" three times. Same
user-visible symptom every round — an overwritten draft silently reverting to its old
content after ordinary navigation — and three genuinely different root causes underneath,
each one hiding behind the previous fix. Every fix was correct and necessary; none was
sufficient, because each round only examined the pair of data copies implicated in *that
round's* repro instead of asking the expensive question up front:

> **"How many copies of this fact exist in total, and does this specific write touch all
> of them?"**

The skill is the method that finally broke the loop, generalized so it works in any
codebase. It is a *diagnosis and verification* discipline, not a coding style — use it to
find the real bug and to be honest about how verified the fix actually is.

## Origin — the worked example (real, in this repo)

**Read `bugs-fixed/040-23072026.md` first** — it is the complete worked example of this
skill's method, with exact code, mechanisms, and every dead end preserved in place. The
compressed version: a session's working draft lived in **three places** — the
`sessions.transcript` DB row, the debounced `private_autosave_session_<clientId>`
localStorage snapshot, and the in-memory `sessions` array `SessionsPage.tsx` reopens
drafts from (`handleSelectSession`, the `prefill_session_id` handoff, the sidebar list).

| Round | Claimed fix (commit) | Actual root cause found later |
|---|---|---|
| 1 | `handleSelectSession` overlays a newer localStorage snapshot (matching `savedSessionId`) over the raw DB row (`d3a48cd`) | Reopen read straight from the stale DB object, ignoring a newer localStorage snapshot tagged for that exact session |
| 2 | New durable per-session DB autosave (1.5s debounce); key terms rescoped to `sessions.key_terms` (`99425cb`) | The localStorage snapshot was **one slot per client**, not per session — opening a second draft for the same client silently evicted the first draft's unsaved edit before it ever reached the DB |
| 3 | The round-2 autosave's `.then()` and the Beautify normal-path auto-persist now also update the `sessions` array (also in `99425cb`) | The round-2 `PATCH` was **correct** — but nothing told the in-memory `sessions` array it happened, so reopening the draft repainted the pre-write copy over the screen |

The pattern under all three: **the same fact lived in more than one place, and a write
path updated one copy without updating its siblings.** Round 1 was DB vs. localStorage.
Round 2 was one cache slot vs. N sessions wanting it. Round 3 was DB vs. the in-memory
array the UI actually reads from. Three costumes, one species.

What broke the loop in round 3 was not new information — the code had been sitting there
the whole time. It was: (a) refusing to trust the bug doc's own prior narration and
re-reading the literal current `SessionsPage.tsx`, and (b) for the new write round 2 had
introduced, grepping *every other call site* that writes a session (`handleDeleteSource`,
`handleSave`, the other `saveBeautifyResult` callers) and diffing what they update
afterward. Three already refreshed `sessions` (via `setSessions` or
`loadDisplaySessions()`). The new silent autosave didn't. That diff was the bug.

## Activation

Explicit triggers (any of these activates this mode for the rest of the task):

- "fable bug fix" / "bug-fix mode" / "fable bug-fix mode"

Also self-activate, without being asked, when a request has this shape:

- a bug reported as **still broken** after one or more previous "fixed" claims — the
  strongest trigger; go straight to Phase 5's rules
- user data described as "disappeared", "gone", "reverted", "back to the old version",
  "didn't save", or "lost my edits"
- any bug involving autosave, debounced/background persistence, caches, snapshots, or
  drafts — especially when the repro involves ordinary wandering (switch to another
  record, go to another tab, close the app, come back later)
- a save that "works" until the user navigates away and returns

## The Method

### Phase 0 — Extract the literal repro from the user's own words

Before reading any code, write down the user's scenario **verbatim** — their sequence,
their timing, their exact words. It is the ground truth, and it frequently *is* the
diagnosis. (In the origin case, "no problem for ones that did not have any notes before —
it's the ones that had a draft before and you overwrite" was the complete root-cause
statement, given before any code was read. It was right every round.)

Rules:

- Do not generalize prematurely. "Switch to a different draft **for the same client**,
  then come back" is a different code path from "switch to another client" — the specific
  navigation IS the spec, and it is also the final verification script (Phase 6).
- The user's frustration-phrased description is data, not noise. Mine it for the exact
  conditions: what had prior content, what was new, how long they dwelled, where they
  went, when they came back.
- Treat ordinary wandering as normal use, not edge-case polish. Users treat an app like a
  room they walk around in, not a script they follow. An autosave that only works if the
  user stays on one record and never navigates is not "mostly working" — it is broken.

### Phase 1 — "Disappeared" is a hypothesis, not a diagnosis

Before assuming data loss, check whether the durable store actually has the data:

- **Data genuinely absent from the durable store** → a write-path bug. Repair the write.
- **Data present in the durable store, but the screen shows an older value** → a
  read/refresh-path bug (stale copy repainted over the truth). Repair the read.

These need **opposite fixes**, and misclassifying costs a full round. (Origin round 3 was
exactly this: the DB write succeeded every time; only the in-memory list was stale. It
*looked* identical to data loss from the user's seat.)

### Phase 2 — The fact census

Before touching any code, enumerate **every** place the fact lives. Standard suspects, in
the order they get forgotten:

1. The durable store row (DB, file, server).
2. Any cache/snapshot layer (localStorage, sessionStorage, an on-disk temp file) — and
   note its **keying granularity**: a cache keyed per-parent when the fact is per-child
   *guarantees* silent eviction the moment two children exist (origin round 2).
3. The in-memory "currently open/selected" object.
4. **Any in-memory list/array that a future reopen reads from.** This is the copy that
   got missed three rounds running — the write can be perfect and the very next reopen
   still repaints the stale list entry.
5. Snapshots captured for async/background runs (the values a long-running job saw at
   launch, applied at completion).

For each copy, answer: who writes it, on what trigger, and which of the *other* copies
does that write also update? Fill in the census table (Templates below) before proposing
any fix. If a write leaves any sibling stale, either that's the bug or it's the next
round's bug.

### Phase 3 — Silent write paths are guilty until proven innocent

Explicit-save buttons are usually fine — a user is watching, they get reviewed carefully,
and they tend to already refresh the sibling copies. Debounced, background, and
auto-persist effects are exactly the code that gets added fast, watched by no one, and
reviewed least — **all three rounds' bugs in the origin case lived in silent write
paths.** Audit those first, and audit any new one you introduce hardest of all: a fix
that adds a silent write path must itself pass Phase 4 before it ships.

Also check the flip side: a silent write that succeeds and then sets an "everything is
saved" flag (`hasUnsavedChanges = false` and friends) while having persisted only *some*
fields is worse than no write — it tells the UI, and the user, a lie.

### Phase 4 — The sibling-writer diff

For any write to an existing record — especially a **new** write path you are about to
add — grep every other call site that writes the same record type, and diff what each of
them updates afterward. If N−1 of them refresh the sibling copies and one doesn't, that
diff is the bug (or the bug you are about to ship). This single check, run at round 2,
would have prevented round 3 entirely: the correct pattern already existed three times in
the same file; the new effect just hadn't copied it.

This also tells you the right *shape* of the fix: match the sibling call sites' existing
pattern rather than inventing a new one.

### Phase 5 — Round 2+: re-read the file, not the narration

When the same symptom comes back after a "fixed" claim, special rules apply:

- **Distrust all prior narration — including your own.** The bug doc's description of
  what the previous fix did, the previous session's summary, your memory of the code:
  none of it is evidence. Open the literal current file and trace what is actually there.
  The previous fix's mental model is the trap — each failed round re-derives its
  diagnosis from the last round's model instead of re-running the census.
- **Assume the previous fix was correct AND incomplete.** That is the common case (it was
  the case all three rounds). Don't rip it out; find what it didn't cover. The question
  is never "was the fix wrong" first — it's "which copy of the fact did it still not
  touch", and specifically: **did the previous fix itself introduce a new write path, and
  did that new path get the Phase 4 treatment?**
- Re-run Phase 2's census from scratch. The copy that explains this round is usually one
  that wasn't on the previous round's list at all.

### Phase 6 — The confidence ladder (never blend rungs)

These are strictly different levels of confidence. Name the rung you actually reached —
in the final summary and in the bug doc — and never present a lower rung as a higher one:

1. **Typecheck/compile clean** — the code is syntactically coherent. Nothing more.
2. **Unit/self-checks pass** — the isolated logic behaves.
3. **The service boots / the migration applies** against a real database.
4. **Click-through under the user's EXACT navigation from Phase 0** — the only rung that
   closes the bug.

In the origin case, two consecutive rounds shipped at rung 1 with the word "fixed"
attached, and both failed live testing. "tsc clean" is not "verified", and blending them
into one "done" burns the user's trust and their time.

If rung 4 is unreachable in your environment, **say so explicitly, do not fake it, and do
not quietly skip it.** In this repo that is the normal case: the only database on this
machine is `backend/local_private.db` — real clinical data, never to be click-tested
against — there is no throwaway licence key to activate a scratch workspace, and the
workspace may be PIN-locked. Hand back numbered repro steps in the user's own scenario
(including "restart the app/dev server first so the fix actually loads"), and state
plainly that the fix is code-traced, not click-verified. That honesty is what lets the
user's live test function as the real rung 4 instead of a surprise round N+1.

### Phase 7 — Write it down so round N+1 is cheap

One document per bug, updated in place across rounds — supersede, never erase. The
failure history is precisely what makes the next round solvable: round 3's breakthrough
required knowing exactly what rounds 1 and 2 claimed and where those claims broke.

The write-up must carry:

- The user's verbatim repro and their own diagnosis (Phase 0).
- The root cause **with the why**, not just the what — the reasoning that makes the fix
  correct rather than merely different. If a design decision was involved (e.g. changing
  a fact's scoping), record the user's concrete justifying example, because that
  reasoning is what future sessions need to not undo it.
- What was **deliberately not changed** and why — the guard against a future session
  blindly copying the fix into a path where it's wrong.
- The status line at the top updated every round ("live-tested and failed — see Update
  N"), so the doc never claims more than the highest rung actually reached.
- A handover list and a paste-ready resume prompt for the next session.

## Templates

### Fact census (Phase 2 — fill before proposing any fix)

```markdown
Fact under investigation: [e.g. "a session's working-draft text"]

| # | Copy | Keyed by | Written by (trigger) | Which siblings does that write update? |
|---|---|---|---|---|
| 1 | DB row `X.field` | record id | explicit Save; [any silent path?] | ... |
| 2 | cache/localStorage `key` | [per-record? PER-PARENT? ← check] | debounced effect (Ns) | ... |
| 3 | in-memory selected object | — | set on open; [after saves?] | ... |
| 4 | in-memory list/array reopen reads from | — | initial load; [after silent saves? ← usual gap] | ... |
| 5 | async-run snapshot | captured at launch | applied at completion | ... |

Stale-sibling risks found: [every write whose row above leaves a sibling blank]
```

### Sibling-writer diff (Phase 4)

```markdown
Record type: [X]   Write sites found (grep for the update/save call):

| Call site | Updates durable store | Updates selected object | Updates list/array | Updates cache |
|---|---|---|---|---|
| explicit save handler | ✓ | ✓ | ✓ | ✓ |
| delete/mutate handler | ✓ | ✓ | ✓ | — |
| silent autosave effect | ✓ | ? | **✗ ← suspect** | ✓ |

The odd row out is the bug (or the bug being shipped). Fix shape: copy the pattern the
conforming rows already use.
```

### Confidence statement (Phase 6 — goes in the final summary verbatim)

```markdown
Verification reached: rung [1-4] of 4.
- [what was run and its result, per rung]
- NOT done: [e.g. click-through under the Phase 0 navigation] because [real constraint].
- To close this as verified, reproduce: [numbered steps in the user's exact scenario,
  starting with "restart the app/dev server so the fix loads"].
```

## Verification Checklist (self-check before claiming anything)

```markdown
[ ] The user's repro is recorded verbatim, and the fix was reasoned against THAT
    navigation, not a generic version of it.
[ ] "Data lost" vs "display stale" was explicitly determined, not assumed.
[ ] The fact census is complete — including the in-memory list/array a reopen reads from
    and every cache's keying granularity.
[ ] Every silent/background write path touching this fact was audited, not just the one
    in the repro.
[ ] The sibling-writer diff was run; the fix matches the conforming call sites' pattern.
[ ] If this is round 2+, the current file was re-read directly; no claim was inherited
    from the bug doc, a previous session, or memory.
[ ] If the fix adds a new write path, that path itself passed the sibling-writer diff.
[ ] No "saved" flag is set anywhere that persists only part of the fact.
[ ] The confidence rung is stated explicitly; lower rungs are not dressed as higher ones.
[ ] If rung 4 wasn't reached, the constraint is named and numbered repro steps are
    handed to the user.
[ ] The bug doc is updated in place: status line current, why-not-just-what root cause,
    deliberately-not-changed list, handover, resume prompt.
```

## Anti-Patterns

Avoid:

```markdown
- Fixing the pair of copies implicated in this round's repro without censusing the rest.
- Trusting the bug doc's narration of the previous fix instead of the current file.
- Declaring "fixed" from a clean typecheck — or letting "fixed" appear anywhere the
  confidence rung isn't stated beside it.
- Treating "disappeared" as data loss before checking whether the durable store has it.
- Ripping out the previous round's fix because the symptom returned — it is usually
  correct and incomplete, and removing it adds a fourth bug.
- Adding a new silent write path without running it through the sibling-writer diff.
- Setting an "all saved" flag after persisting only some of the fact's fields.
- Verifying with a generic smoke test instead of the user's exact stated navigation.
- Treating navigation-heavy repros (switch, go Home, close app, return) as edge cases.
- Quietly skipping live verification instead of naming the constraint and handing the
  user the exact steps.
- Erasing failed-round history from the bug doc instead of superseding it in place.
```

## Key Principle

Every recurring bug in this class is the same species wearing a different costume: **one
fact, many copies, a write that updates some of them.** The reason it takes three rounds
instead of one is never a lack of information — the code is sitting there the whole
time — it's that each round asks the cheap question ("which copy broke this repro?")
instead of the expensive one ("how many copies exist, and does this write touch all of
them?"). Ask the expensive question first; it is far cheaper than the third round.

## Pairing

Works alongside, not instead of, its siblings in this repo:

- `local-first-restore-hydration-triage` — names the *entry-path* symptoms (restore keys,
  PIN-boot hydration, one-shot `prefill_*` handoffs, always-mounted pages) and should be
  read together with this skill on any "data doesn't appear here" bug; this one adds the
  fact census, the sibling-writer diff, the round-2+ discipline, and the confidence
  ladder.
- `fable-user-reality` — its wandering law is this skill's Phase 0 stance: switching
  drafts, going Home, closing the app, and coming back tomorrow is the product working
  at all, not polish.
- `fable-bug-fix-portable` — the product-agnostic copy of this skill; take that folder,
  not this one, into a new project.
