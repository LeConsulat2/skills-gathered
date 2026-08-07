# Backend Router Reference

Read this file when working on: `backend/routers/license.py`, `backend/routers/transcribe.py`, `backend/routers/documents.py`, `backend/routers/system.py`, license activation/verify flow, client file uploads, reporting/analytics endpoints, purge/backup system endpoints.

---

## license.py — full detail

**Three runtime modes** (controlled by `config.py`):
1. `WEB_API_URL` set → calls `privatespace.co/api/licenses/...` (production — no Supabase credentials in binary)
2. `SUPABASE_URL` + `SUPABASE_ANON_KEY` set → calls Supabase directly (dev/fallback)
3. Both blank → no enforcement (local dev bypass — any well-formatted 16-char key activates)

**Verify statuses:**
- `ok` — allow silently
- `expired` — admin kill switch; **hard block**: user redirected to selection screen, no bypass
- `warning` — soft amber banner, allow access
- `offline` — network failure, allow silently; uses cached `expires_at` from `app_licenses` for the expiry badge

**Activation guards:**
- **409 guard:** if a *different* key is already active for that workspace locally, activation is blocked (prevents one user overwriting another's slot on a shared machine).
- **Cross-workspace guard** (local, no network): if a key is stored in `app_licenses` for a *different* workspace type, activation is blocked with a vague message ("not valid for this workspace").

**Other activation details:**
- `activate` returns `workspace_type` from the server so the app knows which workspace to open.
- `max_devices` is read per key from the server; upgrading a customer from 1→2 devices requires only a Supabase DB update, no code change.
- Activation with expired key on a new device → clear message directing to `privatespace.co/renew`.

**Backend feature gate (`services/license_gate.py`):**
- `POST /api/clients`, `POST /api/transcribe`, `POST /api/ai/beautify`, `POST /api/summarize` return 403 when the workspace licence is >7 days past expiry (same grace window as `isLicenseExpired` in `App.tsx`) or when the admin kill switch was seen.
- Verify persists kill-switch state to `app_licenses.blocked`; cleared on next valid verify or reactivation.
- **UI state alone is NOT the enforcement layer** — never add a licence-gated feature without also calling `require_active_license()` in its router.

**Other:**
- DevTools + default menu accelerators are disabled in packaged builds (`devTools: isDev`, `Menu.setApplicationMenu(null)` in `electron/main.js`).
- Self-service deactivation removed from UI (2026-06-05) — Settings shows "Moving devices? Contact support" (mailto link). Backend `/api/licenses/deactivate` endpoint kept for admin/support use.

> Expiry stages, date-based behaviour, HKEY fallback, offline behaviour: see [LicenseExpiry.md](.claude/commands/LicenseExpiry.md).

---

## transcribe.py — full detail

Audio → Whisper transcription endpoint (`POST /api/transcribe`).

**Current behaviour:** audio file + `_transcript.txt` are both permanently saved to `private_storage/`. This causes backup ZIPs to grow large over time (a 1 hr recording ≈ 20–50 MB).

**Planned fix (MorePlan item 11):** auto-delete the audio file after successful transcription, keep only the `_transcript.txt`. Implementation: `os.unlink(audio_path)` after `model.transcribe()` returns without error.

License gate: gated by workspace — `category == 'meetings'` → Executive license check, otherwise Clinical.

---

## documents.py — full detail

### Feature C — Client documents

Files a client/student provided, attached to a client profile and optionally linked to one session.

**Schema:** `client_id` mandatory, `session_id` nullable (covers initial-form-with-no-session case). `original_filename` is the only copy — disk names are random UUIDs.

**Endpoints:**
- `POST /api/clients/{id}/documents` — multipart; ext allowlist = **pdf/docx/md/png/jpg/jpeg/webp/heic** (narrowed 2026-07-15, bugs-fixed/031: dropped txt/rtf/odt/xlsx/xls/csv — the live code allowlist had drifted broader than this doc's prior 7-type list; gif was removed 2026-07-11). `.md` is download-only (no uploaded-file render path). A **.pdf** upload must also begin with the `%PDF-` signature (content check, defence in depth — not malware detection); other types are extension+size only. Removing an extension blocks NEW uploads only — download/list never consult the allowlist, so already-stored files stay accessible. 50 MB cap; licence-gated via `require_active_license`; rejects (400) once the target `session_id` already has `MAX_DOCUMENTS_PER_SESSION = 5` linked documents (live `COUNT(*)`, no cached counter — see Session Document Groups below)
- `GET /api/clients/{id}/documents` — list (no blobs)
- `GET /api/documents/{id}/download` — decrypts and streams with original filename
- `PATCH /api/documents/{id}` — label, doc_date, session link (`session_id: -1` unlinks; re-linking to a *different* session is also checked against the 5-cap, skipped when `session_id` is unchanged); `observations` field — changed non-empty value flips `observations_status` to `edited` (sticky), clearing resets to `not_generated`; `notes`
- `DELETE /api/documents/{id}`

**Session Document Groups (D12, built 2026-07-11):** documents sharing a non-null `session_id` are treated as one bounded group of at most 5 files with one shared context — grouping key is always `session_id`, never the visible date. The group's context lives on `sessions.document_group_context TEXT` (not per-document) — written via the existing `PATCH /api/sessions/{id}` (dynamic `UPDATE` builder already picks up the field, no new endpoint). The observation-generation endpoint below resolves context from the session when the document is linked, falling back to the document's own `session_context` (Phase A's column) only when unlinked.

**Storage:** `private_storage/client_files/{client_id}/` under random uuid names, **encrypted at rest** (AES-256-GCM, `services/client_files.py` — format `PRIVFILE1` + nonce + ct + tag; fail-open to plaintext with `encrypted=0` flag when no DEK).

The original filename exists only in the `client_documents` row (inside the encrypted DB). Backups include the folder automatically (it's under `private_storage/`), and `db_keys.json` travels in backups so restored files decrypt wherever the DB does.

Deleting a client removes its rows + the entire files folder.

### Feature B — Drawing observations

`POST /api/documents/{id}/observations` (`?force=true` to replace).

- Licence-gated, IMAGE documents only (png/jpg/jpeg/webp; +heic when `pillow-heif` present — **gif removed 2026-07-11**).
- **Never automatic** — explicit button only.
- Pre-checks `is_vision_available()` → 409 + Settings pointer if projector not downloaded.
- Commits `pending` status *before* the model call (crash-safe — startup migration flips orphaned `pending` to `failed`).
- Decrypts the file via `client_files.read_document`, calls `analyze_drawing_service()` with the image + practitioner label + resolved session/document context ONLY — no client name, other documents, or private notes. Output is rendered client-side as two parts (Visible Observations / Questions & Connections to Explore) split from one stored `observations` field — see `DocumentDetailView.tsx`.
- Writes `generated` / `failed`. On `finish_reason == "length"` (model ran out of token budget mid-answer) the result is treated as failed, never saved as a complete draft (D14.2).
- Sticky-edited: non-force returns `{status:'already'}` when text exists or was hand-edited.
- Concurrency: per-document `pending` status prevents double-triggering the same document; a *sibling*-in-group guard (only one document per session group generating at a time) is frontend-only (`siblingObsBusy` in `ClientHistoryPanel.tsx`).

---

## system.py — full detail

Major endpoints in `backend/routers/system.py`:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Backend liveness check |
| `POST /api/ai/download` | Download model or mmproj; SSE progress stream |
| `GET /api/ai/status` | Installed model info, `vision_available`, `any_vision_available` |
| `GET /api/ai/model-options` | All AVAILABLE_MODELS entries |
| `POST /api/ai/switch-model` | Switch active model (restarts llama-server) |
| `GET/POST /api/settings` | Workspace key/value settings (`client_id_label`, `require_client_id`, section labels) |
| `GET /api/analytics/trend` | Session/meeting counts by period, accepts `offset` for prior-period navigation |
| `GET /api/analytics/by-client` | Per-client session stats |
| `GET /api/analytics/client/{id}` | Single client drill-down |
| `GET /api/analytics/reporting-pending` | Completed sessions still owing a reporting summary |
| `POST /api/backup/create` | Manual backup (returns 400 with reason if no license) |
| `POST /api/backup/auto` | Event-triggered backup (returns silent `{status:"skipped"}` if no license — never error noise) |
| `GET /api/backup/list` | List backup archives |
| `DELETE /api/backup/{filename}` | Delete one backup |
| `POST /api/backup/restore/{filename}` | Restore from backup ZIP |
| `POST /api/system/purge` | Institutional wipe — requires confirmation phrase |
| `GET /api/system/encryption-status` | DB + file encryption state |
| `GET/POST /api/session-categories` | CRUD for reporting category list |
| `PATCH /api/session-categories/{id}` | Rename and/or activate/deactivate a category |
| `DELETE /api/session-categories/{id}` | Delete a category — 409 if any session still references it (deactivate instead) |
| `POST /api/session-categories/reorder` | Drag-reorder categories |
| `POST /api/session-categories/restore-defaults` | Reset to `DEFAULT_SESSION_CATEGORIES` |
| `GET /api/reports/insights` | .xlsx export (instant, reads stored values only) |
| `POST /api/reports/insights/generate` | Queue reporting summary generation (sequential) |
| `GET /api/reports/insights/generate-status` | Poll sequential generation queue |
| `GET /api/whisper/status` | Whisper model download state |
| `POST /api/whisper/download` | Download "Higher Accuracy" Whisper model |
| `DELETE /api/whisper/delete` | Delete downloaded Whisper model |

**Analytics note:** bucketed by the session/meeting **`date`** field with `created_at` fallback. `sessions.date` is a display string — all date logic parses in Python (`_parse_insights_date`), never SQL string comparison.
