---
name: fable-refactor-discipline
description: Activate explicitly on "fable refactor discipline" / "refactor discipline pass" / "move-only check". Also fits, unprompted, whenever a task splits a large file, extracts hooks or components, moves/renames modules or folders, or is described as "refactor" / "reorganize" / "restructure" / "tidy the structure" — read it BEFORE touching any file, because in this repo the structural refactor is gated (.claude/plan/FABLES-REFACTOR-FINAL.md §1). Encodes the discipline - the gate check, behavior-drift-not-file-size as the enemy, hooks-before-JSX, the Extract test, move-only PRs, state-outlives-the-screen, facades/shims, invariants relocated byte-for-byte, and the stop rules that prevent over-refactoring.
---

# Fable Refactor Discipline

## Purpose

This is an **execution-discipline skill**, not a plan. The plan already exists and is
approved: `.claude/plan/CODEX-REFACTOR-SUGGEST.md` is the detailed playbook and
`.claude/plan/FABLES-REFACTOR-FINAL.md` is the decision on top of it (where they
disagree, FINAL wins). This skill exists because a plan doesn't protect you at the
moment of temptation — mid-PR, when "while I'm in here" whispers. It encodes the habits
that keep a structural refactor from becoming the app's next production bug.

The one-sentence version:

> **The risk of this refactor is behavior drift, not file size. Every rule below
> exists to move code without moving behavior.**

This repo's bug history is the proof: the licence-screen flash, the spinner regression,
the autosave clobber, the first-run transfer banner — every one was a small structural
or process change that drifted behavior. None was caused by a file being too long.

## Activation

Explicit triggers:
- "fable refactor discipline" / "refactor discipline pass" / "move-only check"

Self-activate, without being asked, when:
- a task splits, extracts from, or relocates any source file
- a task creates `src/shared/`, `src/features/`, `src/app/`, or any backend package move
- a PR description contains "refactor", "reorganize", "restructure", "cleanup", "split"
- reviewing someone else's (or a past session's) refactor diff

## Step 0 — The Gate (check before any structural work, every time)

The refactor is allowed to start **only** when all four conditions of
`FABLES-REFACTOR-FINAL.md` §1 are true. Do not inherit "the gate is open" from memory
or a prior session — verify it now:

1. Perf checklist functionally complete through Phase 8 (or explicitly descoped in
   writing) — read the **Current Status** block of
   `.claude/plan/CODEX-SONNET5-CHECKLIST.md`.
2. Result shipped in a real clinical build that passed the installed smoke test —
   dev-mode success is not enough.
3. Measured before-numbers written down (Phase 8) so regressions are checkable.
4. Jonathan explicitly said go, and the perf branch is merged.

If any condition is false: the only structural work permitted is what the perf
checklist itself requires. Say so and stop.

**At gate time, harvest the perf-era invariants** (`FABLES-REFACTOR-FINAL.md` §3):
every landed perf item — stats plumbing (`capture_stats`, `cold_start`/`ttft_ms`/
`decode_ms`/`rtf` fields), `stream_options: {"include_usage": true}`, sync-`def`
endpoints + the Whisper `threading.Lock`, llama-server spawn flags, exact
`faster-whisper` pins — joins the Phase 0 test list and relocates **byte-for-byte**.
A flag you don't recognize in a spawn `args` list is a measured decision, not lint.

**Known duplicate to reconcile, not rediscover (created 2026-07-10):**
`src/components/MarkdownEditor.tsx` does almost exactly what `SessionsPage.tsx`'s
`BeautifiedEditor` + its `markdownToHtml`/`htmlToMarkdown` converters do. It was
written as an independent copy rather than extracted, precisely because this gate
was closed at the time. It's already in real use — via `DocumentDetailView.tsx`
(rendered from `ClientHistoryPanel.tsx`) for the Visual Observations editor — so
when Phase 3 reaches `SessionsPage.tsx`, treat this as one seam to consolidate
under the Laws above, not a fresh extraction to invent.

## The Laws

1. **The unit of extraction is a state cluster, not a JSX block — hooks before
   components.** Measured 2026-07-10 (re-measure, don't inherit):
   `SessionsPage.tsx` was 6,993 lines with ~107 `useState`, 29 `useEffect`, 32
   `useRef`, and 50 `localStorage` touch points. That file is a state machine with a
   UI attached. Extracting JSX first leaves all the states behind and adds
   prop-drilling on top. Order, always: pure helpers/constants → hooks (each takes its
   states, effects, and refs with it) → JSX panels last, once their inputs are clean
   hook return values.

2. **State outlives the screen** (this is `fable-user-reality` corollary 1 wearing a
   refactor hat). Long-running state (streaming, recording, downloads, batch runs)
   never moves *down* into a component that can unmount. The always-mounted
   `SessionsPage`/`MeetingDashboard` architecture and the no-router rule exist to
   protect detached streaming — a "normal" feature-folder refactor that adds
   route-based mounting would kill it. Paid for once already: the 2026-07-06
   download-progress bug (state died in an unmounted Settings component).

3. **A move-only PR moves only.** Its diff is paths + imports + re-export shims —
   nothing else. No formatting, no renames of wire vocabulary, no `async def` ↔ `def`
   "tidying", no copy tweaks, no "while I'm in here" fixes. A behavior change you
   discover mid-move becomes its own PR, before or after — never inside.

4. **One component per file. No grab-bag files.** `SessionsPageComponents.tsx` must
   never exist — a barrel of components is the monolith with a moved address plus
   prop-list rot. A component earns extraction when it has a name, a small prop
   contract, and a reason (reuse, or independent understandability).

5. **Facade and shim, never import churn.** `src/utils/api.ts` stays as the public
   facade while internals move; old import paths keep working via re-exports and are
   migrated incidentally, not in a churn PR. Feature components never grow raw
   `fetch()` — token, 423, error, FormData, SSE, and download handling stay in the
   shared client.

6. **Invariants are test cases, and they move verbatim.** The Non-Negotiable
   Invariants section of `CODEX-REFACTOR-SUGGEST.md` plus the §3 perf-era list are
   the contract. If a refactor PR can't state which invariants its files carry, the
   PR isn't ready. When in doubt whether something is load-bearing: it is.

## The Extract Test

Before cutting any boundary (hook, component, module), complete this sentence with a
concrete answer:

> *"This unit can be understood without knowing ___ about the rest of the file."*

If you can't complete it, the boundary is wrong — don't cut there yet; pick a smaller
or different seam. (Sibling of the Disable test in `fable-user-reality`: no cut
without a nameable justification.)

## Stop Rules (the anti-over-engineering half)

- **Files under ~700 lines don't get touched.** No splitting `ClientsPage` (350
  lines) for symmetry. Symmetry is not a reason; pain is.
- **Don't pre-build the target tree.** A folder is created the day the first file
  moves into it. Empty scaffolding is how refactors become religions.
- **Done-state is behavioral, not aesthetic:** "a bug fix touches one small file with
  an obvious owner" — not "all files are small." When `SessionsPage.tsx` is an
  orchestrator of ~8 hooks and ~6 panels at 500–800 lines, the sessions refactor is
  DONE. Stop.
- **The end state should feel less clever, not more clever** (CODEX's closing line —
  adopted as the taste test for every PR).

## Per-PR Gates

Every refactor PR, no exceptions:

```powershell
npm run check:config
npx tsc --noEmit
npm run build:clinical
backend\env\Scripts\python.exe backend\run_security_tests.py
```

Plus:
- **Installed clinical smoke test** for anything touching Electron, packaging,
  startup, licence, lock, storage, backup, restore, encryption, updater, or audio.
- **Performance neutrality** (`FABLES-REFACTOR-FINAL.md` §3.3): after any phase
  touching an AI/transcribe path, re-run the Phase 8 baseline on the same fixed
  non-PHI input. Regression >10% on the reference machine blocks the PR until
  explained.

## Execution Order (condensed — FINAL §4 is authoritative)

```text
Phase 0   characterization tests + baselines (incl. §3 perf invariants) — no moves
Phase 1   shared storage keys/handoffs → shared API client (facade stays)
Phase 2   App.tsx startup/licence/security hooks (no router; always-mounted intact)
Phase 3   SessionsPage: helpers → handoffs → autosave → selection → transcription
          → beautify → reporting/take-away → JSX panels LAST
Phase 4-5 Settings panels; Meetings/Calendar/Clients/Audio
Phase 6   backend: system.py → exporters.py → ai.py → audio_queue.py → backups.py
          → license.py → database.py DEAD LAST (never before its five DB-state tests)
Phase 7   doc alignment + mark superseded plan docs archived-complete
```

Note the backend order is by risk, not size: `exporters.py` (3,778 lines as of
2026-07-10) is the biggest file but sits mid-order; `database.py` is smaller and goes
last anyway. Size never overrides risk.

## Templates

### Extraction plan entry (one per hook/component, written before the cut)

```markdown
Extracting: [name]  Kind: [hook / component / module]
Takes with it: [which states/effects/refs/helpers — enumerated]
Leaves behind: [what stays in the parent and why]
Contract: [props in / return value out — small enough to write here]
Long-running state: [none / lives at parent level / lives in backend-queue]
Extract test answer: "understandable without knowing ___ about the rest"
Invariants carried: [bullets from the invariant list, or "none"]
```

### Move-only PR self-check

```markdown
[ ] Diff contains ONLY: file moves, import updates, re-export shims.
[ ] Zero changes to: strings, wire vocabulary, async/sync-ness, flags, pins,
    key names, headers, DTO shapes, NSIS/packaging config.
[ ] Invariants in the moved files identified and relocated verbatim.
[ ] check:config + tsc + build:clinical + backend security suite green.
[ ] Smoke test run if the touched domain requires it; perf baseline re-run if an
    AI/transcribe path moved.
```

## Verification Checklist (self-check before delivering any refactor PR)

```markdown
[ ] Gate re-verified this session, not inherited (Step 0).
[ ] Extraction order was helpers → hooks → JSX, never JSX-first.
[ ] No long-running state moved into an unmountable leaf; no router introduced.
[ ] Every cut passed the Extract test, written down.
[ ] The PR is move-only OR behavior-only — never both.
[ ] No file under ~700 lines was touched for symmetry.
[ ] No grab-bag component files created.
[ ] Facade/shims preserved old import paths; no raw fetch() appeared.
[ ] All per-PR gates green; smoke/perf checks run where required.
```

## Anti-Patterns

```markdown
- Starting any structural work without re-checking the gate this session.
- "While I'm in here" — a behavior fix riding inside a move PR.
- SessionsPageComponents.tsx (or any *Components.tsx grab-bag).
- Extracting JSX panels while 100+ states still live in the parent.
- "Tidying" a sync def back to async def, or deleting a spawn flag you
  don't recognize.
- Creating the full target folder tree before the first file moves.
- Splitting a 350-line file because its siblings got split.
- An import-churn PR that migrates paths with no other purpose.
- Trusting a stale doc over current source (source and CLAUDE.md win).
- Declaring done because files are small, rather than because ownership is obvious.
```

## Key Principle

A structural refactor succeeds when nobody can tell it happened from inside the app.
Every rule here serves that: verify the gate now, cut along state seams not JSX seams,
keep long-running state above the leaf, move without changing, shim instead of churn,
and stop the moment ownership is obvious. When in doubt, the question is not "can this
file be smaller?" but **"if I move this, what behavior am I trusting to survive — and
which test proves it did?"**

Sibling skills: `fable-maker-compass` (should it exist), `fable-domain-lens` (what the
user actually does), `fable-user-reality` (how features behave when users wander),
`fable-mode` (the audit half — use it to re-verify claims before each refactor phase).
Doc chain: `CODEX-REFACTOR-SUGGEST.md` (playbook) → `FABLES-REFACTOR-FINAL.md`
(decision + gate; wins on conflict) → this skill (the discipline at the keyboard).
