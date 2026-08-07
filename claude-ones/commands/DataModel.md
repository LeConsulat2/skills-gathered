# Data Model — localStorage Keys & SQLite Schema

Reference for the two storage layers. Summary + invariants live in `CLAUDE.md`; this is the full lookup.

---

## localStorage Keys

| Key                                | Type                          | Purpose                                                                                                                                                                                                                               |
| ---------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `private_whisper_model`            | string                        | Whisper weight size (`tiny`/`base`/`small`/`medium`)                                                                                                                                                                                  |
| `private_section_labels_counselor` | JSON string (4-item array)    | Custom clinical note section labels                                                                                                                                                                                                   |
| `private_setup_welcome_{view}`     | `'shown'`                     | One-time: first-entry welcome modal per workspace (never shown again once set)                                                                                                                                                        |
| `prefill_status_filter`            | `'draft'`                     | One-shot handoff: pre-filters session/meeting list to drafts                                                                                                                                                                          |
| `prefill_session_id`               | string (number)               | One-shot handoff:`ClientHistoryPanel` → `SessionsPage` to pre-select a specific session in the editor                                                                                                                                 |
| `prefill_append_note`              | string                        | One-shot handoff riding along with `prefill_session_id` ("Insert into session note" on a drawing's observations): text appended to the loaded session's working draft. Always written and consumed together with `prefill_session_id` |
| `pending_meeting_title`            | string                        | One-shot handoff: pre-fills new meeting title from scheduler                                                                                                                                                                          |
| `prefill_open_bulk_audio`          | `'1'`                         | One-shot handoff: Home "Untranscribed Audio" card →`SessionsPage` auto-opens the bulk-transcribe window onto the retained pending audio                                                                                               |
| `prefill_open_meetings_audio`      | `'1'`                         | One-shot handoff: Home "Transcribe Recordings" card (meetings view) → `MeetingDashboard` auto-switches to Audio tab and shows the retained queue                                                                                      |
| `prefill_open_reporting`           | `'1'`                         | One-shot handoff (rides with `prefill_session_id`): Home "Prepare summary →" → `SessionsPage` opens the reporting (digest) panel and briefly highlights its Prepare button so the counsellor lands right on it                        |
| `private_last_workspace`           | `'counselor'` \| `'meetings'` | Auto-login: set when entering a workspace via `navigateTo()`, cleared when clicking "Exit Portal". On next launch, `App.tsx` reads this and calls `checkLicense` — if still active, skips the picker and navigates straight in.       |
| `private_last_verify`              | ISO string                    | Timestamp of the last `verifyLicense` result (any status, incl. offline); written by `App.tsx`, read by the Settings → Privacy & Data Security panel as "last licence check".                                                         |
| `private_move_in_progress`         | `'counselor'` \| `'meetings'` | Device-transfer (old laptop): set when "Move this licence to a new device" releases the slot. **UX state only, never an auth signal** — drives `SelectionPage`'s "move in progress / re-enter key to cancel" screen. Cleared on cancel-reactivation or after erasing the device.                                                                                                |
| `private_move_cancelled`           | `'1'`                         | One-shot handoff: set when re-activating cancels an in-progress move; `App.tsx` consumes it once to show the soft "welcome back — your move was cancelled" toast.                                                                     |

**One-shot handoff pattern:** the producing page sets the key; the consuming page reads and deletes it on mount.

**Configurable Section Labels** (`private_section_labels_counselor`): defaults `Client's Account / Observations / Impression / Next Steps`. **Unused by Phase 1 sessions** (Beautify produces one block, not four) — kept for: (1) legacy 4-section session migration on load (`legacyToBeautified` in `SessionsPage.tsx`); (2) future template-driven Beautify heading scaffolding. Helpers: `getSectionLabels()` + `DEFAULT_SECTION_LABELS` from `src/utils/api.ts`.

**DB-backed workspace settings** (NOT localStorage — they back up and sync) live in the `settings` table via `GET/POST /api/settings`: `client_id_label` (string) and `require_client_id` (`'true'`/`'false'`, treated as required unless `'false'`).

---

## SQLite Schema (Tables)

| Table                | Purpose |
| -------------------- | ------- |
| `counselor_profile`  | Per-workspace settings; one row per `workspace_type` (`'counselor'` / `'meetings'`) |
| `clients`            | Client/student profiles; `first_name`+`last_name` → `name`; configurable `student_id`; `nhi_number`; GP/referral fields; `holistic_summary` |
| `sessions`           | Per-client clinical notes; `soap_*` fields; `counselor_private_notes` (sandboxed, never sent to AI); `session_type` (`'standard'`/`'walk-in'`/`'urgent'`/`'crisis'`/`'group'`/`'other'` + free-text `session_type_other`); `take_away_*` lifecycle columns mirroring reporting-summary |
| `meetings`           | Admin meeting notes; `transcript`, `summary`, `action_items` |
| `calendar_events`    | Unified scheduler; `category` = `'standard'` / `'meeting'`; `client_id: null` required for meeting events |
| `client_documents`   | Client files (Feature C) + drawing observations lifecycle (Feature B); `session_id` nullable; disk names are random UUIDs; encrypted at rest in `private_storage/client_files/{client_id}/` |
| `document_templates` | Uploaded `.docx`/`.pdf` templates; `category` locks to workspace; `extracted_schema` (JSON) holds AI-read structure |
| `settings`           | DB-backed per-workspace key/value (`client_id_label`, `require_client_id`); backs up and syncs, unlike localStorage |
| `session_categories` | Configurable reporting categories (Settings-managed); only `is_active` rows used for generation; retired rows kept for history |
| `app_licenses`       | One row per `workspace_type`; `license_key`, `machine_fingerprint`, `expires_at`, `blocked` (admin kill switch — persisted offline), `last_verified_at`, `license_mode` (`'active'`/`'pending'` device-transfer slot mode; written on activate/verify/finalize/cancel, read via the fingerprint trust rule) |

> Full DDL for every table, the ALTER-TABLE migration history, and a relationships/purge reference: [`sqls/app-schema-update.sql`](../../sqls/app-schema-update.sql) (a learning mirror — the real schema is built by `database.py:init_db()`).
