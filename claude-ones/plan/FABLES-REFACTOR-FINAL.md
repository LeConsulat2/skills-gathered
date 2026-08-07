# FABLE 5 — Final Refactor Decision (2026-07-02 · re-reviewed 2026-07-19)

**No application code was changed while producing or updating this document.** This is
the reviewed, finalized position on the structural refactor proposed in
`CODEX-REFACTOR-SUGGEST.md`, read together with the performance initiative
(`CODEX-SONNET5-CHECKLIST.md`, `CODEX-REIVEW-SONNET5-AFTER-OPUS.md`, `CODEX-FABLE5-REVIEW.md`).

**Update 2026-07-19:** `CODEX-REFACTOR-SUGGEST.md` was rewritten by CODEX SOL 5.6 MAX —
its top section is now a "2026-07-19 Authoritative Review And Execution Amendment"
(Gate Zero + Milestones 2–8), and the 2026-06-30 plan this file originally reviewed was
demoted to a historical appendix inside the same file. I re-verified the amendment's
load-bearing claims against the current source (every one held — see §6) and adopted it
as the execution playbook. §7 is the new tri-state execution checklist — the live
tracker for this whole program. Sections 1–5 are the original 2026-07-02 decision,
kept intact with dated annotations rather than rewritten.

**One-line verdict (unchanged): the CODEX refactor plan is approved — direction,
phasing, invariants, and the first-five-PRs order — but it is gated hard behind the
performance initiative, and it inherits the perf-era invariants recorded in §3.**

**Precedence chain (2026-07-19):**
1. **This file** — the decision layer. Where any doc disagrees, this file wins.
2. **CODEX-REFACTOR-SUGGEST.md, 2026-07-19 amendment** — the detailed execution
   playbook (Gate Zero items, per-milestone file orders, per-PR verification rules).
3. **CODEX-REFACTOR-SUGGEST.md, 2026-06-30 appendix** — rationale/history only.
   Never execute from it; it contains at least one reversed instruction (§6 R3).

---

## 1. The Gate — when the refactor is allowed to start

Jonathan's explicit sequencing call: **the refactor begins only once the performance
feature 100% works.** "100% works" means ALL of the following, not just "code landed":

1. **The speed checklist is functionally complete through Phase 8** (the honest reality
   check) — every phase either done or explicitly descoped with a written decision.
   Phases 9–10 (Fast Mode, workflow glue) may be deliberately deferred, but that deferral
   must be written into the checklist, not left ambiguous.
2. **The result is shipped in a real clinical build** (`npm run dist:clinical`, version
   bumped, full Pre-Release Checklist) and has passed the **installed-build smoke test**
   — dev-mode success is not enough, per the standing rule.
3. **The measured numbers are written down** in the checklist (Phase 8's "actual achieved
   numbers, honestly") so the refactor has a durable "before" state to protect. Any
   regression during refactoring must be checkable against those numbers.
4. **Jonathan explicitly says go.** The `performance-optimization` branch merging to
   `main` is his call; the refactor never starts on a branch that still carries unmerged
   perf work.

> **2026-07-19 annotation:** the CODEX amendment expands these four conditions into a
> nine-item **Gate Zero** (adding: manual runtime verification of every newer behavior
> carried on the same branch; a recorded snapshot of final tuning values and the
> dependency lock; a fresh refactor branch cut from the exact accepted commit; and a
> pre-gate reliability fix for the Whisper lock-coverage gap I confirmed in §6 V1).
> **Adopted.** The four conditions above remain the spirit; the operative pre-refactor
> gate is now the §7.0 checklist block. The Whisper-lock fix is permitted before the
> gate under this section's existing carve-out — it is a bug fix, not a refactor.

Until the gate is fully green: no `src/shared/`, no `src/features/`, no backend package
moves, no doc-alignment pass. The only structural work permitted before the gate is what
the perf checklist itself already requires (e.g., Phase 1.5's sync-`def` endpoint fix —
which is a bug fix, not a refactor).

**Why the gate is right (not just cautious):** the perf work and the refactor touch the
same hot files — `backend/services/ai.py`, `backend/routers/transcribe.py`,
`backend/routers/audio_queue.py`, `backend/services/whisper_service.py`,
`backend/routers/sessions.py`, `src/pages/SessionsPage.tsx`. Running a structural
migration underneath an active benchmarking effort would make every perf measurement
unattributable (violating the checklist's own "one lever per change" rule) and every
refactor diff noisy. Sequential is the only sane order, and perf-first is correct because
it's the customer-facing problem (the 10–15 minute window) while the refactor is
maintainability investment.

---

## 2. Verdict on the CODEX plan — approved, with these confirmations

*(Written 2026-07-02 against the 2026-06-30 plan; the judgments below carry forward
unchanged into the 2026-07-19 amendment, which restates all of them.)*

- **Contract-first is the right model.** The plan's core insight — that the main risk is
  behavior drift, not file size — matches this repo's actual bug history (licence flash,
  spinner regression, autosave clobber, first-run banner). Phase 0 (characterization
  tests + baseline commands) before any file move is non-negotiable.
- **The "First Five PRs" order is correct and is adopted as-is:**
  1. Safety/contract baseline (tests + gates, no behavior change)
  2. Shared storage keys + one-shot handoff helpers (`src/shared/storage/`)
  3. Shared API client split (`src/utils/api.ts` stays as facade)
  4. App startup hooks extraction from `App.tsx`
  5. Sessions autosave + handoffs extraction (JSX stays put initially)

  > **2026-07-19:** the amendment renumbers these as Phase 0 (PRs 1A–1E) and
  > Milestones 2–5, and expands each with lettered sub-steps. The order is identical.
  > Amendment numbering is now canonical — see §7.
- **The Non-Negotiable Invariants section is adopted wholesale** (packaging/NSIS,
  startup/auto-login, workspace lock/423, licence axes, device-transfer slot modes,
  DB chokepoint, backup format, AI/privacy boundaries). Treat every bullet there as a
  test case, exactly as written. *(2026-07-19: the amendment's "Updated Non-Negotiable
  Invariants" is the authoritative phrasing now — it absorbs the perf-era invariants
  from §3 below, including keep-awake, powerSaveBlocker ref-counting, All-at-Once's
  two-stage state machine, bulk-group beautify rules, and Key Terms chokepoints.)*
- **The "What Not To Do" list is adopted wholesale**, especially: never split
  `database.py` before encrypted/locked/restored/migrated/fresh DB tests exist; never
  mix file moves with behavior changes in one PR; never let feature components grow raw
  `fetch()` calls.
- **Target trees (frontend `src/app` + `src/shared` + `src/features`, backend `core/` +
  `db/` + package-per-service) are adopted as the destination**, reached gradually with
  re-export shims — never in one PR.
- **The dual-workspace code stays.** The packaged product is clinical-forced, but the
  meetings workspace is live product surface, not dead code. No refactor PR deletes or
  "simplifies away" the meetings path without an explicit product decision from Jonathan.

---

## 3. Invariants the perf initiative adds (the delta the 2026-06-30 plan couldn't see)

By the time the gate opens, the following exist in the code and **must be in the
refactor's Phase 0 test list** — they are the freshest, least-documented code in the
repo and therefore the most likely to be silently dropped during a package move.
*(2026-07-19: landed-status re-verified against source; stamps below.)*

### 3.1 Landed and re-verified 2026-07-19

- **Beautify SSE instrumentation contract:** `_ensure_server()` returns a bool
  (cold/warm); `_chat`/`_chat_stream` accept an optional `capture_stats` dict;
  `beautify_notes_stream` fills it; `routers/sessions.py` reads it and writes
  `cold_start`, `ttft_ms`, `completion_tokens`, `prompt_tokens`, `reasoning_chars` onto
  the `beautify-single` activity-log row. When `ai.py` is split, **this stats plumbing
  must survive intact** — it is the app's only performance telemetry. The fields are
  numbers/flags only (no PHI); the split must not widen them.
  *Re-verified: `ai.py:371–421` (capture helpers), `:441+` (`_chat_stream` param),
  `:688–691`, `:958–978`.*
- **`stream_options: {"include_usage": true}`** on the streamed llama-server request —
  purely additive, must not be lost when request-building moves.
  *Re-verified: `ai.py:467`.*
- **Transcribe-path instrumentation** (`model_size`, `beam_size`, `cold_start`,
  `model_load_ms`, `decode_ms`, `audio_duration_s`, `rtf`, `cpu_threads`,
  `on_ac_power`) on transcribe/audio-queue activity-log rows — same PHI-free rule.
  *Re-verified: `transcribe.py:139–143`, `audio_queue.py:511–515`, `:1245–1248`.*
- **llama-server spawn flags:** `-t -1`, `-tb -1`, `--reasoning auto` — measured,
  benchmarked decisions living in the spawn `args` list. The refactor moves them
  **byte-for-byte** and must not "clean up" flags it doesn't recognize.
  *Re-verified: `ai.py:82–93` (constants), `:292–297` (args).*
- **Whisper `CPU_THREADS = 8`** — same byte-for-byte rule.
  *Re-verified: `whisper_service.py:36`. Note: the comment block above it
  (`whisper_service.py:30–35`) still says "0 = library default / not yet tuned" — stale
  relative to the value. Two-line comment fix; belongs to perf-initiative housekeeping
  or the doc-alignment milestone, never a refactor PR.*
- **Revised token-budget formula** (`reasoning_est` term).
  *Re-verified: `ai.py:974–975`.*
- **`faster-whisper==1.2.1` exact pin.** *Re-verified: `requirements.txt:3`.*
  ⚠️ **The pinned transitive deps (`ctranslate2`, `av`, `onnxruntime`) called for by
  `CODEX-FABLE5-REVIEW.md` §9 are NOT in `requirements.txt` as of 2026-07-19** — this
  must be resolved (pin them, or record a written descope) at Gate Zero item G0.2.
  Refactor PRs never float any of these either way.
- **Phase 1.5 sync-`def` + `TRANSCRIBE_LOCK`:** the inline path is correct — the lock
  is taken **before** model load (`transcribe.py:91–93`), matching the stated invariant
  that the lock covers model-load + the full lazy segment iteration
  (`whisper_service.py:24–28`). **However, three `audio_queue.py` paths violate it** —
  see §6 V1. Fixing that is Gate Zero item G0.9, a pre-gate reliability PR. Once fixed,
  the refactor preserves the resulting one-owner/one-lock contract exactly — the single
  easiest thing for a router split to accidentally undo (someone "tidies" a `def` back
  to `async def`, or hoists a model load out of the lock again).

### 3.2 Check tick state at gate time (not re-verified this pass)

- **Phase 2 warm-engine logic (if built):** RAM-aware pre-warm + idle shutdown with
  guardrails (never during first-launch/licence/cover screens). If it exists at gate
  time, it joins the startup-sequencing invariants in Milestone 4's test list.
- **Phase 10 glue (if built):** the opt-in "Beautify automatically when this
  transcription finishes" checkbox (default OFF, snapshot-before-start, respects the
  workspace lock) and any `BATCH_MAX` change. Milestone 6 must carry these as explicit
  behaviors, not rediscover them.
- **Reasoning A/B outcome:** the observed value is `--reasoning auto`; whether that is
  the accepted final answer or the A/B is still open must be read from the speed
  checklist at gate time, then snapshotted (G0.2).

### 3.3 One standing rule for the whole refactor

**Re-run the Phase 8 baseline after each refactor phase that touches an AI/transcribe
path.** A structural refactor must be performance-neutral; the instrumentation built in
perf Phase 1 makes this a five-minute check (compare `ttft_ms` / `decode_ms` / total on
the same fixed non-PHI input) instead of a guess. Any regression >10% on the reference
machine blocks the refactor PR until explained.

---

## 4. Final execution order (the whole program, both initiatives)

> **2026-07-19:** renumbered to the amendment's scheme; the §7 checklist is the live
> tracker. Mapping from this file's old labels: REFACTOR 1 → Phase 0 (PRs 1A–1E),
> REFACTOR 2 → Milestones 2–3, REFACTOR 3 → Milestone 4, REFACTOR 4 → Milestone 5,
> REFACTOR 5 → Milestones 6–7, REFACTOR 6 → Milestone 8, REFACTOR 7 → doc alignment.

```text
NOW → GATE:   Performance initiative only, on branch performance-optimization,
              in the agreed order (checklist "Current Status" §Agreed execution order),
              PLUS the Gate Zero additions: manual runtime verification of the
              branch's newer behaviors, the G0.9 Whisper-lock reliability fix,
              tuning-value + dependency-lock snapshot, honest Phase 8 re-measure,
              ship, installed smoke test.

GATE (G0):    All §7.0 items [x]. Jonathan says go. Perf branch merged to main.
              Fresh refactor branch cut from the exact accepted commit.
              Baseline snapshot archived.

Phase 0:      Safety + characterization baseline (PRs 1A–1E), INCLUDING the §3 perf
              invariants (instrumentation fields, lock/sync-def behavior, spawn
              flags, pins) as test cases.
Milestone 2:  Shared storage keys + one-shot handoffs (2A–2D).
Milestone 3:  Shared API transport with facade (3A–3D).
Milestone 4:  App shell + lifecycle hooks (4A–4F).
Milestone 5:  Sessions autosave + handoffs (5A–5C; no JSX moves).
Milestone 6:  Remaining Sessions split (6A–6J; JSX panels last).
Milestone 7:  Remaining frontend, one feature at a time (Settings → bulk modal →
              Meetings → Home → Calendar → Client History → VOR/Docs → Help).
Milestone 8:  Backend split in risk order: system.py → exporters.py → ai.py →
              audio_queue.py → backups.py → license.py → database.py LAST,
              then main.py/config.py.
Final:        Documentation alignment (CLAUDE.md, .claude/commands, SMOKE_TEST.md,
              fold perf-era outcomes into LocalAIStack.md) and mark
              CODEX-REVIEW*.md / CODEX-REFACTOR-SUGGEST.md / the perf checklist /
              this file's execution sections archived-complete.
```

Every refactor step keeps the standing quality gates: `npm run check:config`,
`npx tsc --noEmit`, `npm run build:clinical`, backend security suite, and the installed
clinical smoke test for anything touching Electron/startup/licence/lock/storage/backup/
audio — plus the §3.3 performance-neutrality check. The amendment's "Per-PR Verification
And Stop Rules" section is the operative detail for all of these; its **Immediate Stop
Conditions** list is adopted verbatim.

---

## 5. Explicitly out of scope for the refactor

Carried over from CODEX's "What Not To Do" and reaffirmed with the perf context:

- No behavior changes, renames of wire vocabulary (`active`/`pending`, licence statuses),
  model/mmproj filename changes, or NSIS/packaging changes inside refactor PRs.
- No touching the perf-landed spawn flags, pins, locks, or instrumentation except to
  relocate them verbatim.
- No parallel transcription/Beautify "while we're in there" — that was evaluated and
  rejected in the perf initiative (CPU-bound, race-prone); the refactor doesn't reopen it.
- No starting `database.py` or `license.py` splits before their characterization tests
  exist, no matter how far along the rest of the refactor is.
- No broad cleanup/formatting PRs mixed with file moves.
- *(2026-07-19, from the amendment — adopted:)* no new migration registry/schema-version
  framework inside this program (reverses the 2026-06-30 appendix — see §6 R3); no
  dependency/model/binary upgrades; no new performance flags, Fast Mode, or `BATCH_MAX`
  change; no security hardening that changes behavior without its own authorized PR
  (the amendment's "Security Follow-Ups" list — query-token downloads, licence-key
  exposure in status responses, hostile-archive tests, Electron surface tests — stays
  parked as separate future work, exactly as it says).

---

## 6. Re-review of the 2026-07-19 CODEX SOL 5.6 MAX amendment

**Verdict: adopted as the execution playbook.** The amendment is a faithful superset of
this file's 2026-07-02 decision — it independently arrives at the same gate ("the
execution gate is not open today"), keeps the first-five order and the backend risk
order byte-for-byte, absorbs every §3 perf invariant into its invariant list, and adds
genuinely new material (Gate Zero items 3/8/9, the baseline snapshot, per-PR stop rules,
a route-policy test table). Nothing in it contradicts this file's decision layer.

### 6.1 Verification of its load-bearing claims (all checked against source 2026-07-19)

| # | Amendment claim | My check | Status |
|---|---|---|---|
| V1 | Three `audio_queue.py` paths call `get_whisper_model()` **before** entering `TRANSCRIBE_LOCK`, violating the stated hold-across-load invariant | Counsellor bulk: load `audio_queue.py:262`, lock `:328`. Meetings bulk: load `:923`, lock `:983`. Per-item retained: load `:1185`, lock `:1203`. Inline path is correct (`transcribe.py:91–93` loads **inside** the lock). Invariant stated at `whisper_service.py:24–28` | **CONFIRMED** |
| V2 | Working-tree tuning values: Whisper threads 8, llama `-t`/`-tb` = −1, reasoning `auto`, `faster-whisper==1.2.1` | `whisper_service.py:36`; `ai.py:82,83,93,292–297`; `requirements.txt:3` | **CONFIRMED** |
| V3 | Current line counts (SessionsPage 7,533; exporters 4,057; SettingsPage 2,392; api.ts 2,058; ai.py 1,631; App.tsx 1,446; database.py 1,314; system.py 1,307; audio_queue.py 1,278; license.py 1,223) | `wc -l` on all ten files | **CONFIRMED — exact match** |
| V4 | Direct `fetch()` calls exist outside the generic helper | 8 outside `api.ts`: ReportPage ×3, SessionsPage ×3, SettingsPage ×1, VisualObservationRecordView ×1 (`api.ts` itself: 18) | **CONFIRMED** |
| V5 | Repo still on `performance-optimization`; ship gates open | Branch confirmed; perf checklist + memory show Phase 8 / installed-smoke / several manual verifications open | **CONFIRMED** |
| V6 | §3.1 instrumentation contracts still intact (implicit — the amendment requires preserving them) | `ai.py:371–421,441,467,974–975`; `transcribe.py:139–143`; `audio_queue.py:511–515,1245–1248` | **CONFIRMED** |

**V1 failure scenario (why G0.9 is a real pre-gate item, not pedantry):**
`get_whisper_model()` mutates the module-global cached model (`_whisper_model`,
`_loaded_model_size`) when the requested size differs. Called unlocked from a bulk
worker while an inline decode holds `TRANSCRIBE_LOCK` mid-iteration, it can swap/reload
the global under a live decode — the in-flight decode keeps its local reference (no
immediate crash), but two multi-hundred-MB models end up resident at once on the weak
RAM tier, and two unlocked bulk workers (counsellor + meetings) can race the global
mutation itself. Bounded blast radius, but it directly contradicts the invariant the
refactor is supposed to freeze — so it must be fixed (or explicitly redesigned) in a
separate reliability PR **before** the baseline is frozen, exactly as the amendment says.
Do not hide the fix inside the later audio-queue refactor.

### 6.2 Deltas this re-review adds on top of the amendment

- **D1 — transitive pins absent:** `ctranslate2` / `av` / `onnxruntime` are not pinned
  in `requirements.txt` (checked 2026-07-19), despite `CODEX-FABLE5-REVIEW.md` §9. The
  amendment's G0.2 ("resolve and record final shipped values… and dependency lock")
  covers this implicitly; recording it here makes it explicit — pin them or write the
  descope, at gate time.
- **D2 — stale `CPU_THREADS` comment:** `whisper_service.py:30–35` still describes the
  pre-tuning state ("0 = library default… not yet tuned") above `CPU_THREADS = 8`.
  Two-line comment fix; perf-initiative housekeeping, never a refactor PR.

### 6.3 Rulings (stamped 2026-07-19)

- **R1 — ADOPTED:** the amendment's Gate Zero (nine items + baseline snapshot) replaces
  this file's four-condition gate as the *operative* gate; the four conditions remain
  the intent. Tracked as §7.0.
- **R2 — ADOPTED:** amendment milestone numbering (Phase 0, Milestones 2–8) is
  canonical; this file's REFACTOR 1–7 labels are retired (mapping in §4).
- **R3 — ADOPTED (reversal of the 2026-06-30 appendix):** **no migration registry** or
  schema-version framework is added anywhere in this program. The appendix's
  "add a small migration registry" instruction is void; preserve the current idempotent
  `PRAGMA`-guarded migration behavior exactly. A migration framework is a separate,
  later initiative.
- **R4 — ADOPTED:** the G0.9 Whisper-lock fix is authorized pre-gate under §1's
  existing bug-fix carve-out, as its own reliability PR with its own verification —
  and re-verified as still-fixed when the baseline snapshot is taken.
- **R5 — CONFIRMED:** the amendment's "Security Follow-Ups" are parked, not smuggled
  into refactor PRs (§5). Its "Explicitly Out Of Scope" list is adopted wholesale.

---

## 7. Tri-state execution checklist (the live tracker)

**Legend:** `[ ]` not started · `[~]` in progress / partially done · `[x]` done **and
verified** (never tick on "code landed" alone). When ticking, append a date and an
evidence pointer (commit SHA, test-run note, or measurement doc) — chat is not the
record. Do not start a numbered block until every item in the previous block is `[x]`
(lettered items inside a block are sequential too, unless marked otherwise).
Every production-code item additionally carries the standing per-PR gates (§4 closing
paragraph) and, where it touches AI/transcription, the §3.3 performance-neutrality check.

### 7.0 Gate Zero — refactor NOT authorized until every item is [x]

- [~] **G0.1** Performance initiative functionally complete through Phase 8 — every
      phase done or explicitly descoped in writing in the speed checklist
      *(in progress on `performance-optimization`; Phase 8 re-measure still open)*
- [ ] **G0.2** Final shipped tuning values + dependency lock resolved and recorded from
      accepted source (llama flags, `CPU_THREADS`, reasoning decision, `faster-whisper`
      pin **and the D1 transitive-pin decision**; snapshot values, don't infer from plans)
- [~] **G0.3** Manual runtime checks complete for every newer behavior on the branch:
  - [ ] live recording + backend keep-awake behavior
  - [ ] single Transcribe-&-Beautify (All-at-Once): navigation, Stop, retained-queue,
        close-confirm, template confirmation *(known open: live E2E untested)*
  - [ ] bulk Transcribe / bulk Transcribe-&-Beautify: selection, grouping, Stop,
        partial/failure, restart recovery, friendly labels, global disabling,
        completion acknowledgement
  - [ ] Key Terms capture/fresh-resolution + no-term-text diagnostic audit
        *(known open: manual click-through)*
  - [ ] meeting-summary streaming/progress
  - [ ] hard revoke/reactivation + exact allow-list behavior
        *(known open: live second-device drill)*
  - [ ] loading states on a slower/representative machine
- [ ] **G0.4** Final paired non-PHI performance measurements written down: reference
      machine, fixture identity/hash, power state, cold/warm, medians, accepted variance
- [ ] **G0.5** Real clinical installer built (full Pre-Release Checklist) + installed-
      build smoke test passed
- [ ] **G0.6** `performance-optimization` merged to `main` with Jonathan's approval
- [ ] **G0.7** Jonathan's explicit refactor go-ahead recorded, with the exact baseline
      commit SHA
- [ ] **G0.8** Fresh refactor branch cut from that exact commit, clean worktree
- [ ] **G0.9** Whisper lock-coverage fix (§6 V1): model load brought under
      `TRANSCRIBE_LOCK` (or explicitly redesigned) for counsellor-bulk, meetings-bulk,
      and per-item paths — separate reliability PR, verified, before baseline freeze
- [ ] **G0.10** Baseline snapshot archived from the accepted commit (per the amendment's
      "Baseline Snapshot" section: SHA/versions, lockfile + requirements + builder-config
      hashes, storage-key inventory, method/path route list, middleware order +
      allow-lists, public exports of api.ts / ai.py / exporters.py / database.py, DB
      schema inventory from a throwaway fixture, file-size inventory, final perf numbers
      + diagnostic field names — **no PHI, keys, fingerprints, tokens, or customer paths**)

### 7.1 Phase 0 — safety & characterization baseline (Milestone 1)

- [ ] **1A** Test runner + isolation only (pinned dev-only deps; temp-dir redirection
      before backend imports; no real-DB discovery; document-upload + DOCX-sanitization
      tests wired into an explicit command; no production source movement)
- [ ] **1B** Route + security contract suite (method/path snapshot, docs disabled,
      local-token cases, 423 + allow-list, revoked 403 + exact exceptions, middleware
      order, CORS, licence gates, meeting sanitization; route-policy test table)
- [ ] **1C** Frontend protocol contract (token header/query per transport, 423 event +
      deferred saves, revoked-vs-ordinary 403, storage-key spellings + one-shot
      semantics, verify-trigger lifecycle + no-interval assertion, auto-login/cover
      ordering, always-mounted pages; **inventory all 8 direct fetches** — §6 V4)
- [ ] **1D** High-risk workflow fixtures (autosave shapes, handoffs, async origin
      targeting, cancellation, transcription concurrency incl. the G0.9 contract, bulk
      audio, Key Terms, AI spawn/auth/switch/drain, semantic export fixtures,
      backup/restore incl. wrong-key + corrupt archive, database matrix, licence matrix)
- [ ] **1E** Performance + installed baseline archived (baseline commands run + recorded;
      accepted fixed perf fixtures; installed clinical smoke matrix; no tuning)

### 7.2 Milestone 2 — shared storage keys & handoffs

- [ ] **2A** Define contracts without replacing callers (`src/shared/storage/keys.ts`,
      `handoffs.ts`, `preferences.ts`, `autosaveKeys.ts` — exact current strings, typed
      builders, zero renames/expiry/versioning)
- [ ] **2B** Migrate one-shot session producers→consumers, one protocol family at a
      time (HomeDashboard → ClientHistoryPanel → ClientsPage → SessionsPage; prove
      consume-once + removal timing unchanged per family)
- [ ] **2C** Migrate meetings + app/move UX (HomeDashboard meeting producers →
      MeetingDashboard → SettingsPage move producer → SelectionPage → App.tsx;
      move-state stays UX-only, never authorization)
- [ ] **2D** Autosave key builders + preferences last (no generic object store)

### 7.3 Milestone 3 — shared API transport with facade

- [ ] **3A** Extract response policy first (`base.ts`, `requestJson.ts`, `errors.ts`,
      `events.ts`; one owner for token/headers/423/revoked-shape/unreachable mapping;
      FormData must not gain a JSON content type)
- [ ] **3B** Extract non-JSON transports (`formData.ts`, `downloadBlob.ts`,
      `eventStream.ts`, `streamingPost.ts`; preserve AbortSignal, headers, filename
      parsing, SSE framing, token placement)
- [ ] **3C** Split domain APIs in low-risk order (health/model → settings/profile/
      templates → calendar/analytics → clients/docs/VOR → meetings → sessions/reporting/
      exports → licensing/security → audio queue/streaming; `src/utils/api.ts` stays
      the import-compatible facade throughout)
- [ ] **3D** Direct-fetch audit: replace the 8 component-level fetches with the tested
      primitives one workflow at a time (no query→header token change inside these PRs)

### 7.4 Milestone 4 — App shell & lifecycle

- [ ] **4A** Pure types + helpers (Electron bridge declaration, `semverLt`, sidebar
      config; no listener/effect movement)
- [ ] **4B** Electron lifecycle + busy bridge (update events, backup-starting,
      recording-flush, close-confirm, window state, busy aggregation, OS-resume;
      mount-once listeners preserved)
- [ ] **4C** Workspace security unit (PIN init, 423 listener, shortcut, idle timer,
      lock overlay state, unlock rehydration; overlay stays top-level, not a route)
- [ ] **4D** Startup coordinator (backend health, security wait, auto-login, profile
      requirement, cover resolution incl. 60s fallback + 20s escape, startup backup,
      initial hydration — ONE coordinator; tests cover ordering, not just final state)
- [ ] **4E** Licence lifecycle unit (event-driven verify, in-flight guard, cooldown
      rules, listener registration, local SSE relay, expiry/blocked/revoked/min-version
      derivations, device-transfer state; **assert no interval exists**)
- [ ] **4F** Presentational shell last (title bar, sidebar, banners, cover, tab
      composition; always-mounted hidden pages exactly preserved)

### 7.5 Milestone 5 — Sessions autosave & handoffs (no JSX moves)

- [ ] **5A** Pure autosave schema (key selection, serialization, legacy normalization,
      DB-authoritative field merge with an explicit maintained field list, empty/corrupt
      decisions; fixture per current field)
- [ ] **5B** Handoff hook (consume-on-active-tab; page-stays-mounted, re-check on
      activation, exact consumption timing, reporting highlight/scroll, catch-up
      identity, selection ordering)
- [ ] **5C** Autosave lifecycle hook (debounce, immediate/unmount flush, DB draft
      create/reconnect, walk-in, suppress-unsaved guards; page keeps owning API +
      selected-session state initially)

### 7.6 Milestone 6 — remaining Sessions split (facade component throughout)

- [ ] **6A** Pure editor + metadata (word count/dates, legacy conversion, MD↔HTML,
      `BeautifiedEditor`, normalization, template/schema resolution + match guard)
- [ ] **6B** Client/session/draft lifecycle (selection, all-drafts, walk-in,
      attach/change, create/reconnect, delete/discard, return-to-draft; preserve the
      order pending-audio/autosave/selection/unsaved flags change in)
- [ ] **6C** Recording capture (MediaRecorder + mic/system composition, timer, exit
      flush, Electron recording protection — one lifecycle owner; pending-audio cache
      into one dedicated module, not context)
- [ ] **6D** Single transcription (job ID, AbortController, cooperative cancel,
      progress cleanup, start-time snapshot, retained-item path; discriminated outcome,
      no truthy shortcuts)
- [ ] **6E** Single beautify + background detach (template resolution, run target,
      stream parser, ETA, Stop, detach, origin save, partial rollback, stale-session
      avoidance, deferred 423 save; save payload = intended fields only, never a stale
      spread)
- [ ] **6F** All-at-Once orchestrator (two-stage state machine with explicit
      transitions; no mid-run modal; template/overwrite decided before Start; per-stage
      durable artifacts on cancel/failure) — only after 6D + 6E stable
- [ ] **6G** Batch beautify (queue selection/order, per-row template, cap, ETA, abort,
      per-item progress, origin/deferred saves, diagnostics; nothing preselected)
- [ ] **6H** Bulk-audio background observer (standing watchdog + tighter poll,
      global-disable derivation, counters, OS notification, body-portal toast; test
      after long-mounted-page uptime) — separate from 6G
- [ ] **6I** Reporting, take-away, catch-up, exports (in order: reporting gen/abort →
      summary save + mark-logged → take-away gen → take-home export → clinical record
      export + template mismatch; practitioner-triggered rules preserved)
- [ ] **6J** JSX panels last (SessionRail, SessionHeader, SourcePanel,
      StructuredNotePanel, ReportingPanel, TakeAwayPanel, AudioPanel,
      BatchBeautifyDialog, RunCompletionToast; panels get data + commands only)

### 7.7 Milestone 7 — remaining frontend, one feature at a time

- [ ] **7.1** `SettingsPage.tsx` (panel order: profile/signature → locale/startup →
      client-ID → categories → templates/export → AI/transcription models → Key Terms →
      privacy/paths/diagnostics → PIN/security → subscription/transfer → purge LAST;
      extra security tests on panels 8–11; parent-owned Save All until proven)
- [ ] **7.2** `BulkAudioUploadModal.tsx` (pure labels/grouping/validation/phases first;
      one controller owns selection/polling/start/Stop — never one poller per phase)
- [ ] **7.3** `MeetingDashboard.tsx` (mirror low-level primitives only; sanitization,
      licence gate, queue-all semantics stay meetings-specific)
- [ ] **7.4** `HomeDashboard.tsx` (independent cards after handoffs/APIs centralized;
      parallel-load fallback semantics preserved)
- [ ] **7.5** `ClinicalScheduler.tsx` (calendar CRUD/import/catch-up + `logged_at` as
      contract boundaries)
- [ ] **7.6** `ClientHistoryPanel.tsx` (history/exports/documents/observations/handoffs)
- [ ] **7.7** `VisualObservationRecordView.tsx` + `DocumentDetailView.tsx`
- [ ] **7.8** `HelpPage.tsx` content/data last (only if maintainability actually gains)

### 7.8 Milestone 8 — backend split in risk order

- [ ] **8A** `routers/system.py` → facade router + subrouters (group order: health/
      encryption-status → local events → model SSE → Whisper → diagnostics →
      settings/categories → analytics/reporting → insights → backup wrappers →
      purge/admin LAST; per group compare method/path/order/response/gates/execution
      mode — sync must not become async for style)
- [ ] **8B** `services/exporters.py` → package behind facade (cleanup lifecycle → pure
      normalization → DOCX primitives → PDF primitives → org-template fill → meetings →
      sessions → take-home → VOR → dossier → XLSX; semantic golden fixtures each move,
      never whole-byte compares; preserve lazy imports)
- [ ] **8C** `services/ai.py` → prompts/parsing/vision-prep first, then ONE `engine.py`
      owning process/lock/identities/key/spawn/drains/HTTP, then capability services
      (meeting summary → template mapping → beautify → holistic → reporting digest →
      take-away → legacy drawing → VOR), then thin facade; never from-import a mutable
      runtime global; §3.1 stats plumbing survives intact; perf baseline after each step
- [ ] **8D** `routers/audio_queue.py` (do NOT dedupe counsellor/meetings workers first;
      repository → encrypted storage adapter → preflight → per-workspace state/lock
      owner → shared low-level decode helper (text/progress/stats only, never chooses
      the writer) → counsellor writer → meetings writer → per-item → thin routes;
      workspace can never default across writers; G0.9 contract preserved exactly)
- [ ] **8E** `services/backups.py` (after full restore fixtures: constants/path
      validation → password/format → manifest → validation → compile/retention →
      restore prep → atomic replace/key recovery → purge LAST; failure injection
      before/during/after replacement; never the live DB)
- [ ] **8F** `routers/license.py` (after full licence matrix: models/day-math →
      fingerprint trust → slot mode → local cache → web client → Supabase fallback →
      recovery unlock → diagnostic dedupe → thin router LAST; verify stays one policy
      service until all branches have parity tests; never collapse the status axes)
- [ ] **8G** `database.py` LAST (internal refactor in-module first — name sections,
      keep globals in place, prove parity on every fixture — then move to `backend/db/`
      behind a facade; no registry, no transaction/DDL/seed/fail-open/key-ownership
      changes)
- [ ] **8H** `main.py` / `config.py` (middleware moves only with order-proving contract
      suite; router inclusion stays explicit; config largely intact)

### 7.9 Final — documentation alignment & archive

- [ ] **9.1** Doc alignment pass (CLAUDE.md, `.claude/commands/*`, SMOKE_TEST.md,
      DataModel/LocalAIStack/RouterReference/ExportEngine; fix known stale items:
      domain spelling, Exit Portal → Restart App, mmproj vision-only, telemetry →
      Support Diagnostic Log, D2 comment; record final paths/commands/test matrix/perf
      results)
- [ ] **9.2** Mark archived-complete: `CODEX-REFACTOR-SUGGEST.md`, `CODEX-REVIEW*.md`,
      the perf checklist docs, and this file's execution sections — only after 9.3
- [ ] **9.3** Done-state audit against the amendment's Done-State list (facades proven,
      one owner per mutable runtime, zero drift in endpoints/DTOs/keys/schema/filenames/
      licence vocabulary/prompt boundaries/backup format/installer behavior; every
      intermediate phase was shippable and revertible)

---

## 8. Bottom line

The refactor is the right investment, and after the 2026-07-19 re-review the CODEX
SOL 5.6 MAX amendment is the right playbook for it — it independently reconfirmed this
file's decision, and every load-bearing claim it makes checked out against the current
source, including its one genuinely new pre-gate finding (the Whisper lock-coverage gap,
confirmed at three exact call sites in `audio_queue.py`). The program still waits, fully
and without exception, behind Gate Zero: performance work finished honestly through
Phase 8, the branch's newer behaviors manually verified, the lock gap fixed as its own
reliability PR, the result shipped and smoke-tested, and Jonathan's explicit go recorded
against an exact baseline commit. When the gate opens, execute §7 top to bottom, tick
tri-state boxes only with dated evidence, and hold every PR to the standing gates plus
the >10% performance-neutrality block. The one thing that would go wrong if ignored:
starting any `src/shared/` or backend move while `performance-optimization` is still
unmerged would make both the perf numbers and the refactor diffs unattributable — the
exact failure mode both reviews were written to prevent. Nothing in this update touched
any application code; the only file changed is this document.
