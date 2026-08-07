The current Add document / assessments flow only saves the uploaded file, but I think it should behave more like opening a proper document record.

Instead of just uploading and saving, clicking Save Document should create the document and then open a dedicated page, something like:

students/{id}/documents/{document_id}

On that page, the user should be able to:

view the uploaded document
see the document date
see whether it is linked to a session
add or edit notes about what the document is
save those notes

So the workflow would be:

Go to client profile
Click Add document
Upload intake form / assessment / referral / photo / other document
Save it
App opens the document detail page
User can review the uploaded file and write notes underneath

The note area should be reasonably large, because the user may want to write context such as:

“Initial intake form provided before first session. Includes presenting concerns, risk history, GP details, and consent information.”

So basically: Add document should create a viewable document page, not just silently save a file into history.

---

## Decisions (locked in 2026-07-06, not built yet)

- **Notes = a new field**, separate from the existing `label` column. `label` stays as-is (the short
  title shown on the timeline card, falls back to `original_filename`). The new field is for longer
  free-text context, e.g. the intake-form example above.
- **Timeline card stays as-is** — the compact document card in the client profile's timeline keeps
  showing title/date/file type/size/encrypted badge/download/delete/session-link exactly as it does
  today. The document detail page is additional, not a replacement — reached both right after Save
  Document and by clicking the card afterwards.
- **Layout**: the document itself is the star of the page — a large rendering of the actual file up
  top (not a thumbnail), with the notes textarea as a secondary panel underneath it. Document date
  and session link are small metadata near the top, not competing for space with the file view or
  the notes area.
- **No URL router in this app** (no `react-router-dom`) — navigation is `view`/`activeTab` state in
  `App.tsx`. So `students/{id}/documents/{document_id}` describes the *shape* of the feature, not a
  literal route — it'll be a state-driven full view/overlay, same pattern the rest of the app uses.
- **Biggest net-new piece**: there is currently no in-app document viewer at all — today's Download
  button just fetches-and-saves the file, nothing renders it inline. Images can use a blob URL
  `<img>`; PDFs an `<iframe>`/`<embed>` with a blob URL; other types (docx etc.) likely still fall
  back to download-only, same as today.

## Decisions (locked in 2026-07-10, fable-mode assessment, not built yet)

- **Presentation = new full-bleed overlay**, not the existing 680px `ClientHistoryPanel` slide-over
  and not the existing centered intercept-modal shape (batch-beautify config, vision add-on prompt,
  update-required block — all `max-w-xl`/`80vh` or similar, sized for "answer this, then get out of
  the way," not for lingering on a document). `fixed inset-0`, above the slide-over's `z-50` and the
  vision-intercept's `z-60` (e.g. `z-[70]`), since it opens from inside `ClientHistoryPanel` and must
  sit on top of it. Local component state (`openDocument: ClientDocument | null`), not a new
  `view`/`activeTab` — that machinery is workspace/tab level, this is scoped inside one open client.
  Closed via back arrow/X back to the slide-over/timeline.
- **Drawing Observations (Feature B) moves into this view.** The existing image-only
  Prepare/Save/Insert/Regenerate block (`ClientHistoryPanel.tsx` timeline card, ~lines 761-870)
  relocates into the new detail view alongside the manual notes field — one home for all
  per-document actions. The timeline card shrinks back to compact metadata-only (matching how
  non-image documents already render there).
- **PDF rendering must be spiked first, before any layout work.** `electron/main.js`'s
  `BrowserWindow` has no `plugins: true` in `webPreferences` — Electron gates its bundled PDFium
  viewer behind that flag, so a blob-URL `<iframe>`/`<embed>` may not render a PDF inline by default
  (could trigger a download instead). Confirm empirically before building the surrounding page.
- **Auth requires fetch-as-blob**, not a plain `<img src>`/`<iframe src>` against the API URL —
  every document endpoint requires the `X-Local-Token` header. Reuse/refactor
  `api.downloadClientDocument()`'s fetch pattern into a shared blob-fetch helper for both Download
  and inline viewing, but give the viewer its own revoke-on-close lifecycle (the existing helper
  hardcodes a 10s auto-revoke, fine for save-to-disk, wrong for something rendered on screen).
- **`isPending` (device-transfer read-only mode) must gate notes-save and any relocated observations
  actions** in the new view, same as it already gates upload/generate in `ClientHistoryPanel` today.

### Execution order

1. **Schema + API** — `client_documents.notes TEXT` column (mirror the `observations` column
   migration pattern in `database.py`), `DocumentUpdate.notes`, PATCH handling, TS interface.
2. **Viewer spike** — confirm image + PDF blob-URL rendering work in this Electron config before
   writing any component; resolve the `plugins: true` question if PDFs don't render.
3. **Detail view + entry points** — full-bleed overlay (metadata → file render → notes textarea);
   wire Save Document to auto-open it; wire timeline-card click to reopen it; non-renderable types
   (docx, xlsx, csv, ...) get an explicit "no inline preview, use Download" fallback state.
4. **Relocate Drawing Observations** into the new view; shrink the timeline card.
5. **Verify** — `npx tsc --noEmit`, manual pass per file type, confirm `isPending` gating, confirm
   blob URLs get revoked on view-close.
