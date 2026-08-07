# Emergency Hard-Deactivate ("revoked" licence state) + Admin UI — FINAL BUILD PLAN

**Status: final, signed off 2026-07-06. Desktop backend + desktop frontend BUILT + verified. Web side: schema migration written (`sqls/schema-hard-device.sql` — copy of the web project's `schema-hard-revoke.sql`; not yet run in Supabase) and the `verify`/`activate`/`finalize`/`cancel-transfer` route changes DONE + tsc-clean (see Appendix B). Admin dashboard + `hard-deactivate`/`reactivate` admin routes POSTPONED (2026-07-06) — direct Supabase SQL one-liners (`schema-hard-device.sql` §3) are the v1 admin path. Remaining: run the migration in Supabase + merge/deploy the web routes, the live web + §8 desktop drills, and docs.**

## Current Status (read this first when resuming)

- **Branch**: `performance-optimization` in `private-test-claude` (desktop repo). **Web side (`private-test-web`)**: no longer untouched — the schema migration is written (`sqls/schema-hard-device.sql`, brought into this repo for reference; not yet run in Supabase) and the `verify`/`activate`/`finalize`/`cancel-transfer` route changes are done + tsc-clean (Appendix B). The admin dashboard + `hard-deactivate`/`reactivate` admin routes are **postponed** (Jonathan's call, 2026-07-06) — raw Supabase SQL is the admin path at the current tiny user count.
- **Done**: the entire "Desktop backend" section of Appendix B's checklist (all boxes ticked) — DB column, `db_keys.scrub_dpapi`/`rewrap_dpapi`, `_set_revoked`, verify branch + healthy-clear + offline-priority + `check_license` + dedup'd outcome logging, the activate-path recovery gate (incl. online-required-when-locally-marked rule) + elif branch, `RevokedMiddleware` + startup wiring, `reset_pin` refusal. Also **all of §5 Desktop frontend** (Appendix B checklist fully ticked): `LicenseVerifyResult.status`/`LicenseStatus.revoked` types in `src/utils/api.ts`; `src/App.tsx` — verify-effect `revoked` branch (copy does not claim records are accessible), a 10-min `setInterval` poll reusing the same verify handler *(**deleted 2026-07-10** — see the no-polling bullet below; the same handler is now driven by focus/visibility/wake/reconnect events)*, auto-login stops navigation on `res.revoked` (stays on `selection`, does NOT clear `private_last_workspace`), full-screen dark hard-block overlay (distinct from the sky-blue `updateRequired` block) for the case where revoke lands mid-session; `src/pages/SelectionPage.tsx` — distinct dark/slate revoked banner (never rose/amber) driven by the same state, **plus a fix found during live testing**: `handleMeetingsEntryClick`/`handleCounselorEntryClick` now check `res.revoked` and refuse via a new `onRevoked` callback prop instead of opening the reactivation-key modal (this closes a click-through gap the plan didn't call out — clicking the workspace card while the auto-login banner was showing used to fall through to the setup/entry flow). 8 commits total on the branch so far (5 backend + 3 frontend).
- **Verified**:
  - Backend: 67/67 assertions in a throwaway offline test harness (scratch DB, `http.post` monkeypatched — web side isn't live) covering every backend-testable item in §8, including the soft-block regression and the "blocked ≠ revoked" invariant. Script was scratch-only, not committed.
  - Frontend: `npx tsc --noEmit` clean after every sub-step. Additionally **live-drove the actual running app** (backend + Vite dev servers + a headless Edge instance scripted via raw CDP over Node's native WebSocket — no new npm deps added) against Jonathan's real dev DB: took a full backup of `backend/local_private.db` + `backend/db_keys.json` first, temporarily cleared the PIN to get past the lock screen (real dev PIN was unknown), flipped `app_licenses.revoked` for the existing `counselor` row directly via `database.get_db_connection()`, and confirmed — (a) normal auto-login/PIN/workspace-entry flow is unaffected when `revoked=0`, real client data loads fine; (b) with `revoked=1`, a full page reload correctly stops auto-login before entering the workspace and shows the dark "This workspace has been deactivated…" banner on SelectionPage, `private_last_workspace` stays set; (c) clicking the workspace card while that banner is showing now correctly refuses (post-fix) instead of opening a modal; (d) flipping back to `revoked=0` and reloading restores completely normal behaviour. Backend + DB + PIN were fully restored from the pre-test backup afterward and all dev processes were cleanly killed — confirmed via `git status` that only the intended source files are modified. This was **not** a full drill of §8 (web side still isn't live, so the `verifyLicense`-driven mid-session re-verify/overlay and the online-required recovery gate couldn't be exercised end-to-end in dev — the dev "no-config" bypass in `_verify_license_impl` always returns `{"status":"ok"}` regardless of the local `revoked` flag, only `checkLicense()` reads it directly). Scratch driver script, not committed.
- **Not started**: docs/runbooks (§10 step 5); running the migration against live Supabase + merge/deploy of the web routes; and the full §8 / Web verification drills that need a live web side (soft-block regression, live-session hard-deactivate drill, restart drill, offline-recovery refusal drill, reactivation drill, full runbook drill). *(The admin dashboard is not on this list — it is postponed by decision, not pending; SQL one-liners cover admin actions for v1.)*
- **Next single step**: on the web side — merge/deploy the `verify`/`activate`/`finalize`/`cancel-transfer` route branch and run `schema-hard-device.sql` against live Supabase (both are that SQL file's own pre-checks). Then run the prepared end-to-end drill (the "내일 할거"/tomorrow section at the bottom of that SQL file — throwaway key `CLIN-TEST-DRIL-0001`, covers §8 items 4/5/7/8 against the real deployed routes), then the remaining §8 desktop drills, then docs (§10 step 5). The admin dashboard/admin routes are off this path (postponed — SQL one-liners cover admin actions).
- **Working style**: go slowly, one sub-stage at a time, commit at each checkpoint (not squashed), verify before moving on — this was explicitly requested and worked well for both the backend and frontend stages.
- **2026-07-09/10 additions** (doc of record for both: `bugs-fixed/024-07072026.md`): (a) live drills against the deployed web side found + fixed the reactivation dead end — `activate_license()`'s recovery-unlock gate now clears the revoked flags itself after an explicit online `valid` precheck (Addendum 2); (b) **Live Hard-Revoke Kill Switch Phase 1 BUILT, then the polling half REVERSED the same day** — see (d); (c) §6.1 added — the concrete SQL-era stolen-laptop support-call runbook.
- **2026-07-10 (evening) — NO LICENCE POLLING. Read `bugs-fixed/024-07072026.md` "Addendum 3" before touching any of this.** Jonathan's product ruling: PRIVATE is a local desktop app and must never contact `privateworkspace.co` on a timer. The 25 s poll was **deleted** (not re-lengthened; the old 10-minute poll is gone too). Licence verification is now purely event-driven — startup/workspace entry, window focus, tab visibility, **OS wake from sleep** (new: Electron `powerMonitor` → `system-resumed` IPC), **network reconnect** (new: `window 'online'`), Settings mount, and the explicit online licence operations (activate/finalize/cancel-transfer/recovery). One request at a time (`verifyInFlight`), rate-limited to one per 15 s — but only a request the server actually *answered* starts that cooldown, so a reconnect always gets through. Also hardened: a 5xx, an unparseable body, or an unknown status from the licence server now returns the cached local state instead of a bare `{"status":"ok"}` — previously an upstream outage could silently clear a cached admin block, drop the revoked overlay, or promote a `pending` device-transfer machine to `active`. **Phase 2 (Supabase Realtime / relay push) is now out of scope**, not merely unbuilt: a permanently-held cloud connection is the same dependency the poll removal rejects. The **honest guarantee** is: *PRIVATE remains fully local and offline-capable; a Hard Deactivated installation is blocked the next time it performs a successful online licence verification (startup, focus/wake, reconnection, activation, recovery, or transfer-related verification).* Never claim a bounded revoke latency, continuous checking, or knowledge of when a thief opened the app.

This revision **replaces** the 2026-07-05 design-discussion version of this file (full rationale — PART 0 plain-English walkthrough, encryption background, tier analysis, open decisions — recoverable via git history of this path) and **supersedes** `AdminEverything-Update.md` and `AdminEverything-GPT.md`. Where this document contradicts any earlier draft, this document wins. Every file/line anchor below was verified against the live code on 2026-07-06.

---

## 1. Context

Today's only admin kill switch (`licenses.status = 'blocked'`) was built for missed-payment cases: by design it never blocks reading/exporting existing clinical data and never touches the local database encryption key. For a genuinely lost/stolen laptop that's not enough — a thief who gets past Windows login can still open everything, because the silent-unlock ingredient (the DPAPI wrap in `db_keys.json`) sits on disk untouched.

This plan adds a second, stronger admin action — **Emergency Hard-Deactivate** — that makes a specific licence stop working on that laptop even though the key and machine are both technically correct. It is **reversible**: a mistaken trigger costs the real counsellor one re-entry of their licence key after admin reactivation, not lost work.

The three-state model:

| State     | Meaning                          | Data access | DPAPI key | Recovery unlock with key |
|-----------|----------------------------------|-------------|-----------|--------------------------|
| `active`  | normal                           | full        | intact    | allowed                  |
| `blocked` | soft billing/admin pause         | read/export stays open; new work gated | intact | **allowed** (load-bearing) |
| `revoked` | emergency hard-deactivate        | all stored-data routes blocked | scrubbed | **online-required** (refused offline and when server says revoked; only a server `valid` after reactivation unlocks) |

`blocked` and `revoked` must never be confused — in code, in the admin UI, or in support copy.

### Already built — nothing to do

- **Temporary 2–3 device allowance**: `POST /api/admin/licenses/set-max-devices` exists in the web project, with the server-enforced rule that the old device must be revoked before lowering back to 1.
- **Admin dashboard**: `private-test-web/app/dashboard/page.tsx` (gated by `ADMIN_SECRET`, unlinked from public nav) already has block/unblock, set-max-devices, revoke-device, override-cooldown, clear-transfer-state. This feature would add **two more actions to that panel**, not a new page — but that dashboard work is **postponed** (see §3.5 / §9); raw Supabase SQL is the v1 admin path.

### Honest security limit (state plainly in every runbook; never oversell)

If a thief has the laptop **and** the exact licence key string, and writes their own offline tool re-implementing the documented PBKDF2+AES-GCM recovery unwrap against `db_keys.json` — never touching our app or network — no server-side action can stop them. The licence key is currently also a local recovery secret; treat it like a password. This plan closes the realistic path: a thief who uses the actual PRIVATE app. Once revoked, our own app refuses to unlock with that key even typed correctly — and once the revoke has *landed* on the device (marker written), going offline no longer helps either: a locally-marked machine's recovery unlock is online-required (§4.3). What remains open is only the device that never checks in at all, plus custom forensic tooling. (Full attacker-by-attacker breakdown: Appendix A.)

---

## 2. Decision log — how this Final differs from the earlier drafts

Adopted from the second-opinion review (real gaps in the Update pass):

1. **Recovery-unlock gate fires on `revoked` only — never `blocked`.** The Update doc's "revoked/blocked" wording would have made a billing-lapsed licence unable to recover a backup onto a new machine, violating the app's own rule that blocked never blocks access to existing data. Implement as a **literal `status == "revoked"` check**. The wire protocol makes this inherently safe: the web routes map DB `blocked` to wire `"expired"` (verify/route.ts:78-80, activate/route.ts:97-99), so a literal `"revoked"` comparison can never catch a blocked licence.
2. **The in-memory flag flips synchronously inside the verify branch, not just at startup.** Tier 1's whole point is shutting down a live, already-open session the moment a revoke lands. `security.set_revoked(True)` is called inside `_verify_license_impl()`'s revoked branch; `security.set_revoked(False)` on the healthy `valid` branch. Startup initialization alone would defer the blackout to next restart.
3. **`activate_license()`'s status elif-chain needs its own `revoked` branch.** The existing chain (license.py:409-437: `invalid_key` / `device_limit` / `expired` / `error` / `cooldown`) has no `revoked` arm — a revoked key hitting a normal fresh activation would fall into the generic `web_status != "activated"` → 503 "Unexpected response". This is a separate fix from the recovery-gate (which handles the locked-DB path earlier in the same function).

Final-review corrections (founder sign-off pass, 2026-07-06):

4. **A machine that already knows it is revoked must not self-recover offline.** The earlier recovery-gate wording let *any* network failure fall through to the offline local unlock. That preserves legitimate offline restores — but it also let a thief defeat the whole feature: revoke lands → DPAPI scrubbed + `"revoked": true` marker written → thief disconnects the internet → enters the original key → offline fallback unlocks the DB → `rewrap_dpapi` clears the marker. Fixed rule (§4.3): offline fallback is allowed **only when the local machine is not already marked revoked**; a locally-marked-revoked machine's recovery unlock is **online-required** and refuses when the server is unreachable. Normal offline restore is untouched.
5. **Never reactivate a licence globally while the stolen device still holds an active device row.** The earlier runbook reactivated before revoking the old device's activation row — if the stolen laptop hadn't yet checked in, it could come online after reactivation and see `active` instead of `revoked`. Runbook reordered (§6): revoke the old device row *before* the licence is reactivated.

Rejected (from the GPT doc):

- **Extra audit columns** (`revoked_by`, `reactivated_at/reason/by`): skipped. `license_events` already records actor/machine/note/old/new for every admin action (see `logEvent()` in activate/route.ts:36-56); block/unblock don't have `_by` columns either. One audit trail, not two. Only `revoked_reason` + `revoked_at` are added (mirroring the existing `blocked_reason`/`blocked_at` pair).
- **"Issue a replacement key" as the key-compromised fix**: kept in the runbook but with the gap stated honestly — backup ZIP passwords are PBKDF2 of whichever licence key created them (`backend/services/backups.py`, Step-2 format), so a new key does **not** retroactively re-encrypt the counsellor's existing USB backups. Those still open with the old, compromised key. Half-solved until the key-rotation feature exists (§9).

Superseded from this file's own previous revision:

- **`verify_pin()` no longer needs a revoked check** (old PART C item 3): the RevokedMiddleware doesn't allow-list `/api/security/`, so the unlock endpoint itself 403s while revoked — a correct PIN cannot bypass the revoke, with zero changes to PIN code. Do not re-add the verify_pin change.
- **Purge is NOT reachable while revoked in v1** (reverses old decision E7): the middleware allow-list stays minimal. Erase-on-checkin can be added later if an org contract demands it; the interim path is revive → purge → re-revoke.

New findings from final code verification (2026-07-06):

- `_log_verify_outcome()` (license.py:544-566) has **no branch that would log a `revoked` outcome** — it must gain one, alongside the outcome-change dedup cache. Logged as `outcome="revoked"`, `error_code="license_revoked"` — both are new values that must be added to the bounded frozensets in `services/activity_log.py` (`OUTCOMES` :50-53, `ERROR_CODES` licence group :70-71); these are Python-side allowlists, and an unknown outcome silently coerces to `"completed"`, so the frozenset additions are required.
- Electron's `before-quit` backup calls `/api/backup/auto`, which is deliberately NOT on the revoked allow-list → it 403s while revoked. A 403 is a response, so app close proceeds without the 10s timeout hang. Deliberate: a stolen machine should not mint fresh backup ZIPs. Covered in verification (§8, item 14).

---

## 3. Web side (`private-test-web`)

### 3.1 Schema migration — new file `supabase/schema-hard-revoke.sql`

- Widen the `licenses.status` CHECK constraint to `('active','blocked','revoked')`. **Confirm the live constraint name first** (`SELECT conname FROM pg_constraint WHERE conrelid = 'licenses'::regclass;`) — don't assume the generated name before `DROP CONSTRAINT`.
- `ADD COLUMN IF NOT EXISTS revoked_reason TEXT, revoked_at TIMESTAMPTZ`. Nothing else (see §2 rejections). Reason text must never contain PHI.
- No changes to `admin_license_overview` (selects `l.status` raw, no status filter — revoked rows flow through) or to `detail/route.ts` (`select("*")` picks up the new columns).

### 3.2 `app/api/licenses/verify/route.ts`

Immediately after the `status === "blocked"` → `{status:"expired"}` block (lines 78-80), **before** slot-mode resolution (line 82+):

```ts
if (license.status === "revoked") {
  return Response.json({ status: "revoked", message: "This licence key cannot be used. Contact support." })
}
```

Revoked wins regardless of fingerprint match — it must never fall through into mode resolution. Update the top JSDoc (which currently documents `expired` as "ADMIN KILL SWITCH ONLY") to document the three-state model.

### 3.3 `app/api/licenses/activate/route.ts`

Same early-exit immediately after the blocked check (lines 97-99) — this runs before the single-seat/multi-seat split (line 106), so one addition covers both models:

```ts
if (license.status === "revoked") {
  return Response.json({ status: "revoked", message: "This licence key cannot be used. Contact support." })
}
```

Note: revoked keys are *valid* keys (found in DB) so they never hit the invalid-key rate limiter — no interaction there.

### 3.3a `finalize` / `cancel-transfer` routes (addition found during the web build)

Same early-exit as §3.2/§3.3, applied to the device-transfer endpoints so a revoked licence cannot complete or cancel a transfer:

- `app/api/licenses/finalize/route.ts` — refuse `revoked` before completing the transfer.
- `app/api/licenses/cancel-transfer/route.ts` — refuse `revoked` before cancelling.

Both return the same `{ status: "revoked", message: "This licence key cannot be used. Contact support." }` shape. Built + tsc-clean (Appendix B); they complete the "revoked wins on every licence path, not just verify/activate" invariant.

### 3.4 New admin routes (mirror `block/route.ts` / `unblock/route.ts` exactly) — POSTPONED (2026-07-06)

> Deferred with the admin dashboard (§3.5 / §9). These two routes exist only to back the dashboard; the desktop app never calls them (only `verify`/`activate`). For v1 the admin actions run as the commented Supabase one-liners in `sqls/schema-hard-device.sql` §3, each paired with a `license_events` audit insert. Build these alongside the dashboard. Spec retained below.

- `app/api/admin/licenses/hard-deactivate/route.ts` — `{license_key, reason, actor?}` → `status='revoked'`, `revoked_reason`, `revoked_at=now()`. `license_events` insert: `event_type: 'license_hard_deactivated'`. Does **not** touch fingerprints/activations — device-slot handling stays a separate, already-built action (see runbook §6).
- `app/api/admin/licenses/reactivate/route.ts` — `{license_key, actor?, note?}` → `status='active'`, `revoked_reason=null`, `revoked_at=null`. `license_events` insert: `event_type: 'license_reactivated'`.

### 3.5 Admin dashboard (`app/dashboard/page.tsx`) — POSTPONED (2026-07-06)

> Convenience-only UI; the enforcement logic is already live without it. At the current tiny user count, admin revoke/reactivate runs via raw Supabase SQL (`sqls/schema-hard-device.sql` §3) or the table editor. Revisit when hand-run SQL becomes impractical. Spec retained below for when it's built.

- `LicenseOverview` type: add `revoked_reason: string | null`, `revoked_at: string | null`.
- `StatusBadge`: third rendering for `revoked`, visually distinct from the red "blocked" badge (dark/black + ban icon) — the two must never be confusable at a glance.
- New "Emergency Hard-Deactivate / Reactivate" action card in `DetailDrawer` near the Block/Unblock card, same pattern: required reason field, `confirm()` dialog (like the existing revoke-device button), shows `revoked_reason`/`revoked_at` when revoked. Confirmation copy must say: locks on next check-in; removes the silent Windows unlock key; does not delete clinical data; user may need to re-enter their licence key after reactivation.
- Optional: "Revoked" quick-stat tile next to "Blocked" (client-side filter, no new query).

---

## 4. Desktop backend (`private-test-claude`)

### 4.1 `backend/database.py`

Guarded migration `ALTER TABLE app_licenses ADD COLUMN revoked INTEGER DEFAULT 0`, same `PRAGMA table_info` check-before-alter pattern as the existing `blocked` column migration (~line 1129). Lives in the encrypted DB.

### 4.2 `backend/services/db_keys.py`

- **`scrub_dpapi(path=KEYS_PATH) -> bool`**: `load_keyfile()` → delete the `"dpapi"` entry → keep `"recovery"` fully intact → set a plaintext top-level `"revoked": true` sidecar marker → atomic `save_keyfile()` (existing, db_keys.py:151). The marker is **load-bearing for the official app flow, not a tamper-proof cryptographic boundary**: readable pre-unlock, it drives (a) UI copy on the locked screen, (b) locked-DB startup init of the in-memory flag (§4.4), and (c) the online-required recovery rule (§4.3). A marked machine may not self-recover offline *through the official app*. A thief who tampers with `db_keys.json` (e.g. deletes the marker) is in the same class as one running custom unwrap tooling — already outside what server-side revoke can stop (§1 honest limit). Returns `False` if no keyfile (plaintext-DB installs — nothing to scrub; the middleware still blackouts routes). **Idempotent**: a missing `"dpapi"` entry counts as already-scrubbed success. `unwrap_dek_dpapi()` already handles a missing entry gracefully (try/except → None) — no change needed there.
- **`rewrap_dpapi()` (db_keys.py:208)**: add `keyfile.pop("revoked", None)` before the save. This is the single chokepoint that clears the marker for **both** callers — `database.py:424` (`try_unlock_with_license`, licence-recovery unlock) and `services/backups.py:516` (restore path). Reaching a rewrap means a legitimate unlock just succeeded.

### 4.3 `backend/routers/license.py`

- **`_set_revoked(workspace_type, revoked: bool)`** — twin of `_set_blocked()` (:51-60), updates `app_licenses.revoked`. Set on verify-revoked; cleared **only** by a successful online `valid` verify — never by offline, PIN, or reset-PIN.
- **`_verify_license_impl()`** — new branch next to the existing `elif web_status == "expired":` (:695), never folded into it:

  ```python
  elif web_status == "revoked":
      _set_revoked(workspace_type, True)
      security.set_revoked(True)        # synchronous — shuts the LIVE session (§2 correction 2)
      security.set_locked(True)
      try:
          db_keys_service.scrub_dpapi() # best-effort; a keyfile IO error must not mask the revoke
      except Exception:
          pass
      return {"status": "revoked", "message": "This licence key cannot be used. Contact support."}
  ```

  On the healthy `web_status == "valid"` branch, alongside the existing `_set_blocked(workspace_type, False)` (:683): add `_set_revoked(workspace_type, False)` and `security.set_revoked(False)` — this is what completes a revive once the device re-verifies online after admin reactivation. (Demo keys return a canned verify response before any network call, license.py:634-644, so a revoke can never land on a demo machine — accepted; demo machines are the founder's own.)
- **`_offline_response()`** (:225): add `revoked` to the SELECT (:238-241) and check `cached["revoked"]` **before** `cached["blocked"]` (:248) → return `{"status": "revoked", "message": ...}`. Revoked is the stronger state; a revoked machine must not downgrade itself to a soft blocked banner offline.
- **`check_license()`** (:270): add `revoked` to the SELECT and response, so the frontend auto-login path reacts before the first verify completes (same reasoning as the existing `mode` field).
- **`activate_license()` — recovery-unlock gate** (the "thief found the key" fix): right before the existing locked-DB block (:322 `if get_encryption_status().get("mode") == "locked": try_unlock_with_license(...)`), add an online pre-check of the submitted key. The behaviour branches on whether **this machine is already locally marked revoked** (the `db_keys.json` sidecar marker via `load_keyfile()` — the DB is locked here so `app_licenses.revoked` is unreadable; also consult `app_licenses.revoked` in the non-locked activation path where it *is* readable):
  - **Not locally marked revoked** (the normal case — every legitimate cross-machine restore): best-effort check. When the server is reachable, refuse **only** on the literal response `status == "revoked"` → 403 `"This licence key cannot be used. Contact support."` — **without ever calling `try_unlock_with_license`**, so the DEK never loads into process memory for a killed key. `wrong_machine`/`not_found`/`expired` responses and **any network failure** fall through to today's offline-friendly local unlock, unchanged.
  - **Locally marked revoked**: recovery unlock becomes **online-required**. Server unreachable → refuse: 403 `"This workspace was deactivated and must be reactivated online."` Server says `revoked` → refuse (same as above). Server returns `valid`/`activated` → allow the recovery unlock to proceed; the subsequent `rewrap_dpapi` clears the sidecar marker (§4.2), and — **as of the 2026-07-09 fix, see `bugs-fixed/024-07072026.md` Addendum 2** — this same code path immediately clears `app_licenses.revoked` and the in-memory `security_service` flag itself (`if _precheck_status in ("valid", "activated"): _set_revoked(...); security_service.set_revoked(False)`), rather than deferring that to "the next healthy verify". The original design (deferring to the next verify) was a real bug: a live drill found the frontend can never reach a workspace view — and therefore never trigger that next verify — while every route is still 403'd by the still-`True` in-memory flag, creating a dead end that only a full app restart could escape. **Why this must not fall through offline**: otherwise a thief defeats the feature by disconnecting the internet after the revoke lands — offline fallback would unlock the DB and `rewrap_dpapi` would clear the marker (§2 correction 4). Normal offline restore is unaffected because a machine that never received the revoke has no marker.
  - Demo keys (`normalized_key.replace("-","") in _DEMO_KEYS`) skip the online check as today — safe, because demo keys are never added as recovery protectors (activation skips `add_or_refresh_recovery` for them, license.py:526), so a demo key cannot open an encrypted DB regardless.
  - Additive gate, not a restructure — the device-transfer/cooldown/pending logic later in the function must be untouched.
- **`activate_license()` — status elif-chain** (:409-437): add `elif web_status == "revoked": raise HTTPException(403, "This licence key cannot be used. Contact support.")`. Without it a revoked key on a normal (non-locked-DB) activation falls to the generic 503 (§2 correction 3).
- **`_log_verify_outcome()`** (:544-566):
  - Add a `revoked` branch (today a revoked status would log **nothing**): `outcome="revoked", error_code="license_revoked"`. Both are new values for the bounded frozensets in `services/activity_log.py` — add `"revoked"` to `OUTCOMES` (:50-53) and `"license_revoked"` to the licence group of `ERROR_CODES` (:70-71). This addition is required, not cosmetic: `_insert` coerces any outcome not in `OUTCOMES` to `"completed"` (:263), which would log a revoke as a success.
  - Add a module-level outcome-change dedup cache (dict keyed by `workspace_type`, storing last logged status): log only on change. Originally motivated by the 10-minute frontend poll (§5, since deleted), but **still required**: focus/wake/reconnect can each fire a verify many times a day, and the function logs unconditionally for every non-ok result (`offline` on an offline machine = one row per attempt, and the Support Diagnostic Log rotates at 30 days + a row cap, so spam flushes real crash evidence).

### 4.4 `backend/services/security.py` + `backend/main.py`

- `_IS_REVOKED` / `is_revoked()` / `set_revoked()` mirroring `_IS_LOCKED` / `is_locked()` / `set_locked()` (:42-61).
- `initialize_revoked_state()` called from `main.py`'s startup event alongside `initialize_lock_state()` (:192): read `app_licenses.revoked` when the DB is readable; when the DB is **locked** (the post-scrub restart — exactly the state Tier 2 creates), fall back to the keyfile sidecar marker (`db_keys.load_keyfile()` → `.get("revoked")`). Best-effort, never blocks startup.
- **`RevokedMiddleware`** in `main.py`, mirroring `WorkspaceLockMiddleware`'s structure (:125-132, including `_call_next_safe`). Gated on `security.is_revoked()`. Returns **403** with `{"detail": "...", "revoked": true}` — distinct from the lock's 423 so the frontend can tell them apart. Allow-list (deliberately much smaller than `_LOCK_ALLOW_PREFIXES` :82-101):
  - `/api/health`
  - `/api/licenses/` (the only path that can ever clear the flag)
  - `/api/system/encryption-status`
  - Explicitly NOT allowed: AI generators, transcribe, `/api/backup/auto`, `/api/security/` (PIN unlock must not bypass revoked; the frontend's revoked screen takes precedence over the lock screen, so a failing `pin-status` call is moot), purge (§2 supersessions), everything stored-data.
  - Register with `app.add_middleware(RevokedMiddleware)` between the existing Lock and Token adds (its allow-list is a strict subset of the lock's, so relative order doesn't change outcomes; token auth stays outermost).
- **PIN interaction — no `verify_pin()` change needed**: `/api/security/` isn't on the revoked allow-list, so PIN unlock 403s while revoked. After scrub+restart the DB is `locked` → `pin_is_set()` already returns `False` (`_db_readable()` check, security.py:64-79) → the licence-recovery screen naturally supersedes the PIN screen. Confirm both in testing.
- **`reset_pin()`** (`backend/routers/security.py`:110): extend `if result.get("status") == "blocked"` to `in ("blocked", "revoked")`. The docstring (:79-83) already promises revoked refusal — make the code match. Defensive and cheap, correct regardless of whether the scrub already ran.

---

## 5. Desktop frontend

- **`src/utils/api.ts`**: extend `LicenseVerifyResult.status` union (:585) with `'revoked'`; add `revoked?: boolean` to `LicenseStatus` (`checkLicense` return, :1542).
- **`src/App.tsx`**:
  - Verify handler (:472-496): new `result.status === 'revoked'` branch with copy distinct from blocked/expired. Must read as final and must **not** claim "existing records are accessible" (after scrub+restart they aren't). Suggested: *"This workspace has been deactivated. For security reasons, this licence can no longer open this workspace. Please contact your organisation administrator or PRIVATE support."*
  - ~~**Periodic re-verify poll** (~10 min `setInterval` alongside the view-entry verify effect at :471)~~ — **BUILT, then DELETED 2026-07-10 (024 Addendum 3). Do not re-add any time-based licence poll.** What makes a live open session hear a revoke is now the event set: focus, tab visibility, OS wake (`powerMonitor` → `system-resumed`), network reconnect (`window 'online'`), plus workspace entry. All of them keep working while PIN-locked with no extra work — `/api/licenses/` is already on the workspace-lock allow-list (main.py:91); **don't remove that entry.**
  - Auto-login effect (:317-355): check `res.revoked` from `checkLicense()` before navigating in — a revoked machine lands on the hard-lock messaging immediately, no workspace flash.
- **`src/pages/SelectionPage.tsx`**: parallel, visually distinct revoked variant of the `licenseBlockedMessage` banner (:280-283). The activation form's generic error-toast already surfaces the backend 403 detail for a revoked-key activation — needs only good copy, no special-casing.

---

## 6. Runbook: genuinely lost/stolen laptop, counsellor needs a new one

Process, not new code — chains the new action with already-built tools.

**Key principle: never reactivate the licence globally while the stolen device still holds an active device row.** If the old laptop hasn't yet checked in when the licence flips back to `active`, it would see `active` — not `revoked` — the first time it comes online.

1. **Immediately**: admin clicks **Hard-deactivate** (reason: "stolen"). The old laptop goes dark the next time it performs a successful online licence verification — its next launch, the next time its window regains focus or the machine wakes, the moment its network reconnects, or any activation/recovery/transfer attempt. It then becomes unopenable after its next restart, even with the correct key. **There is no timer and no bound**: an app sitting idle and untouched in the foreground is not checking, and a laptop that never reconnects is never reached. Set the counsellor's expectation accordingly.
2. **Revoke the old device's activation row** as soon as the old `machine_id` is known (existing **Revoke device** action; the dashboard shows activation rows). Harmless under the single-seat model today; load-bearing the moment step 3 switches the licence to the count model — multi-seat verify requires `activations.status = 'active'` (verify/route.ts:99-108), so a revoked row bars the old machine even after reactivation.
3. Counsellor has the new laptop: admin **Set device limit → 2** (switches the licence to the legacy multi-seat count model, which ignores the single-seat fingerprint columns — no fingerprint-clearing needed).
4. Admin clicks **Reactivate** — only now, with the old device row already revoked (or when genuinely ready to recover the legitimate user).
5. Counsellor installs PRIVATE on the new laptop, restores their own USB backup ZIP via Backups → restore (already carries `db_keys.json`), activates with the same key — runs through the already-built cross-machine licence-recovery screen. No new desktop code.
   **⚠ Order correction (2026-07-10, see §6.1 for why): activation must come BEFORE restore** — the
   backup ZIP's password is derived from the locally-activated licence key (`backups.py`
   `_get_license_keys()` reads `app_licenses`), so on a fresh install the restore cannot open the ZIP
   until the key has been activated on that machine.
6. **Confirm the old device row is still revoked** after the counsellor's activation (one dashboard glance — cheap assurance the stolen machine stays barred).
7. Admin **Set device limit → 1** (server already enforces the old device must be revoked first).

Write this up as a short internal runbook doc once built.

### 6.1 SQL-era concrete runbook (2026-07-10) — the live support-call script

The steps above are phrased for the postponed admin dashboard actions. While hard-deactivate/reactivate
run as raw Supabase SQL (§9), this is the **exact live script** for the real case: laptop stolen,
licence already `status = 'revoked'`, counsellor is on a call with a **new laptop**, her **same 16-char
key** (email/records), and her **USB backup ZIP**. Whole call ≈ 10 minutes.

Core mental model (this is what confused the first walkthrough): **revoke is a status-column flip, not
key deletion — un-revoke is flipping it back.** The key *string* is the crypto secret for everything
local (ZIP password via PBKDF2, DEK recovery entry in `db_keys.json`); the server column only controls
whether the app flow accepts it.

**Support side (Supabase SQL editor):**

```sql
-- 0. Confirm state
SELECT license_key, status, revoked_at FROM licenses WHERE license_key = 'CLIN-XXXX-XXXX-XXXX';
SELECT machine_id, activated_at FROM activations WHERE license_key = 'CLIN-XXXX-XXXX-XXXX';

-- 1. Free the stolen machine's device slot (single row = the stolen laptop).
--    Dashboard "Revoke device" is the safer equivalent when available (keeps the row as an
--    audit trail + bars it under the count model). Raw-SQL path per how-it-works.md:
DELETE FROM activations WHERE license_key = 'CLIN-XXXX-XXXX-XXXX';
--    ⚠ If the live schema carries the device-transfer single-seat fingerprint columns on
--    `licenses` (web repo schema-device-transfer.sql — not mirrored in this repo), clear
--    those too (the documented v1 support reset: clear active_fingerprint). Verify column
--    names in the web repo before relying on this line.

-- 2. Un-revoke the SAME key (identical to schema-hard-device.sql §3 REACTIVATE):
BEGIN;
  UPDATE licenses
    SET status = 'active', revoked_reason = NULL, revoked_at = NULL
    WHERE license_key = 'CLIN-XXXX-XXXX-XXXX';
  INSERT INTO license_events (license_key, event_type, actor, note)
    VALUES ('CLIN-XXXX-XXXX-XXXX', 'license_reactivated',
            'support@privateworkspace.co', 'Stolen-device recovery — moving to new laptop');
COMMIT;
```

Run step 2 only when the counsellor is ready to activate **immediately** — the window between
un-revoke and her claiming the slot is the only moment the thief (with the key, online) could claim it.
On a live call that window is seconds.

**Counsellor side (new laptop, right after step 2):**

3. Launch app → enter the same 16-char key → **activated** (new `activations` row = her new machine).
   From this moment the stolen laptop is barred for good: it is locally marked revoked
   (online-required), and every online check it makes now returns wrong-machine/device-limit — never
   the explicit `valid` the marked-machine gate demands.
4. Fresh install shows profile setup — create a **throwaway profile** (restore overwrites it).
5. Backups tab → **Open Folder** → copy the ZIP from USB into `private_storage/backups/` → Restore →
   confirm → full "Close PRIVATE" restart. (Activation had to come first: the ZIP password derives
   from the activated key.)
6. Relaunch → DB is `locked` on this machine (restored `db_keys.json`'s DPAPI wrap belongs to the old
   laptop) → recovery screen → **enter the same key once more** → online precheck returns `valid`
   (she owns the slot) → DEK unwraps from the key's recovery entry → DPAPI re-wrapped for this
   machine → workspace opens **first try** (the bugs-fixed/024 Addendum 2 fix; before it this step
   dead-ended on the profile-setup screen). The restored ZIP predates the theft, so it carries no
   revoked marker.
7. Everything is back: clients, sessions, real profile, and her old PIN (`app_security` travels
   inside the DB).

**Absolute rule: recover with the SAME key — never "solve" a theft by issuing a replacement key** while
backups exist. Old ZIPs and the recovery entries inside them are locked under the old key; a
replacement key opens none of them (§7 / Appendix A honest limit; key-rotation is the future fix). A
replacement key is only for the §7 key-compromised case, and §7's step 3 still needs the OLD key one
last time to open the old backup.

## 7. Runbook: key-compromised (thief may have the licence key string)

The old licence key is now a leaked password. Hard-deactivate is **not** full cryptographic protection here.

1. Hard-deactivate immediately; mark internally as key-compromised.
2. Do not reuse the old key. Issue a replacement key for go-forward use.
3. Recover the legitimate user on a safe device from their off-device backup.
4. **Honest gap, stated to the counsellor**: existing USB backup ZIPs are PBKDF2-encrypted under the **old** key (`services/backups.py`, Step-2 format) — a replacement key does not re-encrypt them. Anyone holding both an old ZIP and the old key can open that ZIP. Advise: create a fresh backup under the new key, then destroy/retire old ZIPs where feasible. This is half-solved until the key-rotation feature exists:
   - *Future feature*: old key opens DB → new key verified online → recovery protector rewrapped under new key → old protector removed; same ceremony for a fresh backup set.

## 8. Verification (merged checklist)

1. `npx tsc --noEmit` after frontend changes.
2. **Soft-block regression** — the highest-value invariant: `active → blocked` still behaves exactly as today (new work gated, records readable, exports work, no scrub, no hard lock, **recovery unlock NOT refused**).
3. **Blocked key typed into recovery screen while online** → unlock allowed; soft-block policy applies after entry. (The direct test of §2 correction 1.)
4. **Live-session drill**: workspace open → admin hard-deactivates → **nothing happens while the app sits idle and untouched** (correct: there is no poll). Then trigger any verification event — alt-tab away and back, sleep/wake the laptop, toggle Wi-Fi off and on, or restart — and the middleware 403s stored-data routes; PIN cannot bypass; scrub ran. The overlay lands within ~1 s of the backend learning, via the local `/api/system/events` SSE push. *(2026-07-10 evening: the 25 s poll this item once referenced was deleted — see `bugs-fixed/024-07072026.md` Addendum 3.)*
5. **Restart drill**: hard-deactivate → restart → encryption-status = `locked`, no stored-data route serves anything, PIN screen does NOT appear (superseded by recovery screen), re-entering the still-revoked key online is refused with "cannot be used" (DEK never loads).
6. **Offline recovery fallback — unmarked machine**: DB locked, no local revoked marker, server unreachable → existing offline-friendly recovery still works (legitimate restores must not regress; the honest limit applies).
7. **Offline recovery refusal — marked machine (thief-disconnect drill)**: hard-deactivate → scrub + marker written → disconnect network → enter the original key → refused with "This workspace was deactivated and must be reactivated online."; DEK never loads, marker stays in place. Reconnect while still revoked → still refused. Only after admin reactivation + an online check does recovery succeed.
8. **Reactivate false-alarm (same device)**: after admin reactivation, the marked machine's recovery requires the online check to return `valid` — then recovery-key entry unlocks; `rewrap_dpapi` recreates the DPAPI wrap **and clears the keyfile `revoked` marker**; the next healthy verify clears `app_licenses.revoked` + in-memory flag; workspace opens.
9. **Normal activation + normal (non-revoked) cross-machine restore still work** after the recovery-gate addition — highest regression risk: same function as device-transfer/cooldown/pending logic. Run the transfer flows (set-max-devices, revoke-device, lower to 1, cooldown, pending→finalize).
10. **Revoked key on fresh activation** (normal machine, DB not locked) → clear 403 "cannot be used", not the generic 503 (§2 correction 3).
11. **Auto-login revoked**: `private_last_workspace` set + local revoked → revoked screen immediately, no workspace flash.
12. **Reset-PIN refused** while revoked.
13. **Diagnostic-log dedup**: a day of repeated offline verifies (focus/wake/reconnect) → only outcome *changes* logged, no row-per-attempt spam; and a revoked verify **does** produce a (single) `outcome="revoked"` row — not one coerced to `"completed"` (frozenset addition verified).
14. **App close while revoked**: Electron `before-quit` backup gets a 403 from `/api/backup/auto` → close proceeds promptly (no 10s hang), no fresh backup ZIP is written.
15. Full runbook drill (§6 steps 1–7) on a throwaway test licence.

## 9. Deliberately not building (v1)

- **Admin dashboard UI + `hard-deactivate`/`reactivate` admin API routes** — POSTPONED (2026-07-06), not cancelled. At the current tiny user count, admin revoke/reactivate runs as direct Supabase SQL one-liners (`sqls/schema-hard-device.sql` §3, each with a `license_events` audit insert). The desktop app consumes only `verify`/`activate`, so this postponement does not block the feature; build when hand-run SQL becomes impractical. **The web `verify`/`activate`/`finalize`/`cancel-transfer` route changes are NOT postponed — they are already built (Appendix B).**
- Remote wipe / data destruction (revoke is reversible by design; also deleting `recovery[]` would be an irreversible remote destroy on a no-cloud-copy product — a false-positive catastrophe).
- Deleting `recovery[]` entries on revoke (would break false-alarm recovery).
- Staleness auto-lock ("N days offline") — separate product-policy decision; if ever built: route-lock only, **never scrubs**, 7–14 days, accept the clock-rollback weakness (consistent with the existing wrong-clocks policy, smoke-test decision F4 2026-06-16).
- Treating `blocked` as hard in any way, including refusing recovery unlock for blocked.
- Purge while revoked (see §2 supersessions — interim path is revive → purge).
- Key/recovery rotation (future feature; see §7).
- Extra audit columns beyond `revoked_reason`/`revoked_at` (`license_events` is the single audit trail).

## 10. Implementation order

1. **Web foundation**: schema migration ✅ written (`sqls/schema-hard-device.sql`; not yet run in Supabase) → verify route ✅ → activate route ✅ → **`finalize`/`cancel-transfer` routes ✅ (§3.3a addition)**. `hard-deactivate`/`reactivate` admin routes **postponed** with the dashboard (step 4). Remaining here: run the migration in Supabase + merge/deploy the route branch. (Desktop changes are meaningless without the verify/activate changes.)
2. **Desktop backend**: DB column → `scrub_dpapi` + rewrap marker-clear → `_set_revoked` → verify branch (incl. synchronous `set_revoked`) → healthy-branch clear → offline priority → `check_license` → recovery gate (incl. the marked-machine online-required rule) → activate elif branch → `_log_verify_outcome` branch + dedup (+ `activity_log.py` `OUTCOMES`/`ERROR_CODES` frozenset additions) → in-memory state + startup init → `RevokedMiddleware` → reset-pin.
3. **Desktop frontend**: api.ts types → App.tsx revoked branch + event-driven re-verify + auto-login → SelectionPage variant.
4. **Admin dashboard**: *postponed (2026-07-06)* — raw Supabase SQL one-liners (`sqls/schema-hard-device.sql` §3) are the v1 admin path. Build type/badge/action-card/tile (+ the §3.4 admin routes) when hand-run SQL becomes impractical.
5. **Docs**: CLAUDE.md (License Expiry section), `.claude/commands/LicenseExpiry.md`, `.claude/commands/WorkspaceLock.md` (three-state model, PIN-vs-scrub interaction — "the PIN is not the DB key" gains a sibling: "revoke IS allowed to reach the DB-key path via the Tier 2 scrub"), customer-facing "licence key is a password / you own your off-device backup" wording, both runbooks. Mark this doc built when done.

---

## Appendix A — Honest threat model (retained from the 2026-07-05 revision, updated for the online-required recovery rule)

| Attacker scenario | Today (`blocked` only) | Route blackout alone | Full build (blackout + scrub + online-required recovery) |
|---|---|---|---|
| Casual thief, can't get past Windows login | Already stopped (Windows login + DB encryption at rest) | Same | Same |
| Thief past Windows login, uses the app | Full read/export of everything | Locked at its next online verification event (launch, focus/wake, reconnect) — using the app inevitably produces one; locked at next launch regardless | Same, **plus** after any restart the DB is unopenable without the licence key |
| **Technical** thief past Windows login, ignores the app (own tools + `db_keys.json`) | Full access — DPAPI unwrap needs nothing from us | **Unchanged — full access.** Route-blocking alone fails this attacker | Stopped from the moment the scrub lands (device must come online once) |
| Thief who ALSO has the licence key string, uses the official app | Full access | Unchanged | **Refused** — online check rejects the key; once marked, even going offline doesn't help (online-required recovery) |
| Thief who ALSO has the key string, uses own tooling (or tampers with `db_keys.json`) | Full access | Unchanged | **Unchanged — the key is a password; no server action rewinds local crypto.** Treat as a breach (§7) |
| Thief who imaged the disk before the revoke arrived | Full access on the copy | Unchanged on the copy | Unchanged on the copy — a scrub can't reach a copy taken earlier |
| Laptop kept permanently offline from the moment of theft | Exposure unbounded | Unbounded until a (deferred) staleness lock | Same — the revoke needs one check-in to land (§9: staleness lock deferred) |

**Plain reading:** the full build converts "thief with the Windows password" from *game over* into *needs the licence key too*, and converts "thief with the Windows password AND the key, using our app" into *refused*. Nothing converts "thief with the key and their own tools" into anything better — that combination is a leaked-password breach: revive is refused, the key is permanently dead, and the customer conversation is about what was on the device (§7).

## Appendix B — Build Tracking Checklist

Use this as the working tracker. The sections above remain the signed-off source of truth.

---

# Web side — `private-test-web`

## Web foundation

* [x] Add `supabase/schema-hard-revoke.sql`. — written; **not yet run** against live Supabase (Jonathan runs it).
* [x] Confirm the live `licenses.status` CHECK constraint name before dropping it. — done via dynamic `pg_constraint`/`conkey` lookup inside the migration itself (not a separate manual query first).
* [x] Widen `licenses.status` to allow `active`, `blocked`, and `revoked`. — in the migration, pending Supabase run.
* [x] Add `licenses.revoked_reason`. — in the migration, pending Supabase run.
* [x] Add `licenses.revoked_at`. — in the migration, pending Supabase run.
* [x] Update `app/api/licenses/verify/route.ts` to return `status: "revoked"` before mode/device resolution.
* [x] Update `app/api/licenses/activate/route.ts` to return `status: "revoked"` before single-seat/multi-seat handling.
* [x] **(addition, §3.3a)** Update `app/api/licenses/finalize/route.ts` to refuse `revoked` before completing a transfer.
* [x] **(addition, §3.3a)** Update `app/api/licenses/cancel-transfer/route.ts` to refuse `revoked` before cancelling a transfer.
* [ ] Add `app/api/admin/licenses/hard-deactivate/route.ts`. — **POSTPONED**, see §3.4.
* [ ] Log `license_hard_deactivated` to `license_events`. — **POSTPONED** (folds into above).
* [ ] Add `app/api/admin/licenses/reactivate/route.ts`. — **POSTPONED**, see §3.4.
* [ ] Log `license_reactivated` to `license_events`. — **POSTPONED** (folds into above).

## Admin dashboard — POSTPONED (2026-07-06, Jonathan's call)

Convenience-only UI layer; the enforcement logic above is already live without it. Action revokes/reactivations via raw Supabase SQL or the table editor in the meantime (`schema-hard-revoke.sql` §3). Revisit only if asked.

* [ ] Add `revoked_reason` and `revoked_at` to `LicenseOverview`.
* [ ] Add a visually distinct `revoked` status badge.
* [ ] Add Emergency Hard-Deactivate action card.
* [ ] Require reason before hard-deactivate.
* [ ] Add clear confirmation copy for hard-deactivate.
* [ ] Add Reactivate action for revoked licences.
* [ ] Show `revoked_reason` and `revoked_at` when revoked.
* [ ] Optional: add Revoked quick-stat tile.

---

# App side — `private-test-claude`

## Desktop backend

* [x] Add guarded `app_licenses.revoked INTEGER DEFAULT 0` migration.
* [x] Add `db_keys.scrub_dpapi()` that removes only `dpapi`, keeps `recovery`, and writes `"revoked": true`.
* [x] Make `db_keys.rewrap_dpapi()` clear the `"revoked"` marker.
* [x] Add `_set_revoked(workspace_type, revoked)` in `backend/routers/license.py`.
* [x] In `_verify_license_impl()`, handle `web_status == "revoked"` separately from blocked/expired.
* [x] In `_verify_license_impl()`, call `security.set_revoked(True)` synchronously when revoked lands.
* [x] In `_verify_license_impl()`, scrub DPAPI best-effort when revoked lands.
* [x] On healthy online `valid`, clear `_set_revoked(..., False)` and `security.set_revoked(False)`.
* [x] Update `_offline_response()` so local revoked wins before local blocked.
* [x] Update `check_license()` to select and return `revoked`.
* [x] Add locked-DB recovery gate before `try_unlock_with_license()`.
* [x] Recovery-unlock path clears `_set_revoked`/`security_service.set_revoked` immediately on a confirmed `valid`/`activated` precheck, instead of deferring to the next verify — bug found + fixed 2026-07-09 (see `bugs-fixed/024-07072026.md` Addendum 2); the deferred version was a real dead-end lockout, not just a design simplification.
* [x] Allow offline fallback only when the local keyfile is not already marked revoked.
* [x] Refuse marked-revoked offline recovery with "This workspace was deactivated and must be reactivated online."
* [x] Add normal activation `web_status == "revoked"` branch returning 403, not generic 503.
* [x] Add `_log_verify_outcome()` revoked branch.
* [x] Add verify-outcome dedup cache keyed by workspace type.
* [x] Add `"revoked"` to `activity_log.OUTCOMES`.
* [x] Add `"license_revoked"` to `activity_log.ERROR_CODES`.
* [x] Add `_IS_REVOKED`, `is_revoked()`, and `set_revoked()` in `backend/services/security.py`.
* [x] Add startup `initialize_revoked_state()` using DB when readable and keyfile marker when locked.
* [x] Add `RevokedMiddleware` in `backend/main.py`.
* [x] Keep revoked middleware allow-list minimal: `/api/health`, `/api/licenses/`, `/api/system/encryption-status`.
* [x] Confirm `/api/security/` is not allow-listed while revoked.
* [x] Update `reset_pin()` to refuse both `blocked` and `revoked`.

## Desktop frontend

* [x] Extend `LicenseVerifyResult.status` with `"revoked"` in `src/utils/api.ts`.
* [x] Add `revoked?: boolean` to the local licence status/check type.
* [x] Add `result.status === "revoked"` handling in `src/App.tsx`.
* [x] Use revoked copy that does not promise existing records remain accessible.
* [x] Add 10-minute periodic re-verify while inside a workspace.
* [x] Update auto-login so `res.revoked` stops navigation before workspace flash.
* [x] Add a visually distinct revoked banner/message in `src/pages/SelectionPage.tsx`.

---

# Docs and runbooks — shared / both sides

* [ ] Update `CLAUDE.md`.
* [ ] Update `.claude/commands/LicenseExpiry.md`.
* [ ] Update `.claude/commands/WorkspaceLock.md`.
* [ ] Write short lost/stolen laptop runbook.
* [ ] Write key-compromised runbook.
* [ ] Add customer/support wording: licence key is a password.
* [ ] Add customer/support wording: PRIVATE does not keep a cloud copy; off-device backups are the user's responsibility.
* [ ] Mark this plan as built only after code and verification are complete.

---

# Verification

## Web side verification

* [x] Run web TypeScript checks after web changes. — `npx tsc --noEmit` clean after each of the four route changes above.
* [ ] Run `schema-hard-revoke.sql` in Supabase and confirm with the verification queries at its bottom.
* [ ] End-to-end: flip a test licence's `status` to `'revoked'` via SQL/table editor, confirm `verify`/`activate`/`finalize`/`cancel-transfer` all refuse it; flip back to `'active'`, confirm normal recovery.


## App side verification

* [x] Run desktop `npx tsc --noEmit` after frontend changes.
* [ ] Soft-block regression: `blocked` still allows existing records and exports.
* [ ] Blocked key typed into recovery screen still unlocks existing local data.
* [ ] Live-session hard-deactivate shuts down at the next verification event (focus / wake / reconnect / restart) — and, correctly, NOT while the app sits idle and untouched.
* [ ] Restart after hard-deactivate shows locked/recovery state, not normal PIN.
* [ ] Revoked key typed online is refused before DEK loads.
* [ ] Offline recovery still works on an unmarked machine.
* [ ] Offline recovery is refused on a locally marked revoked machine.
* [ ] Admin reactivation lets the marked machine recover online and clears the marker.
* [ ] Normal fresh activation still works.
* [ ] Normal cross-machine restore still works.
* [ ] Device transfer / cooldown / pending-finalize flows still work.
* [ ] Revoked key on fresh activation returns clear 403, not generic 503.
* [x] Auto-login revoked has no workspace flash.
* [ ] Reset-PIN refused while revoked.
* [ ] Diagnostic-log dedup prevents repeated verify spam (focus/wake/reconnect while offline).
* [ ] Revoked verify logs `outcome="revoked"` instead of coercing to `completed`.
* [ ] App close while revoked does not hang on `/api/backup/auto`.

## Full flow verification

* [ ] Full lost/stolen runbook drill passes on a throwaway test licence.

---

# Future option, not v1

* [ ] Keep irreversible remote cryptographic erase separate from `revoked`.
* [ ] If institutions require it later, design it as a device-specific command, not a licence-wide side effect.
* [ ] Name it accurately as "remote cryptographic erase on next check-in", not guaranteed deletion of an offline stolen disk.



==========================================================================================================================================

그래서 안전성하고 뭐랄까 그게 있음? admin인 나로서 도와줘야할때 그런 장치가 다됨?

● 짧게 말하면: 안전장치(설계)는 거의 다 돼 있고 그 자체로 안전함(되돌릴 수 있고 데이터 안 지움). 근데 "관리자인 네가 지금 당장 실제 고객한테 발동" 은 아직 못 해. 남은
  4개가 있는데, 그게 전부 데스크톱 코드 밖(웹·배포·드릴)이야. 데스크톱 쪽은 다 됐어.

  1. 안전장치는 되어 있고 검증됨 (데스크톱)

  이건 다 만들어졌고 확인까지 됨:
  - revoked ≠ blocked 완전 분리 — 요금 밀린 고객을 실수로 하드락하는 사고 안 남
  - 되돌릴 수 있음 — reactivate = 진짜 주인이 키 한 번 재입력하면 끝, 작업 손실 없음
  - recovery[] 안 지움 → 진짜 주인은 라이선스 키로 데이터 복구 가능 (데이터 파괴 아님)
  - PIN으로 못 뚫음, reset-PIN(Forgot-PIN)도 revoked면 거부
  - 마킹된 기기는 오프라인 복구 거부 — 도둑이 인터넷 끊고 푸는 수법 방어 (이게 핵심 방어)
  - license_events 감사 로그 + 앱 종료 시 안 멈춤

  → 백엔드 67/67 통과 + 실제 앱 구동(revoked=1 직접 넣어서)까지 확인됨. 단, 이건 데스크톱 단독 검증이고, 웹까지 도는 전체 루프는 아직 검증 안 됨.

  2. 실제로 발동하려면 아직 남은 4개 (전부 데스크톱 밖)

  1. Supabase에 마이그레이션 실행 — 안 하면 status='revoked' 자체가 CHECK 제약 때문에 안 써짐(에러). 제일 먼저.
  2. 웹 라우트 브랜치 merge + 배포 — 배포 안 되면 DB에서 revoked 해도 verify가 노트북한테 "revoked"를 안 돌려줌 → 아무 일도 안 일어남
  3. 고객 앱이 v1.0.4+ — 구버전은 "revoked"를 몰라서 그냥 ok로 흘려보냄(fail-open). 구버전 사용자한테 revoke하면 조용히 아무것도 안 됨
  4. 실전 end-to-end 드릴 (SQL 파일 맨 밑 "내일 할거") — 이거 통과해야 "진짜 된다"가 증명됨. 아직 안 돌림

  이 4개 끝나면, 관리자 도구는 대시보드 없이도 완성이야 — 지금은 raw Supabase SQL 한 줄들(§3: hard-deactivate / reactivate)이 관리자 인터페이스고, 기존 revoke-device /
  set-max-devices랑 합치면 분실/도난 전체 절차(§6 런북)가 다 커버됨. 유저 적을 때 이걸로 충분해서 대시보드는 미룬 거고.

  3. 아무리 해도 못 막는 한계 (정직하게)

  - 도둑이 노트북 + 라이선스 키 문자열 둘 다 갖고 자기 툴 쓰면 → 못 막음 (키가 곧 비번). §7 유출 대응으로 처리
  - 노트북이 영영 인터넷 안 붙으면 revoke 못 들음
  - revoke 도착 전에 디스크 통째로 복사했으면 그 복사본은 못 건드림

  ---
  결론: 안전성·되돌리기·데이터 보존은 다 설계·구현됐고 데스크톱은 완성. 근데 "오늘 당장 관리자로서 실제 발동"은 아직 — ①마이그레이션 실행 ②웹 배포 ③고객 v1.0.4+ ④드릴 통과
  이 순서로 끝내야 실전 준비 완료야.

  내가 여기서 바로 도와줄 수 있는 것:
  - 데스크톱 코드가 실제로 revoked를 제대로 처리하는지 직접 확인 (플랜 말고 코드로 — 미들웨어/verify 분기/복구 게이트가 진짜 있는지)
  - 현재 데스크톱 버전 확인 (package.json) — 배포할 빌드가 v1.0.4+ 인지, 자동 업데이트로 고객이 그 버전 받는지
