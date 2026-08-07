# UI-IMPROVEMENT — Bulk Transcribe & Beautify: run visibility, counters, and upload dating

**Status:** BUILT 2026-08-06 — W1–W8 all landed on branch `ui-improvement-bulk-run`
(cut off `prompt-improve` as instructed). Backend + frontend unit tests added per work
item; `npx tsc --noEmit` clean throughout. The manual, real-audio verification pass in
§9 has not yet been run (needs the i5, IT436365, per its own guardrail) — do that before
merging.
**Raised:** 2026-08-06, from owner's own counsellor-role usage session (not a crash report — a usability pass).
**Scope:** the clinical **Bulk Audio Upload** and **Transcribe & Beautify** flows
(`BulkAudioUploadModal` + `audio_queue.py` counsellor worker) and the app-shell surfaces
that report on them. The meetings-side worker is explicitly out of scope — see §7.
**Branch when executed:** new branch off `prompt-improve`; do not fold into the
performance/benchmark work in `.claude/plan/TranscribeBeautifyBreakthrough.md`.

> **Read §1 before §2.** Every defect below is stated against verified code, with file
> and line citations taken on 2026-08-06. Where a cause is *inferred* rather than read
> off the code, it is labelled `[inferred]` and carries a measurement step.

> **Citations re-verified 2026-08-06 at `683c325`, after the owner's merges.** All seven
> primary source files — `BulkAudioUploadModal.tsx`, `SessionsPage.tsx`, `App.tsx`,
> `HomeDashboard.tsx`, `audio_queue.py`, `main.py`, `database.py` — are byte-identical to
> the state this plan was written against. `src/utils/api.ts` changed (+17 lines) but both
> cited anchors still land exactly (`AudioQueueState` :585, `ProcessAssignment` :640).
> The only stale item found and corrected: backend tests moved to `backend/tests/`.
> **Still re-locate a symbol before editing** — that is a habit, not a doubt about this stamp.

---

## 0. Bottom line

Seven reported symptoms reduce to **three structural causes** and **two localised bugs**:

| Cause | Produces | Fix shape |
| --- | --- | --- |
| **C1 — There is no app-level owner of bulk-run state.** The only live progress surface lives inside `SessionsPage`'s session-list sidebar, which is inside a `display:none` container on every tab except Sessions. `HomeDashboard` — where both bulk entry points actually live — is *unmounted* on tab switch, taking the modal and its state with it. | #1 (no persistent bar), #2 (wrong UI on reopen), #5 (progress invisible until the end) | Lift bulk-run status to `App.tsx`, mirroring the existing `batchBar` precedent (`App.tsx:182`, `:1363`). One poller, one source of truth, passed down. |
| **C2 — `_queue_state` reports aggregates only.** It knows `done`/`total` but not *which* recording is active, at *what stage*, or *for whom*. Every richer display today is reconstructed on the frontend by joining `GET /api/audio-queue` — an endpoint that is **not** on the workspace-lock allow-list (`main.py:79–94`), so any surface built on it goes blank while locked. | #5 (no per-file/per-stage view), and blocks the fix for #1 | Add per-item stage fields to `_queue_state` (ids only, no names). `process-status` is already lock-allow-listed and licence-ungated. |
| **C3 — Upload time is silently used as recording time, in two different places.** The modal's own label (`BulkAudioUploadModal.tsx:56–63`) and, more seriously, the created session's `date` and `title` (`audio_queue.py:523,531`). | #4 | Display fix (cheap) + per-row session date in Assign (needs a schema column and a contract change). |
| **B1 — Counter renders completed count, labelled as position.** `processStatus.done` is incremented *after* an item finishes (`audio_queue.py:582–583`), so "0 of 2" is literally true and reads as broken. | #3 | Derive the active index; do not change the backend counter. |
| **B2 — OS notification wording is transcribe-only in both modes.** `SessionsPage.tsx:1289–1291` and `:1299–1303` build their strings before the beautify-aware branch at `:1307`. | the "1 of 2 transcribe done" popup after a Transcribe & Beautify run | Two string sites, mode-aware. |

**Recommended execution order is W1 → W8 in §4.** W1–W4 are the spine and deliver #1, #2,
#3, #5 and the notification fix. W5–W7 (dating) are a separable second tranche with a real
schema change and a genuine product decision inside them (§10 Q1). W8 is cleanup.

---

## 1. Verified current behaviour

Facts, with citations. These are what the plan is built on; re-verify any that a future
edit may have moved.

### 1.1 Where the bulk flows are entered and where their UI lives

- Both entry cards are on **HomeDashboard only**: `showBulkAudio` (`HomeDashboard.tsx:91`,
  modal at `:643`) and `showBulkTranscribeBeautify` (`:92`, modal at `:706`).
- `App.tsx:1385` renders `HomeDashboard` **conditionally** (`activeTab === 'home' && …`).
  Leaving the Home tab therefore **unmounts** the dashboard, destroying `showBulk*` state
  and the modal with it. There is no way to keep the modal open across tabs, and reopening
  is always a cold mount.
- By deliberate contrast, `SessionsPage` is kept mounted inside
  `<div className={... activeTab === 'sessions' ? '' : 'hidden'}>` (`App.tsx:1410`).
- The **only** live bulk progress banner is `SessionsPage.tsx:5922–5961`, rendered inside
  that hidden container's session-list sidebar. It is invisible on Home, Clients, Calendar,
  Reports, Settings, Help and Weekly.
- The app shell already has the right pattern for a cross-tab bar: `batchBar`
  (`App.tsx:182`, rendered `:1363–1376`), fed by `onBatchProgress` and driven by
  `onBatchControlRegister` (`App.tsx:1426–1427`). **This is the precedent to copy.**

### 1.2 How the modal decides what to show on open

`BulkAudioUploadModal.tsx:123` initialises `const [phase, setPhase] = useState<Phase>("upload")`.
The initial effect (`:199–222`) then does:

```
loadQueue()                       // await GET /api/audio-queue
  .then(() => api.getAudioQueueProcessStatus()   // then GET /api/audio-queue/process-status
    .then(status => { if (status.running) setPhase("processing") }))
```

Two **serialized** round-trips before the phase can flip, with the Upload dropzone
rendered the whole time. In beautify mode two further calls fire (`listTemplates`,
`aiStatus` — `:226–239`).

### 1.3 The counter

`audio_queue.py` increments `_queue_state["done"]` only after an item is fully finished:
`:582–583` on success (and note for beautify runs `_finalize_group` at `:571` runs
*before* it, so `done` stays at the previous value throughout structuring), `:595–597` on
failure. The modal prints `{processStatus.done} of {processStatus.total} done`
(`BulkAudioUploadModal.tsx:1151`); the sidebar banner prints
`Transcribing {done} of {total}…` (`SessionsPage.tsx:5928`).

So while item 1 is being worked on, both correctly show `0`. The **aggregate** field is
right; the **label** implies position.

### 1.4 The notifications

`SessionsPage.tsx:1277–1328`, inside `checkAndStartBulkBgPoll`:

- per-item, on `done` increase: `` `Recording ${status.done} of ${status.total} transcribed.` `` (`:1289–1291`)
- on finish: `msg` is built at `:1299–1302` in transcribe-only wording, fired at `:1303`
- **only then** (`:1307`) does the code branch on `status.structured !== undefined` — and
  that branch feeds the *in-app* `runCompleteToast` only, never the OS notification.

For a Transcribe & Beautify run the OS notification is therefore always transcribe-only
wording, exactly as reported. Note also that in beautify mode `done` increments *after*
structuring for the insert branch, so the per-item notification actually fires when the
file is **completely** finished — the trigger is right, only the words are wrong.

### 1.5 Dating of uploaded audio

- Upload stores `created_at = utcnow()` (`audio_queue.py:769`). Nothing about the source
  file's own timestamp is captured.
- `recordingLabel()` (`BulkAudioUploadModal.tsx:46–69`) builds the **primary** label from
  client name + `created_at`, and puts the original filename in a 9px **secondary** line.
  For an external upload that primary date is the upload date.
- `handleStartProcessing` (`:398–403`) sends a single run-level `today`
  (`:159–160`) for **every** recording in the run.
- The backend writes `date = sd` and `title = f"Session — {sd}"` (`audio_queue.py:523,531`)
  — so a 27 June recording uploaded on 1 August produces a session dated **1 August**.
  This is a clinical-record error, not only a label error.

### 1.6 Constraints that bound any fix

- `/api/audio-queue/process-status` **is** on `_LOCK_ALLOW_PREFIXES` (`main.py:91`) and
  carries **no** `require_active_license` call (`audio_queue.py:983–986`).
  `/api/audio-queue` (the list) has neither property — it is licence-gated
  (`:668`) and blocked by the lock middleware.
  **Consequence: an always-on app-level bar must be able to render from `process-status` alone.**
- `sessions.date` is a **display string**, not ISO (CLAUDE.md, Data Model). Any per-row
  date must be formatted the same way the existing code does it.
- `MAX_PROCESS = 4` (`BulkAudioUploadModal.tsx:31`) and `MAX_QUEUE_SIZE = 10`
  (`audio_queue.py:48`) bound every list this plan renders — no virtualisation needed.
- `GET /process-status` returns `dict(_queue_state)` (`:985–986`) — a **shallow** copy.

---

## 2. Defect register

Severity: **S1** = produces a wrong clinical record; **S2** = counsellor cannot tell what
the app is doing during a multi-minute unattended run; **S3** = misleading text.

| # | Symptom (as reported) | Verified root cause | Sev | Fixed by |
| --- | --- | --- | --- | --- |
| D1 | No persistent status while bulk runs | C1 — banner lives inside the hidden `SessionsPage` subtree (`SessionsPage.tsx:5922`) | S2 | W3 |
| D2 | Reopening the modal shows "Upload" for ~10 s | C1 (HomeDashboard unmount ⇒ cold remount) + `phase` defaults to `"upload"` + two serialized round-trips (`BulkAudioUploadModal.tsx:123,199–212`). **The ~10 s magnitude is `[inferred]`** to be backend request latency under a CPU-saturated bulk run; the *ordering* defect is certain and fixing it removes the symptom regardless | S2 | W2 |
| D3 | Counter one behind (`0 of 2`) | B1 — `done` is a completion count (`audio_queue.py:582`) rendered under a positional label | S3 | W4 |
| D4 | Uploaded audio renamed with today's date | C3 — label (`BulkAudioUploadModal.tsx:56–63`) **and** session `date`/`title` (`audio_queue.py:523,531`) both use upload/run time | **S1** | W5–W7 |
| D5 | Detailed progress only appears near the end | C2 — the per-item bar (`:1127–1137`) needs `current_duration_s`, which is only non-zero for the item currently decoding; every other row is a static dot. There is no stage/file view at all outside the modal | S2 | W3 |
| D6 | Windows notification says "1 of 2 transcribe done" after a Transcribe & Beautify run | B2 — `SessionsPage.tsx:1289,1299–1303` are mode-blind; the mode-aware branch at `:1307` only feeds the in-app toast | S3 | W4 |
| D7 *(found during this analysis, not reported)* | `GET /process-status` can, in principle, raise mid-serialisation | `dict(_queue_state)` is shallow (`audio_queue.py:986`); the returned `created` list is the *same object* the worker thread appends to at `:520/:536`, and FastAPI serialises it after the lock is released | S3 (latent) | W1 |
| D8 *(found during this analysis, not reported)* | `session_number` fed to the Beautify prompt can be wrong for back-dated sessions | `audio_queue.py:189` sorts sibling sessions by the **display string** `date` — `"1 Aug 2026" < "27 Jun 2026" < "3 Jul 2026"` lexically. Already latent today; **W5–W7 make it reachable far more often**, so it must be fixed in the same tranche | S2 | W7 |

---

## 3. Architectural decision — one app-level bulk-run status source

**Decision.** `App.tsx` owns a single poll of `GET /api/audio-queue/process-status` and
distributes the result. `SessionsPage`'s private watchdog + poll pair
(`SessionsPage.tsx:1264–1355`) is **removed**, not duplicated.

**Why this and not the alternatives:**

- *Keep the poller in SessionsPage and portal the bar to `document.body`.* Rejected: it
  works (the `runCompleteToast` portal at `:6647` proves the technique) but it leaves the
  app-shell chrome owned by a page component, and `HomeDashboard` still cannot seed the
  modal's opening phase — D2 would survive.
- *Poll in each consumer.* Rejected: three pollers hitting a backend that is, by
  construction, running a CPU-saturating job. Today there are already two
  (`SessionsPage` 5 s watchdog + 2.5 s run poll, `:1343`/`:1328`) plus the modal's own 2 s
  loop (`BulkAudioUploadModal.tsx:263`).
- *Server-sent events over `/api/system/events`.* Rejected for now: that channel exists and
  is allow-listed, but this is a 2–4 minute job whose state changes every few seconds.
  Polling is adequate and far cheaper to reason about. Revisit only if the poll itself
  shows up as measurable overhead.

**Cadence.** One interval, adaptive: **5 s** when idle, **2 s** while `running`. Net
request rate goes *down* versus today.

**Distribution.** `App.tsx` passes the status object to `HomeDashboard` (so the modal can
mount straight into the right phase) and to `SessionsPage` (so its existing disable-guards
at `:4500`, `:4592`, `:5982`, `:7290`, `:7823` and its `onBusyChange` contribution at
`:1362` keep working from a prop instead of local state).

**Non-negotiable:** the bar must degrade, not disappear, when only `process-status` is
reachable (locked workspace / lapsed licence — §1.6). Names come from `App.tsx`'s existing
`clients` array joined on `client_id`; if that array is empty, the bar shows
"Recording 2 of 3" and stays useful.

---

## 4. Work items, in dependency order

Each item lists **files**, **change**, **acceptance**, **risk**. Do not reorder W1→W4.

### W1 — Backend: per-item stage in `_queue_state` (+ fix D7)

**Files:** `backend/routers/audio_queue.py`

**Change.**

1. Extend the counsellor `_queue_state` (`:55–66`) with, all guarded by `_queue_lock`:
   - `current_queue_id: int | None`
   - `current_client_id: int | None`
   - `current_stage: 'transcribing' | 'structuring' | None`
   - `items: [{queue_id, client_id, session_id, stage}]` — one entry per id in this run,
     `stage` ∈ `queued | transcribing | structuring | saved | failed`
2. Write sites:
   - loop head, right after the `status = 'transcribing'` UPDATE (`:428–435`): set
     `current_*` and flip that item's `items[]` entry to `transcribing`
   - `_finalize_group`, in the `not is_partial` branch after the `status = 'structuring'`
     UPDATE (`:160–166`): set `current_stage='structuring'`, `current_queue_id` = first of
     `queue_ids`, `current_client_id` from the already-fetched `session_row` → `client_row`
   - on success (`:582`) → `saved`; on exception (`:595`) → `failed`
   - at run end (`:631–633`): clear `current_*` to `None`
3. **Fix D7** in `get_process_status` (`:983–986`): build the response inside the lock with
   the mutable lists copied —
   `state = dict(_queue_state); state["created"] = list(state["created"]); state["items"] = [dict(i) for i in state["items"]]`.

**Acceptance.**
- `GET /api/audio-queue/process-status` during a 3-file beautify run returns a stage for
  every item, and exactly one item in `transcribing` **or** `structuring` at a time.
- The response contains **no** names, filenames, transcript text, or template names — ids
  and enums only. (Same discipline as the Support Diagnostic Log; see CLAUDE.md.)
- Existing consumers that ignore the new fields are unaffected.

**Risk.** Low. Additive; every write is already inside a `_queue_lock` region or trivially
placed in one. The one trap: `_finalize_group` is also reachable from the post-loop pass
(`:610–629`) where several groups run in sequence — its `current_*` write must be per-call,
not per-run.

---

### W2 — Frontend types + a single status hook

**Files:** `src/utils/api.ts`, new `src/hooks/useBulkAudioRun.ts`

**Change.**

1. `AudioQueueState` (`api.ts:585–604`) gains the W1 fields, all optional, plus a
   `BulkRunItem` interface. No `any` (CLAUDE.md).
2. New hook `useBulkAudioRun()`: owns the adaptive interval from §3, exposes
   `{ status, running, activeIndex, stage, currentClientId, items, stop() }`.
   `activeIndex` is the D3 fix and is computed **once, here**:

   ```ts
   // `done` is a completion count, not a position (audio_queue.py increments it
   // after the item finishes). The counsellor is watching item done+1.
   const activeIndex = running ? Math.min(status.done + 1, status.total) : status.done;
   ```

   The `Math.min` clamp matters: during the post-loop finalize pass of a merge group,
   `done` already equals `total` while structuring is still running — without the clamp
   the bar would read "3 of 2".

**Acceptance.** `npx tsc --noEmit` clean. Hook unit-testable with a stubbed `api`.

**Risk.** Low.

---

### W3 — App-level announcement bar (delivers D1, D5)

**Files:** `src/App.tsx`, new `src/components/BulkRunBar.tsx`

**Change.** `App.tsx` calls `useBulkAudioRun()` and renders `<BulkRunBar/>` in the same
chrome slot as `batchBar` (`App.tsx:1363`), above `<main>`, on every tab.

**Collapsed row** (always visible while `running`):

```
[spinner]  Transcribing — Chris Park · 2 of 3       [====------]     Details ▾   Stop
```

- verb from `stage`: `Transcribing` / `Structuring` / `Finishing up` (stage `null` while
  running — the brief window between items)
- name from `currentClientId` joined against `App.tsx`'s `clients`; falls back to
  `Recording 2 of 3` when unresolvable (§3 non-negotiable)
- the thin bar is the existing `current_processed_s / current_duration_s` ratio
  (`SessionsPage.tsx:5946–5955`) — present during transcription, absent during structuring
  (the backend has no token-level progress for the beautify half, and inventing one is out
  of scope)
- **Stop** calls `api.cancelAudioQueue()` behind `useConfirm()` — never `window.confirm`
  (CLAUDE.md Design System). Copy must say what survives, matching the modal's existing
  promise at `BulkAudioUploadModal.tsx:1188–1191`: already-saved sessions are kept, the
  in-progress recording resets to pending.

**Expanded panel** (`Details ▾`, a popover anchored under the bar, ≤4 rows by `MAX_PROCESS`):

```
✓  Chris Park          Saved
◐  Amelia Tran         Structuring…
○  Sam Rivera          Queued
```

driven entirely by `items[]` from W1 — so it keeps working while the workspace is locked.

**Also in this item:** replace `SessionsPage`'s in-sidebar banner (`:5922–5961`) with
nothing. Two banners for one run is worse than one. Keep the surrounding
`Recording and note structuring paused.` explanation, relocated into the expanded panel.

**Acceptance.**
- Start a 3-file run from Home, immediately switch to Clients → Calendar → Settings. The
  bar is present and counting on all of them.
- Lock the workspace mid-run (PIN). The bar still counts and still names stages;
  client names degrade to `Recording n of N` rather than the bar vanishing.
- The bar disappears within one poll interval of the run finishing.

**Risk.** Medium — this is app-shell chrome and it is on screen for minutes at a time.
Vertical space is the real cost: it must be a single 32–36 px row collapsed, matching
`batchBar`'s existing density. If both `batchBar` and `BulkRunBar` could ever be active at
once — they cannot, because batch beautify is disabled while `bulkRunningInBg`
(`SessionsPage.tsx:5982`) — but assert it rather than assume it.

---

### W4 — Correct openings, correct counters, correct notifications (D2, D3, D6)

**Files:** `src/pages/HomeDashboard.tsx`, `src/components/BulkAudioUploadModal.tsx`,
`src/pages/SessionsPage.tsx`

**Change.**

1. **D2.** `App.tsx` passes the live status into `HomeDashboard`, which passes it to the
   modal as `initialStatus`. The modal's `useState<Phase>` initialiser becomes
   `initialStatus?.running ? "processing" : "upload"` — **the phase is correct on the very
   first paint**, with zero network waits. The existing `:199–222` effect stays as a
   reconciler, but its two calls are made concurrent (`Promise.all`) rather than nested.
   Additionally, when `initialStatus` is absent (cold start, status not yet known) the
   modal renders a neutral one-line "Checking for a run in progress…" placeholder instead
   of the Upload dropzone — **never show an affordance that may be about to be replaced.**
2. **D3.** Modal `:1151` and any surviving counter use `activeIndex` from W2:
   `Recording {activeIndex} of {total}` while running; on the Done phase keep the true
   completion counts, which are already correct.
3. **D6.** In `checkAndStartBulkBgPoll`:
   - per-item (`:1289–1291`) → mode-aware:
     `beautify ? \`Recording ${done} of ${total} transcribed and structured.\` : \`Recording ${done} of ${total} transcribed.\``
     where `beautify = status.structured !== undefined` (the same discriminator already
     used at `:1307`, and the honest one — the backend only reports `structured` when
     `beautify:true` was sent).
   - final (`:1299–1303`) → build the OS notification body from the **same** strings as the
     in-app toast at `:1313–1322`. Extract one `buildRunSummary(status)` helper returning
     `{title, body}` and feed both. This is the actual defect: two independent string
     builders, one of which never learned about beautify.
   - keep **one** OS notification per completed file plus one summary. Do **not** add
     per-file in-app toasts — the owner explicitly flagged toast noise, and with
     `MAX_PROCESS = 4` the expanded panel already carries per-file state.

**Acceptance.**
- Start a 2-file Transcribe & Beautify, leave Home, return, reopen the modal: the
  Processing phase is on screen in the first frame; the Upload dropzone never appears.
- Counter reads `1 of 2` while the first file is being worked on and `2 of 2` while the
  second is, in **both** the bar and the modal.
- Windows notifications for a beautify run never say "transcribed" alone.

**Risk.** Low-medium. The `buildRunSummary` extraction touches the only code path that
tells the counsellor a multi-minute unattended job finished — verify both modes by hand,
not only by reading.

---

### W5 — Capture the source file's own timestamp (foundation for D4)

**Files:** `backend/database.py`, `backend/routers/audio_queue.py`, `src/utils/api.ts`,
`src/components/BulkAudioUploadModal.tsx`

**Change.**

1. Migration in `init_db()` alongside the existing `audio_queue` `PRAGMA table_info`
   block (`database.py:1151–1169`), same style:
   - `source_modified_at TEXT` — ISO string from the browser's `File.lastModified`, or NULL
   - `origin TEXT DEFAULT 'recorded'` — `'recorded' | 'uploaded'`
2. `POST /api/audio-queue/upload` (`audio_queue.py:717–780`) accepts both as optional query
   params and persists them.
3. `api.uploadAudioQueueItem` forwards `file.lastModified` and `origin: 'uploaded'` from
   the modal's `handleFiles` (`BulkAudioUploadModal.tsx:284–291`); the in-session recorders
   in `SessionsPage`/`MeetingDashboard` pass `origin: 'recorded'`.

**Why `origin` and not the filename regex.** `OWN_RECORDING_FILENAME`
(`BulkAudioUploadModal.tsx:38`) is a heuristic on `session_<epoch>.webm`. It is fine for a
cosmetic label; it is **not** fine as the discriminator for how a clinical record gets
dated. Record the fact at the moment it is known.

**Acceptance.** Existing rows migrate to `origin='recorded'`, `source_modified_at=NULL`, and
behave exactly as today. `env\Scripts\python.exe -m unittest tests.test_audio_queue_resume`
passes — run from `backend/`, with `PRIVATE_DB_DIR` **and** `PRIVATE_STORAGE_DIR` set
(CLAUDE.md; see `bugs-fixed/049-28072026.md` Part 5 — a prior sweep destroyed live data).
Test files moved from flat `backend/` into `backend/tests/` on 2026-08-05; there is still
**no `conftest.py` and no `__init__.py`**, so each file sets those env vars itself before
importing app modules. Any new test in this plan must do the same.

**Risk.** Low, but it is a schema change: `init_db()` must stay re-runnable.

---

### W6 — Label uploaded recordings honestly (D4, display half)

**Files:** `src/components/BulkAudioUploadModal.tsx`

**Change.** `recordingLabel()` (`:46–69`) branches on `origin`:

| origin | primary | secondary |
| --- | --- | --- |
| `recorded` | `{Client or "Recording"} · {created_at date, time}` — **unchanged** | `#{id}` — unchanged |
| `uploaded` | `{original filename}` | `{Client name} · Uploaded {created_at date}` |

The word **"Uploaded"** is load-bearing: it is what stops a date being read as a recording
date. Where a `source_modified_at` exists and differs from `created_at` by more than 24 h,
append `· file dated {source date}` — presented as *file metadata*, never as fact.

**Acceptance.** A file named `Chris-27June.m4a` uploaded on 1 Aug shows
`Chris-27June.m4a` as its primary label, and no bare `01 Aug` that could be mistaken for
when the session happened. Dates still go through `formatDate` (Luxon, `private_locale`) —
never `toLocale*` (CLAUDE.md).

**Risk.** Low. Pure display. Note it changes three render sites (`:616`, `:767`, `:1065`)
that all call the same helper — good.

---

### W7 — Per-recording session date (D4, record half; + fix D8)

**This is the only item in the plan that changes what lands in the clinical record.**

**Files:** `src/components/BulkAudioUploadModal.tsx`, `src/utils/api.ts`,
`backend/routers/audio_queue.py`

**Change.**

1. `ProcessAssignment` gains optional `session_date: string` (frontend `api.ts:640–645`,
   backend `audio_queue.py:852–856`).
2. The Assign phase gains a per-row **Session date** control, defaulting to today.
   For `origin='uploaded'` rows whose `source_modified_at` is more than 24 h before
   `created_at`, the row shows an inline suggestion — *"This file's own timestamp says
   27 Jun 2026. Use that date?"* — with an explicit accept. **Never auto-apply it.**
   Filesystem mtime is evidence about a file, not about a counselling session, and some
   copy/sync paths rewrite it.
3. `_run_transcription_queue` uses the per-row date where supplied, falling back to the
   existing run-level `session_date` (`:523`) so nothing changes for recorded audio.
   Format via the same `formatDate(d, DATE_OPTS)` the modal already uses (`:159–160`) so
   the display-string shape stays consistent.
4. **Fix D8.** Replace the lexical sort at `:189` with a parsed one, reusing
   `system.py::_parse_date_robust` (`system.py:940–951`) — rows that fail to parse sort
   last by `id`, never crash. Back-dated sessions currently get a wrong `session_number` in
   the Beautify prompt; this plan makes back-dating easy, so the fix ships with it.

**Acceptance.**
- Two files uploaded together, dated differently in Assign, produce two sessions with two
  different `date` values and matching `title`s.
- A recorded-in-app run produces byte-identical `date`/`title` output to today.
- `session_number` for a client with sessions on 27 Jun / 3 Jul / 1 Aug is 1 / 2 / 3.

**Risk.** **Highest in the plan.** `sessions.date` is a display string consumed by
insights, reports, exports and the ordering above. Add a focused unittest for the parse
ordering. Do not attempt to normalise `sessions.date` to ISO in this plan — that is a
migration, and it is out of scope (§7).

---

### W8 — Cleanup and consistency

- Remove `SessionsPage`'s now-dead `checkAndStartBulkBgPoll`, `bulkBgPollRef`,
  `bulkBgPrevDoneRef` and the 5 s watchdog (`:1264–1355`), replacing `bulkRunningInBg`
  with the prop from W3. **Keep every consumer**: the `onBusyChange` contribution at
  `:1362` (Electron close-while-busy guard) and all five disable-guards. Losing one of
  those re-enables a Beautify button during a bulk run.
- One `npx tsc --noEmit` pass; strict mode, `noUnusedLocals`/`noUnusedParameters` will
  catch the leftovers.
- Update `.claude/plan/BulkTranscribeAndBeautify.md` and CLAUDE.md's Audio Recording
  section: the "standing 5-second watchdog in `SessionsPage`" sentence becomes untrue the
  moment W8 lands.

---

## 5. Backend contract summary

Additive only. No endpoint is added, removed, or re-gated.

```
GET /api/audio-queue/process-status        (unchanged path; lock-allow-listed; no licence gate)
  + current_queue_id  : int | null
  + current_client_id : int | null
  + current_stage     : "transcribing" | "structuring" | null
  + items             : [{ queue_id, client_id, session_id, stage }]
                          stage ∈ queued | transcribing | structuring | saved | failed

POST /api/audio-queue/upload
  + ?source_modified_at=<ISO>   (optional)
  + ?origin=recorded|uploaded   (optional, default "recorded")

POST /api/audio-queue/process
    assignments[].session_date : string (optional; falls back to run-level session_date)
```

**Payload discipline.** Ids and enums only. No client names, no filenames, no transcript
text crosses this boundary that did not already. The frontend resolves names from state it
already holds.

---

## 6. Copy

Draft strings, to be reviewed before build. NZ spelling; never expose model names
("Whisper", "Gemma") — CLAUDE.md.

| Surface | String |
| --- | --- |
| Bar, transcribing | `Transcribing — {name} · {i} of {n}` |
| Bar, structuring | `Structuring — {name} · {i} of {n}` |
| Bar, between items | `Preparing — {i} of {n}` |
| Bar, no name available | `Recording {i} of {n}` |
| Panel row stages | `Queued` · `Transcribing…` · `Structuring…` · `Saved` · `Failed` |
| Panel footer | `Recording and note structuring are paused while this runs. Your computer must stay awake.` |
| Stop confirm | `Stop after the current recording? Sessions already saved are kept. The recording in progress goes back to the queue so you can retry it.` |
| Modal, phase unknown | `Checking for a run in progress…` |
| OS notify, per item, transcribe | `Recording {done} of {total} transcribed.` |
| OS notify, per item, beautify | `Recording {done} of {total} transcribed and structured.` |
| OS notify, final | identical to the in-app toast body — one `buildRunSummary()` |

---

## 7. Explicitly out of scope

- **The meetings-side worker** (`_meetings_queue_state`, `/process-meetings*`). It has the
  same shape and the same D1/D3 defects. Doing both at once doubles the surface and risks
  the dual-workspace separation invariant. Port the pattern in a follow-up once W1–W4 have
  been used in anger.
- **Normalising `sessions.date` to ISO.** Correct, and a migration touching insights,
  reports and exports. Not here.
- **Token-level progress for the structuring half.** The backend does not expose it for
  the bulk worker and adding it means threading `capture_stats` through
  `beautify_notes_stream` per item. The stage label answers the counsellor's actual
  question ("is it stuck?") without it.
- **Anything touching transcription or Beautify speed.** That is
  `.claude/plan/TranscribeBeautifyBreakthrough.md`. **Do not run these UI changes on a
  benchmark machine during a measurement window** — §11 of that plan requires office-idle
  conditions, and a frontend rebuild is not idle.

---

## 8. Invariants this plan must not break

1. **Dual workspace separation.** Nothing here may let a counsellor `client_id` reach the
   meetings path or vice versa. `_queue_state` and `_meetings_queue_state` stay separate.
2. **Lock and licence behaviour.** The new bar must not become a reason to widen
   `_LOCK_ALLOW_PREFIXES` or to add a licence gate to `process-status`. If a surface needs
   data it cannot get, that surface degrades.
3. **`require_active_license()` stays on every licence-gated route it is on today.**
4. **No `any`; `npx tsc --noEmit` after every frontend change.**
5. **`useConfirm()`, never `window.confirm`/`alert`.** The Stop control is a confirmation.
6. **Backend tests are `unittest`, and must set `PRIVATE_DB_DIR` *and* `PRIVATE_STORAGE_DIR`
   before importing app modules.** See `bugs-fixed/049-28072026.md` Part 5.
7. **`init_db()` stays safe to re-run.**

---

## 9. Test plan

**Backend (`unittest`, isolated DB + storage roots):**

- `_queue_state` stage transitions across a 3-item run: queued → transcribing → structuring
  → saved, exactly one active at a time; cleared at end.
- `get_process_status` returns copies — mutate the worker's `created`/`items` after the
  call and confirm the response is unaffected (D7).
- Per-row `session_date` honoured; omitted falls back to run-level (W7).
- `_parse_date_robust` ordering: `27 Jun 2026` < `3 Jul 2026` < `1 Aug 2026`, unparseable
  last (D8).
- Migration idempotence: `init_db()` twice, no error, no duplicate columns.

**Frontend:** `npx tsc --noEmit`; `useBulkAudioRun` `activeIndex` against a stub
(`done=0,total=2,running` → `1`; `done=2,total=2,running` → `2`, **not** `3`;
`done=2,total=2,finished` → `2`).

**Manual, on the i5 (IT436365), 2 real recordings, Transcribe & Beautify:**

1. Start from Home → immediately navigate Clients → Calendar → Settings. Bar present and
   counting throughout. *(D1)*
2. Return to Home, reopen the modal. Processing phase in the first frame. *(D2)*
3. Watch the counter through both files: `1 of 2`, then `2 of 2`. *(D3)*
4. Expand Details during file 2's structuring: file 1 `Saved`, file 2 `Structuring…`. *(D5)*
5. Let it finish with the app minimised. Read the Windows notifications: no beautify run
   ever described as merely "transcribed". *(D6)*
6. Lock the workspace mid-run; confirm the bar survives and degrades gracefully.
7. Upload a file whose mtime is weeks old; confirm the label shows the filename and the
   word "Uploaded", and that Assign offers — but does not apply — the older date. *(D4)*

---

## 10. Open questions for the owner

**Q1 — Default session date for uploaded audio.** W7 proposes: default **today**, *suggest*
the file's own timestamp, require an explicit accept. The alternatives are (a) default to
the file timestamp when one exists, or (b) block Start until every uploaded row has a
confirmed date. (b) is safest for the record and the most annoying in the common case where
the counsellor uploaded this morning's recording. **Recommendation: as written.** Filesystem
metadata is a hint, and a clinical date should be something a person asserted.

**Q2 — Should the bar be dismissible?** It occupies a row for 2–4+ minutes on every tab.
**Recommendation: collapsible to a small pill, not dismissible.** The whole point is that
the counsellor walked away; a bar they can close is a bar they will close and then wonder
about.

**Q3 — Keep the per-file OS notification at all?** With `MAX_PROCESS = 4` that is up to
five notifications per run. **Recommendation: keep for now** (the trigger is already
correct — it fires on genuine per-file completion, §1.4) and revisit after real use.
If it grates, drop the per-file one and keep only the summary.

**Q4 — `MAX_PROCESS = 4` versus the expanded panel.** The panel is designed for ≤4 rows.
If the cap ever rises, it needs a scroll container. Flagging, not proposing.
