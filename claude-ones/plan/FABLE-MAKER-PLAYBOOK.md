# FABLE Maker Playbook — Jonathan's Portable Product-Building System

**What this is:** a product-agnostic playbook extracted from how PRIVATE was actually
built — the design style, working preferences, logic patterns, and process discipline
that made it good. Written 2026-07-07 by Fable 5, from the codebase, the plan folder,
the bugs-fixed journal, and project memory.

**How to use it:** copy this file into any new project's plan folder on day one, work
through Phase 0 before writing code, and treat the Preference Registries (§B–§E) as
your defaults — deviate deliberately, never accidentally. The three portable skills
(`fable-maker-compass-portable`, `fable-domain-lens-portable`,
`fable-user-reality-portable`) are the reusable thinking tools; this document is the
end-to-end sequence that strings them together.

**Applies to:** desktop apps, web services, mobile apps, community sites, MCP servers,
AI analysis tools — the sections mark themselves N/A where a product type genuinely
has no equivalent (e.g. an MCP server has no UI palette, but it absolutely has
"plain-language naming" and "status lifecycles").

---

## Part A — The Build Sequence (phases, in order, with gates)

### Phase 0 — The Compass (before any code)

Write these four things down in the new repo. Not in your head — in a file.

1. **The picture:** one person, in one moment of pressure, using the product.
   Not a persona document — a photograph in words. (PRIVATE's was: *a counsellor,
   end of day, four sessions behind on notes, on a mediocre laptop, in an
   institution that would never approve a cloud tool.*)
2. **The wedge:** one sentence — moat + price story + named alternative.
   (*Fully offline clinical notes, $20/mo, vs Heidi at $120/mo requiring cloud PHI.*)
   Examples for other products:
   - Golf AI: *"Swing analysis from your own phone video, trained eye of a former
     pro, $X once — vs a $150/hr lesson you can't rewind."*
   - NZ Law/Visa MCP: *"Current NZ-specific answers with citations to the actual
     Act/INZ instruction, inside the tools people already use — vs generic LLM
     answers that hallucinate NZ law."*
   - Community site: *"The one place [niche] actually checks daily, because the
     data/tools live there — vs a dead Facebook group."*
3. **The boundary:** 3–5 things the product will NEVER do. The boundary is part of
   what the buyer buys. (PRIVATE: no cloud PHI, no "AI" branding, no telemetry.)
4. **The behavior ledger, seeded:** 5–10 dated behavior facts about the user, each
   predicting a specific action (see `fable-domain-lens-portable`). Mine your own
   biography first — it's the dataset nobody else has.

**Gate:** no feature list exists yet. Features are admitted in Phase 1, one at a
time, through the admission test.

### Phase 1 — Scope by admission, not by brainstorm

Run every candidate feature through the admission test (wedge? moment? coherence
cost? five-customer test? kill criteria?). Sort the survivors by **distance from a
stranger paying/using** — trust items (signing, privacy proof, reliability drills)
rank as features, because for a solo maker, *trust is the product*.

**Gate:** the plan doc for the release exists, with a **Current Status block at the
top** (see §E) before implementation starts.

### Phase 2 — Architecture from the registries

Choose the stack, then immediately install the §B–§D defaults into it: the single
typed API/data wrapper, the centralized config module, the status lifecycles, the
guardrail taxonomy, automatic safety. These cost near-zero on day one and are
brutally expensive to retrofit (PRIVATE retrofitted several — encryption chokepoint,
queue durability, always-mounted streaming — each retrofit cost a multi-day plan doc).

### Phase 3 — Build, with the Four Fates

Every feature with an operation >2s answers Wander / Parallel / Switch / Vanish in
its plan before it's built (`fable-user-reality-portable`). Every `disabled` control
passes the Disable test and shows its reason.

### Phase 4 — Verify like production, on the weakest tier

- Dev-vs-prod is a first-class bug category: "why it looked fine in dev" is a
  required heading in every bug log (§E). Packaged builds, installed builds, clean
  machines, real devices — PRIVATE's sharpest bugs (icon, electron-updater strip,
  licence-flash) were all invisible in dev.
- Drills are real: run recovery/restore/revoke flows end-to-end on an actual second
  device, not a thought experiment. A drill that's never been run is a trust bomb.
- Build **dev-reset paths** early so testing never requires nuking data (reset one
  table/key, not the world) — if resetting is painful, you'll test less.

### Phase 5 — Release discipline

A written pre-release checklist, with the automatable items **enforced by the build
script** (PRIVATE's `check:config` pattern: the checklist item that can be a script
IS a script; humans only check what machines can't). Version bumps always; shipped
artifact names/IDs are permanent (§D.7).

### Phase 6 — Post-ship: the journal and the loop

Every production issue → dated journal entry (§E format). Every pilot observation →
the behavior ledger, allowed to overrule your older facts. Every few weeks → a
fable-mode style audit pass on what's drifted.

---

## Part B — Design Style Registry (user-facing)

These are Jonathan's signatures. B1–B4 apply to *anything* with a user surface,
including an MCP server's tool names and error strings.

1. **Name by benefit, never by technology.** "Higher Accuracy", not "Whisper".
   "Better Quality", not the model name. "Support Diagnostic Log", never
   "telemetry". Users buy outcomes; tech names leak implementation, date the
   product, and scare non-technical buyers. (MCP equivalent: tool called
   `check_visa_eligibility`, not `query_inz_rag_pipeline`.)
2. **Plain English everywhere, written for the profession's own vocabulary.** Copy
   is a domain-knowledge deliverable, not filler. Error messages are specific and
   actionable per cause (the mic-error rework: each `getUserMedia` failure type got
   its own instruction), never generic "something went wrong".
3. **Visible state, always.** Status lights, badges, progress, draft counts —
   the user must never wonder "is it doing something?" or "did it save?". Every
   async thing shows its life. (API/MCP equivalent: status fields in every
   response; long jobs return a pollable/streamable state, never silence.)
4. **Honest UI in failure and recovery.** A recovery flow must never *look like*
   data loss when it isn't (the reactivation profile-screen bug was fixed as a
   priority precisely because it looked alarming while being harmless). What things
   look like IS what they are, to the user.
5. **One committed aesthetic, defined once, referenced everywhere.** PRIVATE chose
   glassmorphism; the next product may choose differently — but it chooses ONE
   system (tokens, surfaces, type) in one file/doc, and no screen goes "plain".
   No raw `alert()`/`confirm()` — modal/confirm primitives from the design system,
   promise-based so logic stays clean.
6. **Respect the user's machine and locale.** Dates/times through one centralized,
   locale-aware helper (the foreign-bought-laptop lesson — never call locale
   formatting ad hoc). Text selectable everywhere. Cold start degrades gracefully;
   never optimize a startup wait below the reality of slow disks and AV scans.
7. **Defaults, empty states, and first-run get design attention before features
   do.** The default is what 90% live with; the first 90 seconds is the judgment
   window (the last-minute arriver).

---

## Part C — App Working Preferences (system behavior)

1. **Data ownership first.** The user's data lives where the user controls it
   (local-first when possible). When something must go online, there is an explicit,
   readable statement of exactly what goes and what never does (the Network
   Transparency panel pattern) — transparency is a feature, built for the buyer's
   procurement/trust conversation.
2. **Safety is automatic, never disciplined.** Backups on open/close/save, autosave
   as crash recovery, rolling limits — the user is never expected to remember to be
   safe. Anything that requires discipline will be skipped exactly when it matters.
3. **Everything long-running is durable and interruption-tolerant.** Queues over
   inline processing; state above the leaf component; stuck-state reset on startup
   (a row left `in_progress` at boot is crash evidence, reset it); the app being
   closed mid-operation is a *defined* path, not an exception.
4. **One chokepoint per concern.** One typed API wrapper (endpoint + interface
   defined there before any UI touches it). One config module. One DB connection
   function (which is how encryption-at-rest was added without touching routers).
   One sanitization function at the trust boundary. When a cross-cutting concern
   arrives later, it lands in one place.
5. **Fail closed for security, fail open for the user's own data.** Licence/access
   checks degrade to restriction (`pending`, read-only); but the user's own data
   remains readable in every failure mode. Kill switches live server-side; a natural
   lapse is never presented as punishment (graceful-lapse model).
6. **Support without surveillance.** Diagnostics exist (dated action log, rotation,
   no content/PII, path-scrubbed), stay on-device, and the user sends them by
   choice. Logging is best-effort and may never break the primary action.
7. **Offline answer for every online call.** Each remote dependency has a stated
   offline behavior, decided at design time — cache, degrade, or queue.

---

## Part D — Logic Preferences (data & code patterns)

1. **Explicit status lifecycles, and user edits are sticky.** Every generated/
   processed artifact has a named lifecycle (`not_generated → pending → generated →
   edited → failed`), and once a human edits, the machine never overwrites
   (`edited` is terminal against regeneration). Empty machine output = `failed`,
   never silently "done".
2. **The machine proposes, the human disposes.** Generation is user-triggered,
   never automatic on save/complete. Human-judgment fields (scores, flags,
   assessments) are never machine-set. Every generation has a working Stop
   (AbortController pattern: abort the stream, roll back the in-progress item, keep
   finished ones).
3. **Source is never overwritten by derivation.** The raw input (transcript, notes,
   uploaded file) stays intact so any AI/processing step can be re-run infinitely.
   Re-runnability is the forgiveness feature.
4. **One-shot handoffs.** Cross-page/cross-step state passes via produce → consume →
   delete-on-read keys. Never leave a stale handoff lying around to fire twice.
5. **Migrations are idempotent and self-checking.** Init/migrate is always safe to
   re-run (check-then-alter). Renames of stored data get a migration, not a
   breaking change.
6. **Parse ambiguity in code, not in the storage layer.** If a stored value is a
   display string or loosely-typed, all interpretation happens in application code
   where it can be tested — never in SQL/queries (the `sessions.date` lesson).
7. **Two-layer naming: display names may change, identifiers never do.** UI strings
   are free to evolve ("Executive Workspace"); DB columns, API routes, file names of
   shipped artifacts, model/download filenames are permanent once a user exists
   (renaming orphans data/downloads — the `counselor` spelling and model-filename
   rules).
8. **Strictness where the compiler can catch you.** Strict types, no `any`,
   interfaces defined at the wrapper, typecheck after every change. Cheap
   discipline, compounding payoff.

---

## Part E — Process Discipline (how the work itself runs)

1. **One plan doc per initiative, with a "Current Status" block as the single
   source of truth.** Resume any multi-session effort with a one-line prompt
   pointing at the doc — never re-paste context. When sibling docs accumulate
   (reviews from several models, drafts), explicitly designate ONE doc of record
   and mark the rest superseded.
2. **A dated bug journal with a required format.** Every production-relevant fix
   records: what the user saw · why it was a problem · **why it looked fine in dev
   but failed in production** · root cause · files changed · why the fix works ·
   a repeatable verification checklist. Written in plain English a non-senior
   reviewer could follow. Vague entries ("fixed icon issue") are banned.
3. **Cross-examination over self-belief.** Get independent reviews (different
   models, different people), then *reconcile them yourself* into one prioritized
   plan — never execute a reviewer's list unverified, never let two reviews become
   two competing truths.
4. **Checklists become scripts.** Any release-checklist item a script can verify is
   enforced by the build (`check:config` pattern); the human checklist holds only
   what machines can't check.
5. **Drills on real hardware.** Restore, recovery, revoke, update — each run
   end-to-end on a real second device before a customer exists. "Designed correct"
   and "drilled correct" are different states; only the second counts.
6. **Memory/knowledge protocol.** Decisions, corrections, and behavior facts get
   written where the next session (or next year's you) will find them — dated, with
   provenance, updated when overruled. The biography-ledger, the bug journal, and
   the plan docs are one continuous system: nothing important lives only in a chat.

---

## Part F — Mapping the playbook to other product types

| Registry item | Golf AI analysis app | NZ Law/Visa/Education MCP server | Community site | Mobile transcribe/beautify app |
|---|---|---|---|---|
| The picture (§A0) | Weekend golfer, range bay, 20 balls left, phone propped on bag | Migrant at 11pm mid-application, terrified of a wrong answer | Member checking "did anyone reply" over morning coffee | Practitioner walking between appointments, one thumb free |
| Name by benefit (§B1) | "Swing check", not "pose-estimation model" | `check_visa_options`, not `rag_query`; cite the actual instruction ID | Plain section names the niche uses | "Tidy my notes", not "LLM beautify" |
| Visible state (§B3) | Analysis progress per video; confidence shown honestly | Every answer carries source + currency date ("as at INZ instructions of …") | Unread/replied state that never lies | Recording/transcribing/queued badges |
| Data ownership (§C1) | Videos stay on device; opt-in per-upload | Queries not retained; say so in the tool description | Members can export their content | Audio on device; queue durable; nothing uploads silently |
| Guardrails (Four Fates) | Record next swing while previous analyzes (Absorb) | Concurrent tool calls safe; long lookups streamable | Draft post survives navigation | Record during transcribe; switch clients mid-flow; lid close = resume |
| Sticky human edits (§D1) | Coach's manual annotation beats re-analysis | A human-verified answer never silently regenerated | Moderator edits stick | Edited note never clobbered by re-beautify |
| Wrong answers are the failure mode | Bad drill advice → say confidence, show the frame it saw | **Hallucinated law is the product killer** — no citation, no answer; currency date mandatory | Misattributed content | Wrong-speaker/garbled text marked, not hidden |
| Drills (§E5) | Real range video, mid-range Android, bad light | Adversarial question drill vs the actual Act, monthly re-currency check | Load + moderation drill | Real commute audio, old phone, interrupted calls |

The registries don't change across the table — only the nouns do. That's the point:
this is a *system*, and the product is a parameter.

---

## Part G — Day-one checklist for any new project

```markdown
[ ] Copy this playbook into the new repo's plan folder.
[ ] Copy the three portable FABLE skills into .claude/skills/.
[ ] Phase 0 written: picture, wedge, boundary, seeded behavior ledger (dated).
[ ] Feature candidates run through the admission test; sorted by
    distance-from-a-stranger-paying; kill criteria attached.
[ ] Chokepoints scaffolded: one API/data wrapper, one config module, one
    storage-access function, one trust-boundary sanitizer (as applicable).
[ ] Status-lifecycle + sticky-edit pattern decided for every generated artifact.
[ ] Four Fates answered for every operation >2s in the first release's plan.
[ ] Bug journal folder created with the required-format README (copy 000-NotesInHere.md).
[ ] Pre-release checklist started; each automatable item becomes a build-script gate.
[ ] Dev-reset paths built alongside the first feature, not after.
[ ] The first drill (restore/recovery/whatever "trust bomb" this product has)
    scheduled before the first external user.
```

---

**Bottom line:** the transferable asset isn't PRIVATE's code — it's this compound
habit: *big picture first, features admitted not brainstormed, behavior facts over
stereotypes, interruption-tolerance as law, one chokepoint per concern, human edits
sticky, safety automatic, checklists as scripts, drills on real hardware, and a
written trail (plan docs + bug journal + ledger) that lets any future session pick up
exactly where you left off.* Point this at golf, law, community, or mobile and the
nouns change; the system doesn't.
