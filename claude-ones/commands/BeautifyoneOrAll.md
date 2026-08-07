# Beautify System — Single & Batch

All implementation lives in `src/pages/SessionsPage.tsx`.

---

## Architecture decision: sequential only, no parallel

Even with llama-server (llama.cpp binary), CPU-only hardware executes tokens sequentially. `--parallel` just interleaves slots — total throughput is the same but each session takes N× longer individually. Sequential wins: session 1 finishes in ~60s and the counsellor can start reviewing, rather than all 4 finishing at ~240s simultaneously. The old `BATCH_CAP = 4` was removed — no artificial limit, all drafts queue.

---

## Single beautify — background detach

**Problem solved:** if a counsellor starts beautifying session X then navigates to another session/client, tokens were landing in the wrong editor. Now it auto-saves to the original session.

**Key state/refs:**
- `hasBackgroundBeautify: boolean` — hides the Beautify button and shows "Structuring a previous note…" spinner while a detached run is in progress
- `activeBeautifyRef` — holds the current run's context object (or null)

**Run context object** (captured per `beautify()` call, local closure):
```typescript
{
  sessionId?: number          // DB id of original session, if saved
  sessionSnapshot: Session | null
  clientId: number | null
  titleSnapshot: string
  transcriptSnapshot: string
  accumulated: string         // tokens accumulate here always
  updateEditor: boolean       // flipped false on navigation → stops state updates
}
```

**`detachBeautifyIfRunning()`** — call at the top of any function that navigates away from the current session. Currently wired into: `handleSelectSession`, `handleNewSession`, `handleNewWalkinDraft`, `handleReturnToDraft`. Flips `updateEditor = false`, sets `beautifying = false`, sets `hasBackgroundBeautify = true`.

**On completion (detached path):**
- Saved session → `api.updateSession(sessionId, { ...snapshot, soap_subjective: accumulated, soap_objective/assessment/plan: '' })`
- Unsaved draft → `api.createSession({ client_id, title, transcript, soap_subjective: accumulated, status: 'draft' })`
- Calls `loadDisplaySessions()` to refresh sidebar
- Toast: "Note saved in background — find it in the session list to review." (7s)

**On completion (normal path — counsellor stayed):**
- `setEditorResetKey` syncs TipTap, `showBeautifyDone` modal fires (16s auto-dismiss)
- Counsellor must manually save (Save as Draft / Mark Complete)

**Button states:**
- `beautifying = true` → shows "Polishing notes…" + Stop button
- `hasBackgroundBeautify = true` → shows "Structuring a previous note…" (no Stop, Beautify disabled)
- Neither → shows normal Beautify Source → button (disabled if no transcript or license expired)

---

## Batch beautify — intercept modal

**Trigger:** "Beautify All Drafts (N)" button in the left sidebar. Disabled when `isRecording = true` (tooltip: "Stop recording before running batch note structuring"). Disabled when single `beautifying = true`.

**`openBatchIntercept()`** — gate function. Checks AI model available, builds sorted queue (oldest draft first), opens modal in configure phase.

**`BatchQueueItem` interface:**
```typescript
{ session: Session; templateId: string; status: 'pending'|'running'|'done'|'error'; selected: boolean }
```

**Intercept modal — configure phase:**
- Drag-to-reorder rows (HTML5 drag, `batchDragIndexRef`, `dragOverIndex` highlight)
- Checkbox per row (deselect to skip this run)
- Template dropdown per row: No Template / PRIVATE Workspace / any org template with `extracted_schema`
- Word count hint (`~N words`) from `wordCount(transcript)`
- Default template: PRIVATE Workspace, default order: oldest first
- "Start Structuring (N notes)" → calls `handleBatchBeautify()`

**Intercept modal — running phase (modal transitions in-place):**
- Status icon per row: spinner (running) / ✓ (done) / ○ (pending) / alert (error)
- "Open →" on completed rows → `handleSelectSession(target)` + closes modal
- "View" button in sidebar progress bar reopens modal while running
- Footer: "Running in background — safe to close" or "All done"

**`handleBatchBeautify()` loop:**
- Processes only `item.selected === true` items, in queue order
- Template resolved via `resolveAiSchema(templateId)`: `'none'`→`[]`, `'private'`→`null`, org id→parsed schema
- Per session: `api.beautifyNotes(transcript, aiSchema, ...)` → `api.updateSession(id, { ...session, soap_subjective: result, soap_objective/assessment/plan: '' })`
- After each save: `loadDisplaySessions()`, `setBatchDoneIds`, sidebar card shows "Ready to edit" badge
- **Completion toast** (10s, top-centre of main editor): "**ClientName** — Session Title is ready to review" with × dismiss. Uses `batchToastTimerRef` to clear previous timer.

**Sidebar during batch run:**
```
[spinner] Structuring X of Y…  [View]
```

**`resolveAiSchema(templateId)`** — shared helper used by both single and batch:
- `'none'` → `[]` (free-form prose, backend detects empty array)
- `'private'` or empty → `null` (PRIVATE_DEFAULT_SCHEMA in ai.py)
- org template id → `JSON.parse(template.extracted_schema)` or `null` on parse failure

---

## Interaction rules summary

| Scenario | Behaviour |
|---|---|
| Single beautify, counsellor stays | Streams live, manual save required |
| Single beautify, counsellor navigates away | Auto-saves to original session, toast on completion |
| Batch beautify running, counsellor navigates | Safe — saves directly to DB, unaffected by editor state |
| Recording active, click Beautify All | Button disabled (tooltip explains why) |
| Recording active, click single Beautify | Allowed — separate processes, no conflict |
| Background beautify running, click Beautify | Button hidden — "Structuring a previous note…" shown instead |
| Two batch runs simultaneously | Not possible — button hidden while `batchRunning = true` |
