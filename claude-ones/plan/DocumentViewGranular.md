# Document Detail View — Granular Assessment & Build Checklist

Companion to `.claude/plan/DocumentView.md` (the original request + locked-in Decisions section).
This doc is the granular record: the fable-mode assessment behind those decisions, every finding
with its evidence, and the step-by-step checklist to build against. Per this repo's multi-session
protocol, **the "Current Status" block below is the single source of truth** — resume work by
reading that block, not by re-deriving from chat history.

## Current Status

**2026-07-10 — Phases 0-3 built, none UI-tested yet.** Fable-mode assessment done (this doc).
Two open architectural questions resolved via user confirmation:
1. Presentation = **new full-bleed overlay** (not the existing slide-over, not the existing intercept-modal shape).
2. Drawing Observations (Feature B) UI **moves into** the new detail view; timeline card shrinks back to compact.

All four build phases (0-3) are coded and `tsc`-clean. New file: `src/components/DocumentDetailView.tsx`.
Changed: `backend/database.py`, `backend/routers/documents.py`, `src/utils/api.ts`,
`src/components/ClientHistoryPanel.tsx`. **Nothing has been run in the actual app yet** — every item
marked `[~]` below needs a real click-through, especially Phase 1's PDF-rendering item (F1), which is
the one genuinely unverified assumption in the whole feature. Phase 4 (Verify) is next: run the app,
click through, flip `[~]` → `[x]` per item or report back what broke.

**Checklist convention for this doc (agreed 2026-07-10):** `[ ]` not started, `[~]` implemented but
not yet confirmed safe to build on top of (needs hands-on/UI check or a real-world input like an
actual PDF), `[x]` implemented and verified. Phase 0 items went straight to `[x]` since they're
backend-only and self-checkable via `tsc`/code read — no UI involved. Expect `[~]` to start showing
up from Phase 1 onward.

---

## Scope

Read-only assessment — no application code was changed while producing this document (one edit to
`DocumentView.md`'s Decisions section records the two resolved questions; that's the only file
touched). All claims below were checked against the current state of the code on 2026-07-10 on
branch `performance-optimization`, not inherited from the original `DocumentView.md` request.

---

## One-page summary

**Where things actually are:** the original plan's "Decisions" section (2026-07-06) is still
accurate — nothing drifted. The gap is that it was written without checking two things the code
already reveals: Electron's PDF viewer isn't provably enabled, and an existing shipped feature
(Drawing Observations) already occupies the exact UI real estate the new notes view wants.

**The biggest things available, in order:**
1. Spike PDF rendering before building anything — the app's Electron window has no `plugins: true`, so inline PDF rendering via blob URL is unverified, not confirmed (F1).
2. Decide the fate of Drawing Observations before Phase 3, not during it — it's a real scope fork against already-shipped code, not a footnote (F2) — **resolved: move it in**.
3. Neither existing overlay pattern in the app (680px slide-over, `max-w-xl`/`80vh` intercept modal) is sized for "document is the star" — needs a new, bigger shape — **resolved: new full-bleed overlay**.

**One warning before anything else:** don't build the notes-textarea-and-metadata chrome first and
discover the PDF viewer doesn't render at the end. Verify the viewer first (Phase 1); everything
else is cheap UI wrapping around it.

---

## Reconciliation with `DocumentView.md`

| Doc | What it covers | Status vs. today |
|---|---|---|
| `DocumentView.md` (2026-07-06 Decisions) | notes = new field separate from `label`; timeline card stays as-is; layout order (file big, metadata small, notes below); no-router, state-driven nature; no viewer exists today; non-renderable types fall back to download | **Adopted as-is** — re-verified against current code, all still true, no changes needed |
| This doc (2026-07-10) | PDF-rendering risk, Drawing Observations scope fork, overlay-shape recommendation, auth/blob-URL mechanics, `isPending` gating, blob-URL lifecycle | **New material** — the delta the original plan couldn't have known without reading `ClientHistoryPanel.tsx` and `electron/main.js` line-by-line |

`DocumentView.md` remains the doc of record for *what* the feature is and the original decisions.
This doc is the doc of record for *how* to build it safely and in what order.

---

## Findings

**F1 — Electron's built-in PDF viewer is not enabled; inline PDF rendering is unverified, not confirmed.** (P1 — blocks Phase 1 until spiked)
`electron/main.js:401-410` — the `BrowserWindow`'s `webPreferences` sets `contextIsolation: true`,
`nodeIntegration: false`, `sandbox: true`, `devTools: isDev`, but no `plugins: true`. Electron gates
its bundled PDFium/`pdf-viewer` behind that flag; without it, Chromium's default behavior for a PDF
loaded via `<iframe src="blob:...">` / `<embed>` is typically to trigger a download rather than
render inline.
Concrete failure scenario: the whole detail-view layout gets built assuming
`<iframe src={blobUrl}>` shows the PDF, then the first real intake-form PDF either silently
downloads or renders a blank frame.
Evidence status: assumed from Electron's documented default — never tested in this app.
Fix sketch (if needed): `plugins: true` on the one `BrowserWindow`. Small change, but it sits right
next to the security-hardening flags (`sandbox`, gated `devTools`, local-token argument) — treat as
a deliberate, reviewed change, not a fix discovered mid-build. Alternative if you don't want to
touch that file: bundle a PDF.js-based viewer instead of relying on the native one.

**F2 — Drawing Observations already lives where the plan wants to put the notes UI; the plan doesn't address it.** (P1 — changes the shape of Phase 2/3, not just an add-on) — **RESOLVED: move into detail view**
`src/components/ClientHistoryPanel.tsx:761-870` — for image documents, the timeline card already
renders a full stateful sub-feature: status lifecycle (`not_generated/pending/generated/edited/failed`),
a 6-row textarea, Save / Insert-into-session / Prepare-again buttons (Feature B, shipped 2026-06-12).
This occupies the same conceptual space ("big content about one document") the new notes UI targets.
Concrete failure scenario (if left unresolved): a counsellor reviewing an intake photo has to work
across two different UI locations for the same document — Prepare/Save/Insert on the compact
timeline card, freeform notes in the new full-bleed view — discovered by users as an inconsistency
rather than decided up front.
Resolution (user-confirmed 2026-07-10): relocate the whole block into the new detail view, next to
the manual notes field. Timeline card shrinks back to compact metadata-only, matching how
non-image documents already render there.

**F3 — Auth means naive `<img src="...">` / `<iframe src="...">` against the API URL will not work.** (Adopted — confirms *why* the plan's blob-URL assumption is mandatory, not optional)
`src/utils/api.ts:5` — `LOCAL_TOKEN` from `window.electronAPI.localApiToken` is required as an
`X-Local-Token` header on every document fetch (`src/utils/api.ts:1069-1071`,
`backend/routers/documents.py:148` download endpoint). A plain `src="http://127.0.0.1:8000/api/documents/5/download"`
carries no header and 401s. The download endpoint already sets the correct `media_type` via
`mimetypes.guess_type` (`backend/routers/documents.py:172`), so `response.blob()` →
`URL.createObjectURL()` carries the right content-type for `<img>`/`<iframe>` once fetched properly
— no backend change needed for viewing itself, only a frontend fetch-as-blob helper.

**F4 — The existing blob-URL lifecycle (10s auto-revoke) is wrong for a viewer.** (P2 — will surface as a bug if missed, not a build-blocker)
`src/utils/api.ts:1084` — `setTimeout(() => URL.revokeObjectURL(url), 10_000)` inside
`downloadClientDocument()` is correct for a one-shot save-to-disk (the browser only needs the URL
alive long enough to trigger the download). An inline viewer that stays open needs its own
revoke-on-close lifecycle, or the image/PDF goes blank ~10s after opening a document someone is
still reading.

**F5 — `isPending` (device-transfer read-only mode) already gates upload/generate in this panel; anything relocated into the new view must inherit it.** (P1 — data-integrity guard, not cosmetic)
`ClientHistoryPanel.tsx:211,473,588` — `isPending` disables Save Document and Generate Holistic
Summary during a device-transfer verification window (`.claude/plan/DeactivatePlanForAllCases.md`).
If notes-save and the relocated observations actions move into the new detail view, that prop and
the same disabled/title pattern must travel with them, not get silently dropped in the move.

---

## Locked decisions (2026-07-10, user-confirmed)

**1. Presentation shape.** New full-bleed overlay: `fixed inset-0`, above the slide-over's `z-50`
and the vision-intercept's `z-60` (e.g. `z-[70]`) since it opens from inside `ClientHistoryPanel`
and must sit on top of it. Local component state (`openDocument: ClientDocument | null`), not a new
`view`/`activeTab` — that machinery is workspace/tab level; this is scoped inside one already-open
client. Closed via back arrow/X back to the slide-over/timeline.

Rejected alternatives and why: a bigger centered modal (reuses the batch-beautify intercept shape)
is still a "answer this, then get out of the way" gate pattern, not a place to linger reading/editing
— wrong metaphor. Staying inside the existing 680px slide-over keeps file rendering too narrow for
"document is the star."

**2. Drawing Observations relocation.** Moves fully into the new detail view (not left on the card,
not duplicated in both places). Timeline card goes back to compact metadata-only for all document
types, image or not.

---

## Execution Checklist

### Phase 0 — Schema + API (cheap, unblocks everything) — ✅ DONE 2026-07-10
- [x] `backend/database.py`: add `notes TEXT` column to `client_documents`, following the exact
      `PRAGMA table_info` + conditional `ALTER TABLE` pattern already used for the `observations`
      columns (`database.py:978-989`) — insert right after the `observations_error` block.
- [x] `backend/routers/documents.py`: add `notes: Optional[str] = None` to `DocumentUpdate`.
- [x] `update_document()` handler: add plain `if body.notes is not None: updates["notes"] = body.notes.strip()`
      — no sticky-status extra_fields needed, `notes` is manual freeform text, not AI-generated
      (unlike `observations`, which has the edited/regenerate lifecycle).
- [x] `src/utils/api.ts`: add `notes?: string | null` to the `ClientDocument` interface.
- [x] `src/utils/api.ts`: add `notes?: string` to `updateClientDocument()`'s data param type.
- [x] Confirm no backup/encryption changes needed — `notes` rides inside the already-encrypted DB
      row for free (same chokepoint as every other `client_documents` column). Confirmed: goes through
      the same `get_db_connection()` chokepoint as every other column, no new code path.

  Verified: `npx tsc --noEmit` clean. Column migration follows the established pattern exactly (init_db()
  is safe to re-run, existing DBs pick up the column on next launch). Self-checked, no UI involved — no
  manual testing needed for this phase.

### Phase 1 — Viewer spike (before any layout work — resolves F1) — built 2026-07-10
- [~] Confirm image rendering via blob URL `<img>` works — implemented (`DocumentDetailView.tsx`
      fetches via `api.fetchDocumentBlobUrl`, renders `<img>`, falls back on `onError`). **Needs a
      real upload to confirm.**
- [~] Confirm PDF rendering via blob URL `<iframe>` works in this Electron config — implemented
      (plain `<iframe src={blobUrl}>`, no `plugins: true` added yet — see F1). **This is the one
      genuinely unknown item in the whole feature; needs a real PDF.** If it downloads instead of
      rendering, or shows blank, that's the signal to come back and decide `plugins: true` vs.
      bundled PDF.js.
- [ ] If PDF rendering fails: decide `plugins: true` in `electron/main.js` webPreferences vs. a
      bundled PDF.js viewer. Not started — contingent on the item above.
- [x] Factor a shared blob-fetch helper off `downloadClientDocument()` — done:
      `api.fetchDocumentBlobUrl()` in `src/utils/api.ts`, `downloadClientDocument()` refactored to
      call it. Self-verified (pure code, `tsc` clean).
- [x] Give the viewer its own revoke-on-close lifecycle — done: `DocumentDetailView`'s blob-fetch
      `useEffect` revokes on doc-change/unmount, does not reuse the 10s auto-revoke. Self-verified by
      reading the effect/cleanup; the "no leak in practice" claim is what Phase 4's manual check is for.

### Phase 2 — Detail view component + entry points — built 2026-07-10
- [~] Built the full-bleed overlay (`src/components/DocumentDetailView.tsx`, new file): metadata row
      → file render → notes textarea + Save. **Needs a look in the running app** — this is layout/visual,
      not something `tsc` can confirm.
- [x] Gate notes-save with `isPending` — done, same disabled/title copy as elsewhere in this panel
      (`'Verifying your move — finalize this laptop before making changes'`). Self-verified (pure
      code, copied verbatim per F5).
- [~] Wire entry point 1: `handleUpload()` success now captures the created document and calls
      `setOpenDocument(created)` instead of just closing the form. **Needs a click-through** —
      upload a file, confirm it lands on the new page instead of just closing.
- [~] Wire entry point 2: timeline document card is now `onClick={() => setOpenDocument(doc)}`
      (inner Download/Delete/session-link buttons got `stopPropagation` so they don't also open the
      view). **Needs a click-through**, including confirming the inner buttons still work standalone.
- [~] Non-renderable types (docx, xlsx, xls, csv, txt, rtf, md, odt) get the explicit fallback state
      — implemented as a straightforward else-branch, but real confirmation is Phase 4's per-type pass.

### Phase 3 — Relocate Drawing Observations (resolved: move) — built 2026-07-10
- [~] Moved the Prepare/Save/Insert/Regenerate block into `DocumentDetailView.tsx`, image documents
      only (same `IMAGE_TYPES` gate). State/handlers (`obsDrafts`, `obsBusyId`, `obsSavingId`,
      `obsSavedId`, `confirmRegenId`, `handlePrepareObservations`, `handleSaveObservations`,
      `handleInsertIntoSession`) **stayed in `ClientHistoryPanel.tsx`** and are passed down as props —
      the move only relocated the JSX/presentation, not the state cluster (kept the polling and the
      vision-intercept modal in one place, per refactor-discipline guidance). **Needs a click-through**
      of Prepare → Save → Insert-into-session → Prepare again, on a real image document.
- [x] Shrunk the timeline card back to compact metadata-only (title, date, file type, size, encrypted
      badge, session link, download, delete) — the old ~110-line observations block is gone from the
      card entirely. Self-verified by reading the JSX; matches non-image documents' rendering exactly
      since it's now the same code path.
- [~] 5s polling for `observations_status === 'pending'` stays in `ClientHistoryPanel.tsx` unchanged;
      added a new `useEffect` that re-syncs `openDocument` from the `documents` array whenever it
      changes, so a poll tick while the detail view is open updates what's on screen. **Needs a live
      check** — prepare observations, and while it's "pending," confirm the open detail view updates
      to "generated" on its own within ~5s instead of needing a manual reopen.

### Phase 4 — Verify
- [x] `npx tsc --noEmit` — clean after Phase 0 and again after Phase 1-3.
- [ ] Manual pass: upload one file of each accepted type, confirm viewer renders (image, PDF) or
      shows the fallback (docx, xlsx, xls, csv, txt, rtf, md, odt, heic-without-pillow-heif).
- [ ] Confirm `isPending` disables notes-save and the relocated observations actions during a
      simulated device-transfer pending state.
- [ ] Confirm blob URLs are revoked when the detail view closes (open a large PDF/photo, close,
      check no lingering blob: URL / memory growth on repeated open-close).
- [ ] Confirm the timeline card's compact-metadata-only rendering matches non-image documents
      exactly after the observations block is removed from it.

**Bugs found in first click-through (2026-07-10), both fixed:**
1. **Window-drag region leaked into the detail view.** `DocumentDetailView`'s outer `fixed inset-0`
   container was missing `no-drag` — only the header and buttons inside had it. Every other
   full-screen overlay in this app (`App.tsx`'s intercepts) puts `no-drag` on the *outermost*
   covering div, not just an inner header; this one didn't follow that convention. Fixed by adding
   `no-drag` to the outer container in `DocumentDetailView.tsx`. **Needs re-confirmation** at a
   non-maximized window size (where the bug was reported).
2. **Vision-download intercept was invisible while inside the detail view.** The "Drawing & image
   support needed" modal is `z-[60]`; `DocumentDetailView` is `z-[70]`. Since Prepare Observations
   can now be triggered from inside the detail view, the intercept rendered but sat *behind* it —
   invisible until closing the detail view revealed it (matching the reported "only tells you when
   you press Back"). Fixed: bumped the intercept to `z-[80]`. Also improved its copy to mention the
   Notes field as a manual alternative, per feedback. **Needs re-confirmation** — Prepare should now
   show the intercept immediately and every time vision isn't downloaded, not just after Back.

**Second click-through round (2026-07-10) — window-drag fix retried, three more items:**
1. **Window-drag fix #1 didn't work; root cause was different than assumed.** Adding `no-drag` to
   `DocumentDetailView`'s outer container didn't fix it. On inspection, no overlay in this codebase
   has ever actually proven that `no-drag` can override the App-level title bar's `drag-area` from a
   deeply-nested `fixed inset-0` overlay: the 680px `ClientHistoryPanel` slide-over only ever covers
   the *right* side of the screen (never the left app-icon/name area people actually grab), and
   `WorkspaceLockGate` deliberately starts at `top-11` rather than covering + fighting the title bar.
   This repo's own bug history (`bugs-fixed/001-20062026.md`) already flags `-webkit-app-region`
   reliability quirks on Windows. **Fix:** changed `DocumentDetailView` and the vision intercept from
   `fixed inset-0` to `fixed top-11 inset-x-0 bottom-0` — same proven pattern as `WorkspaceLockGate`.
   The title bar (incl. minimize/close) now stays visible and usable while a document is open, which
   is arguably better UX, not just a workaround. **Needs re-confirmation**, same window size as before.
2. **Added a simulated progress bar to the observations "preparing" state**, not in the original
   checklist — requested during testing, styled after `SessionsPage.tsx`'s Beautify prep overlay
   (`computePrepPct`/`startPrepProgress`) but simplified: an eased time-based curve toward a cap, no
   real percentage (there isn't one to poll) and no ETA-history fetch (not tracked for this path).
   Lives entirely in `DocumentDetailView.tsx` (`computeObsPrepPct`, `OBS_PREP_CURVE`).
3. **Fixed "can't Save after generating."** `handlePrepareObservations`'s success handler used to
   *clear* the draft after generation, so Save was correctly-but-confusingly disabled (nothing to
   save) with fresh AI text sitting right there. Now seeds the draft with the generated text instead,
   so Save is immediately clickable (re-saving identical text is a harmless backend no-op).
4. **Added a one-line clarifier under Notes** ("separate from the AI-drafted observations above")
   for image documents, addressing the "wait, another Notes?" moment from having two similar boxes
   stacked — Notes itself is unchanged/staying, per the original locked-in decision.
5. **Tweaked the vision-observation prompt** (`DRAWING_OBSERVATION_PROMPT` in `backend/services/ai.py`)
   — output was accurate but generic/thin. Kept the STRICT RULES (no interpretation/emotion/diagnosis)
   completely unchanged — that's a clinical-safety invariant, not up for revision — but added explicit
   instruction to be descriptively specific rather than generic ("colleague could picture it" framing)
   and to use as many bullets per heading as the visual detail supports. Bumped `max_tokens` 1500→2000
   for headroom. **Session-context-aware richer analysis (feeding session summary in) is explicitly
   deferred** — Jonathan flagged it needs its own separate plan, not done here.

**Third click-through round (2026-07-10) — naming + a second pre-existing drag overlap:**
1. **`ClientHistoryPanel`'s own 680px slide-over was overlapping the title bar's status
   indicators.** Same class of bug as the drag issue, different symptom: the slide-over
   (`fixed right-0 top-0 ... z-50`) starts at `top-0` and is the SAME z-50 tier as the title bar, so
   its header (large client-name text) could paint over the title bar's centre "App services: Ready
   / Writing assistant ready" indicators at non-maximized widths where the 680px panel reaches far
   enough left. This is pre-existing — not something introduced this session — just not noticed
   before. Fixed the same way: backdrop and panel now start at `top-11`, matching
   `DocumentDetailView`/`WorkspaceLockGate`.
2. **Image/document naming no longer assumes "Student."** `DocumentDetailView`'s title used to fall
   back to the raw filename when no label was set; now falls back to `${clientName} — Image` (image
   types) or `${clientName} — Document` (everything else) — a real name works regardless of whether
   the deployment calls the person a client, patient, or student, which a role-noun default can't.
   "Image" not "Drawing": not every image is a hand-drawn artwork (photographed intake forms, ID
   photos, etc. also land here). The original filename now shows as a small subtitle under the title
   whenever it differs from what's displayed. Scoped to `DocumentDetailView` only — the timeline
   card's own `label || original_filename` fallback is untouched, per the original 2026-07-06
   decision that the card stays as-is.
3. **Confirmed (no code needed): documents can't be "unattached."** Unlike sessions
   (`listUnattachedSessions()` exists), `client_documents.client_id` is a mandatory FK — the upload
   endpoint is `POST /api/clients/{client_id}/documents`, reachable only from inside an already-open
   client's profile. There's no walk-in/unattached document path to design a fallback name for.

**Note on the refactor-discipline check:** `fable-refactor-discipline`'s Gate (Step 0) was checked
before Phase 3's move — its Gate and REFACTOR 1-7 list are scoped to the named SessionsPage/App.tsx
architectural initiative tracked in `CODEX-SONNET5-CHECKLIST.md`/`FABLES-REFACTOR-FINAL.md` (hot files:
`ai.py`, `transcribe.py`, `SessionsPage.tsx`, `App.tsx`). This move touched `ClientHistoryPanel.tsx`
and a new file, neither on that list, and was an explicit, user-approved part of this feature (Finding
F2's resolution) rather than an opportunistic reorg — so it proceeded, following the skill's *principles*
(state stayed in the parent, JSX-only relocation, invariants — `isPending` copy, sticky-edited status,
polling — carried verbatim) without waiting on that Gate.
