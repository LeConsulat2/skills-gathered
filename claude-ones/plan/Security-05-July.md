Admin-Side Flexibility & Emergency Hard-Deactivate — Design Notes + Build Plan 2026-Jul-05

Audience: both this repo (desktop app) and the web project (Next.js + Supabase at privateworkspace.co).Status: discussion/design only — nothing in this doc is built yet. Captures a conversation working through what admin control over a lost/stolen laptop actually looks like today, where it falls short, and what a genuine "Emergency Hard Deactivate" feature needs on both sides.

Validated 2026-07-05: every code citation in PART A was re-checked against the working tree and is accurate (database.py:67, db_keys.py:106-120, license.py:51/225/529/683/695-706, security.py:5-10/59/83-86/125, App.tsx:233/453-502/472-480, Fromwebsite.sql §1/§5, main.py:88-101, routers/security.py:77-113). The validation also found that the original PART B design (route-blocking flag only) does not deliver the stated goal against a thief who is past the Windows login — the missing move is the DPAPI key-scrub (see PART 0 and B2 Tier 2). PART 0, B6, and several checklist rows were added as a result.

PART 0 — Plain-English summary (read this first)

The picture in plain words

The app protects data with three separate locks, and it helps to keep them apart in your head:

The Windows login — the front door of the house.

The database encryption — a safe inside the house. The contents are scrambled; you need a key (the DEK, a random 256-bit value) to read anything.

The licence system — a permission slip the app checks with your server whenever it can reach the internet.

Why a stolen laptop is exposed today: for everyday convenience, the app keeps a copy of the safe key on the laptop itself, wrapped so that only "this Windows user on this machine" can unwrap it. That wrapping is DPAPI — a built-in Windows service that encrypts small secrets for exactly one user on one machine. It's what lets the app open silently every morning without asking for anything. But it also means everything needed to open the safe is sitting on the disk, and anyone who gets past the Windows login can use it.

Why today's kill switch doesn't cover this: flipping status='blocked' only tells the app "refuse to start new work." It was built for the missed-payment case, so it deliberately never blocks reading or exporting existing records (a counsellor must never be locked out of their own clinical data over billing). And it doesn't touch the safe key at all. So a thief already past Windows can still read and export everything — and a technical thief doesn't even need the app: the unwrap ingredient (db_keys.json's dpapi entry) plus a logged-in Windows session is enough to open the database with their own code. A flag that only tells the app "refuse to serve pages" cannot stop someone who ignores the app.

The fix, in one sentence: when you press the emergency button on your website, the app on that laptop (the next time it's online) locks every screen AND deletes its own silent-unlock ingredient from the disk — from then on the safe only opens by typing the licence key.

Why that works, technically: db_keys.json holds two independent wrappings of the same DEK — the DPAPI one (silent, this-machine-only) and a "recovery" one locked with the exact licence-key string (PBKDF2, 600k iterations, then AES-256-GCM). Deleting the DPAPI entry is a one-file crypto-erase: the silent path is gone, and only the licence key opens the DB. The real counsellor knows their key, so a false alarm costs them one key entry (the app already has this exact "enter your key to unlock" flow — it's the cross-machine-restore path, encryption-status: locked). A thief doesn't know the key — and buying a fresh key from your own website won't help, because the wrap is bound to the exact original key string, not "any valid licence": a different string fails GCM authentication outright; it doesn't half-open.

The three honest limits (no design removes these)

A laptop that never goes online again never hears the revoke. Same limit every corporate remote-wipe system has. The only bound on it is the staleness auto-lock (B5): the app locks itself after N days without a successful server check-in.

A thief who also has the licence key string wins regardless. The key unwraps the recovery entry and is the password for every backup ZIP. Revoking the key on the server changes nothing about maths already done on the laptop. The licence key IS a password — customers must treat it like one. This is a communication/runbook point, not a code fix.

A thief who copies the whole disk before the revoke arrives keeps the pre-deletion ingredients. A remote action can't reach into a copy taken earlier. (This is also why the scrub in B2 Tier 2 matters at all: it only protects the window after it lands.)

What changed in this doc during validation

Added this PART 0 and the threat-model table (B6).

Split "hard" into three tiers in B2: route lock (what the doc already had), + DPAPI key-scrub (new — the piece that actually delivers the stolen-laptop goal), + optional remote wipe.

B4 rewritten: API-layer blocking is the right tool only for the live session; the key-scrub is what holds after a restart.

B5: added the clock-rollback caveat and "staleness never scrubs" rule.

Checklists C/D/E/F extended: reset-pin must also refuse revoked (it already refuses blocked — routers/security.py:110-113); the revoke middleware needs its own allow-list; auto-login must respect the flag; verify-poll log dedupe; Supabase CHECK-constraint replacement SQL; purge-while-revoked decision.

PART A — Background established during this conversation

A1. Encryption layers (why two different ciphers)

Not a deliberate "belt and suspenders" security strategy — it's incidental, driven by each library's own default:

Layer

Cipher

Why

local_private.db itself

ChaCha20-Poly1305

apsw-sqlite3mc (SQLite3 Multiple Ciphers) — this is just its default cipher (backend/database.py:67), nobody chose it over AES deliberately.

Backup ZIPs, client documents

AES-256-GCM

pyzipper — the library that produces WinZip-compatible AES-256 archives; also what any IT/procurement reviewer expects when opening a backup archive with 7-Zip/WinZip.

Both are strong; there's no actual weakness from the mix. db_keys.json's licence-recovery wrap also uses AES-256-GCM (backend/services/db_keys.py:106-120), for the same "it's what the Python crypto library offers" reason.

A2. How the DB key (DEK) is actually held — backend/services/db_keys.py

The 256-bit DEK is never stored raw. db_keys.json beside the DB holds two protectors for it:

dpapi — Windows DPAPI wrap, this machine + this Windows user only. Silent auto-unlock at every launch. This is why a stolen laptop that's still logged into the same Windows session (or whose Windows password gets cracked) will decrypt the DB with zero further checks — DPAPI unlock has nothing to do with the licence key or network state.

recovery[] — one entry per activated licence key: KEK = PBKDF2-HMAC-SHA256(licence key, salt, 600k iters), DEK wrapped under it with AES-256-GCM. This is what makes cross-machine restore / "new laptop" recovery possible — see A4.

Critically: the DEK is wrapped per exact licence-key string (add_or_refresh_recovery, license.py:529), not "any valid licence." A brand-new key generated on the website produces a different KEK — GCM auth fails, try_recovery_unwrap returns None. So a thief who buys/generates a fresh key from your site cannot use it to unlock a stolen device's data.

A3. The PIN is not a crypto gate

backend/services/security.py — the 6-digit PIN gates the UI/API routes (WorkspaceLockMiddleware, 423 while locked), it is explicitly not the DB encryption key (security.py:5-10). DPAPI still silently unlocks the DEK regardless of PIN-lock state; the DEK stays loaded in memory so background jobs keep running. IS_LOCKED resets to True at every fresh backend boot iff a PIN exists (initialize_lock_state, security.py:83-86) — so a cold restart requires the PIN again, but an already-running/unlocked session (laptop just woken from sleep, not rebooted) has no PIN gate to bypass. A 15-minute idle auto-lock exists client-side (src/App.tsx:233) as a partial mitigation.

A4. Org data retention when a laptop is genuinely lost (not recovered)

Two independent things have to both be true for the org to get the counsellor's data onto a new laptop:

An encrypted backup ZIP must have been copied off that laptop before it was lost (USB/network drive, via BackupPage.tsx → "Open Folder"). There is no cloud copy anywhere by design — this app never escrows client data centrally. If no off-device copy exists, the data is permanently gone; nothing server-side can reconstruct it. This needs to be communicated to org customers as their responsibility, not something support can fix after the fact.

The device slot must be freed so the new laptop can activate. Today's live schema (sqls/Fromwebsite.sql) is the simple model: one row per (license_key, machine_id) in activations, capped by licenses.max_devices. Freeing a dead machine's slot is the existing admin one-liner:

-- Fromwebsite.sql §5c
SELECT machine_id, activated_at, last_verified_at FROM activations
  WHERE license_key = 'CLIN-XXXX-XXXX-XXXX';
DELETE FROM activations
  WHERE license_key = 'CLIN-XXXX-XXXX-XXXX' AND machine_id = '<32-hex>';

Then restore the backup ZIP (password = PBKDF2 of the original licence key) and activate normally.

Note: CLAUDE.md's device-transfer design (active/pending slot mode, active_fingerprint, fingerprint trust) is more elaborate than what Fromwebsite.sql actually contains — that's expected, per [[project_device_transfer_lost_laptop_gap]]: the anti-abuse server-side half isn't built yet, and the desktop gracefully defaults to mode: 'active' against today's simpler schema. The §5c delete-the-row approach is what actually works right now.

A5. What today's admin "kill switch" (status='blocked') really does — and doesn't

backend/services/license_gate.py:17-18 states the policy outright: "Reads/edits of existing records are intentionally NOT gated — a lapsed subscription must never lock a counsellor out of their own clinical data." This was built for the billing lapse case, and it applies identically to admin-initiated blocks:

license.py:695-701 — web_status == "expired" (i.e. licenses.status='blocked') → _set_blocked(True) → require_active_license() (license_gate.py:111) starts refusing new work only: creating clients/sessions/meetings, AI beautify/summarize/transcribe, document upload, holistic-summary generation.

src/App.tsx:473-480 — the frontend deliberately stays in the workspace and shows a rose banner rather than navigating to the picker, specifically to avoid a "kicked out → re-enters → kicked again" loop.

All GET reads, search, exports (DOCX/PDF/XLSX/CSV/dossier), PATCH edits, and DELETEs of existing clients/sessions/meetings/documents remain fully available, blocked or not (license_gate.py:41-47 — explicit "UNGATED" list).

So: flipping the kill switch does not stop someone already past the PIN from reading or exporting everything already on disk. It only stops new billable/AI activity.

Small comment-rot found while validating: the _offline_response docstring (license.py:232-234) still says a locally-cached block makes the frontend "navigate back to the selection screen" — the actual behaviour is the App.tsx stay-in-workspace banner above. Harmless (comment only), fix whenever that file is next touched.

A6. Deleting the Supabase licenses row is worse than doing nothing

Traced through license.py:702-706: a missing row makes verify return web_status == "not_found" → the desktop maps this to {"status": "warning", ...} — the same soft treatment as a network hiccup. Crucially, _set_blocked() is not called on this path, so whatever the locally-cached blocked flag already was, it stays that way. Net effect of deleting the row:

Does not additionally restrict the device in any way (no change to local gate state).

Does block that exact key string from ever activating a new device (activate maps a missing row to invalid_key).

Destroys the activations audit trail (cascade delete) and your own ability to look up who the key belonged to.

Destroys your own recovery story — if that licence-key string is ever needed to unwrap db_keys.json's recovery entry (A2), it's now gone from your own records.

Conclusion: never delete a licenses row as a "kill" action. Use the status flag (A5), or the new hard-revoke mechanism below.

PART B — The actual ask: HARD_DEACTIVATE (Emergency)

Goal stated by the founder: maximum admin-side flexibility, with exactly two accepted exceptions — admin still can't read the DB contents directly, and still can't remotely see the counsellor's screen/live machine. Everything else — revive a licence, or kill it so hard that even a thief who cracks the Windows password can't see decrypted data — should be possible.

B1. The wall that can't be engineered around

The admin signal can only reach the laptop over the network (verify/a new poll). If the thief takes the laptop and it never connects to the internet again, no remote action — hard or soft — will ever reach it. This is the same limitation every remote-wipe/MDM system has against an air-gapped device; it is not a bug to fix, it's a property of local-first software. Section B5 below is the mitigation for this specific gap (a staleness auto-lock), and it's the only thing that bounds the exposure window when a device is kept permanently offline.

Given that constraint, everything below assumes the device reconnects to the internet at least once after the admin acts.

B2. What "hard" has to mean, mechanically — three tiers

Today's blocked state is deliberately soft (A5) and must stay soft — it's load-bearing for the honest "your card declined" case. Hard-deactivate needs to be a separate, new state so the two can never be confused. Validation split the enforcement into three tiers, because the original route-block-only design (Tier 1 alone) does not actually stop a technical thief — see PART 0.

Tier 1 — Route lock (blackout the app; reversible remotely)

Plain why: every screen of the app goes dark and stays dark, PIN or no PIN, until you revive the licence from the server. This is the part that shuts down a live, already-open session.Technical why: the Electron UI is the only consumer of the local FastAPI backend, so refusing every stored-data route at the API layer blacks out the whole product even though the process still holds the DEK in memory.

A new Supabase value: licenses.status gains a third option 'active' | 'blocked' | 'revoked' (keep blocked meaning exactly what it means today; revoked is new and stronger). Alternatively an orthogonal boolean (hard_revoked BOOLEAN) if you want soft-block and hard-revoke independently toggleable — recommend the single enum unless a real case needs both simultaneously.

verify must return a distinct status the desktop has never seen before (not reusing "blocked"), e.g. {"status": "revoked", "message": "..."}, so the mapping in license.py can react completely differently from A5's soft path. (Note: revoke can never reach a demo-key machine — demo keys return a canned verify response before any network call, license.py:634-644. Accepted: demo machines are the founder's own.)

On receiving revoked, the backend must:

Force security.set_locked(True) immediately (backend/services/security.py:59).

Persist a new local flag (independent of app_licenses.blocked) that survives restarts and — critically — survives being offline afterward. Once written, this flag is a ratchet: it does not clear itself, and does not depend on future network state to stay in effect. Concrete recommendation: a revoked INTEGER DEFAULT 0 column on app_licenses, mirroring the existing blocked column and _set_blocked() helper pattern (license.py:51-60) — same table license_gate.py already reads, one row per workspace, lives inside the encrypted DB so it can't be flipped by editing a plaintext file.

Make verify_pin() (security.py:125) refuse even a correct PIN while this flag is set. A correct PIN must not undo an emergency revoke.

Extend reset-pin's existing licence re-check (routers/security.py:107-113 — today it refuses when verify returns "blocked") to also refuse "revoked". One-line change, but forgetting it would make Forgot-PIN a revoke bypass.

Add a new middleware (separate from WorkspaceLockMiddleware) that blocks every stored-data route when this flag is set, regardless of whether a PIN exists at all — a device with no PIN configured still has to fully lock. This is more reliable than routing everything through the PIN gate, since PIN setup is optional today. Its allow-list must be even smaller than _LOCK_ALLOW_PREFIXES (main.py:88-101): /api/health, /api/licenses/ (verify is the only path that can ever clear the flag — block it and revive becomes impossible), and /api/system/encryption-status (so the UI can render the right screen). Deliberately NOT allow-listed: the AI generators, /api/backup/auto (no fresh archives while revoked — and the Electron before-quit flow must be confirmed to tolerate the refusal gracefully; it already has a 10s timeout), and /api/security/ unlock (PIN is refused anyway; keep the surface minimal). Whether purge stays reachable is decision E7.

Reactivate (revive) is the symmetric admin action: flip status back to 'active' in Supabase → next successful online verify clears the local flag (mirrors the existing _set_blocked(False) pattern at license.py:683) and PIN entry (or PIN setup, if none existed) is required to re-enter, same as any fresh unlock.

Permanent kill (as opposed to a reversible revoke) = leave the row as status='revoked' indefinitely, and make activate also treat revoked like invalid_key (403, key not found/not usable) so it can never be used to activate any other device either. Never delete the row (A6).

Tier 2 — DPAPI key-scrub (added in validation; the piece that delivers the actual goal; reversible with the licence key)

Plain why: Tier 1 only tells our app to refuse. A thief who is even slightly technical can ignore our app — the silent-unlock ingredient is sitting on the disk in db_keys.json, and the code that uses it ships in every installer. Deleting that ingredient is the difference between "the app refuses" and "the data cannot be opened without the licence key."Technical why: db_keys.json holds two independent wraps of the DEK (A2). Deleting the dpapi entry is a crypto-erase of the silent path: on the next process start, get_encryption_status() reports locked, and the already-built licence-key recovery flow (the cross-machine-restore path) is the only way back in. No new unlock UX needs building — revoke just re-uses it.

On receiving revoked, in addition to Tier 1:

Delete the dpapi protector entry from db_keys.json (services/db_keys.py), keeping the recovery[] entries intact — the legitimate counsellor's data stays fully recoverable with their licence key. Fsync the file; log a no-detail activity row.

The current process still holds _DEK_HEX in memory (B4) — that's acceptable: Tier 1 has already blacked out the API, and the memory copy dies with the process. Optionally also drop the in-memory DEK and close connections for belt-and-braces, but the middleware is the live-session gate either way.

Revive path when a scrub happened: admin flips status='active' → app is online, verify says ok, flag clears → next launch (or immediately, if connections were dropped) the DB is locked → the existing recovery screen asks for the licence key → unwrap via recovery[] → re-wrap a fresh dpapi entry, exactly as the cross-machine restore path already does. Cost of a false alarm: one licence-key entry by the real user. That asymmetry (trivial for the owner, fatal for a thief) is the whole point.

Rule: the staleness auto-lock (B5) must NEVER scrub — Tier 1 route-lock only. A counsellor who is genuinely offline for N days (rural placement, travel) must not come home to a locked DB demanding their licence key because of a timer. Scrubbing is reserved for an explicit admin revoked signal.

Optional polish: since the flag lives inside the (now locked) DB, after a scrub + restart the app can't read why it's locked. A tiny non-secret sidecar marker (e.g. a "revoked": true field in db_keys.json itself) lets the pre-unlock screen show "this licence was suspended — contact support" instead of the generic restore copy. Cosmetic only; not load-bearing.

Tier 3 — Remote wipe (optional; irreversible; recommend NOT in v1)

Plain why: the nuclear option — after this, nobody can ever read the data on that laptop, including the real counsellor with their real key.Technical why: also delete the recovery[] entries from db_keys.json (and optionally the DB file and local backups/ folder, i.e. the existing purge protocol triggered remotely). With every wrap of the DEK gone, the ciphertext is permanent noise.

Not recommended for v1: Tier 2 already covers the stolen-laptop story without destroying anything, the local purge flow already exists for deliberate offboarding, and a remotely-triggered irreversible destroy is exactly the kind of thing that goes catastrophically wrong on a false positive (wrong key revoked, counsellor's only copy gone — the no-cloud-copy design in A4 cuts both ways). If ever built, it needs its own wire value ("wipe"), its own scarier runbook, and probably a server-side two-step confirmation. Parked as decision E8.

B3. The "already open and unlocked" session problem

verify today only fires once, on workspace entry (src/App.tsx:472, effect keyed on view). If the counsellor (or the thief, having found it already unlocked) just stays inside the workspace without navigating away and back, an admin's revoke won't be seen for an indefinite time. A periodic re-verify poll needs adding — e.g. every 5–15 minutes while inside a workspace — purely so a live, already-unlocked session gets shut down promptly instead of only on the next cold start. This is a small, additive change (a setInterval alongside the existing [view] effect) but is required for hard-deactivate to have real teeth against an in-progress session, not just against future launches.

Two implementation notes found in validation:

The poll keeps working while PIN-locked with no extra work: /api/licenses/ is already on the workspace-lock allow-list (main.py:91), so a PIN-locked-but-running app still hears a revoke. Good — no change needed, just don't remove that allow-list entry.

Log spam guard: _log_verify_outcome (license.py:544-566) writes an activity-log row for every non-healthy verify. A 5-minute poll on an offline laptop = ~288 offline rows/day, and the Support Diagnostic Log rotates at 30 days + a row cap — the spam would flush real crash evidence out of the log. The poll must log only on outcome change (keep the last outcome in memory, skip the row when it's unchanged).

Auto-login must respect the flag: on startup App.tsx reads private_last_workspace and enters the workspace straight from checkLicense (App.tsx:471) before any verify. The local check response must carry the revoked flag so a revoked machine lands on the hard-lock screen immediately instead of flashing into the workspace and waiting for the first 423.

B4. Enforcement point given the DEK is already resident — two different jobs

By the time a mid-session revoke arrives, the backend process has already unwrapped the DEK into memory and has open SQLite connections — you cannot retroactively "un-decrypt" those. So enforcement is two different jobs with two different tools:

The live session (process running, DEK in memory): the API layer is the tool. The Tier 1 middleware refuses every stored-data route, and since the Electron frontend is the only consumer of this backend, that blackens the whole UI even though the process technically still holds the key until it's killed/restarted. Nothing better is possible against a live process — accept it and keep the poll interval short.

Everything after the process ends (reboot, app relaunch, thief trying tools later): the key-scrub (Tier 2) is the tool. Once the dpapi entry is gone from db_keys.json, no restart, no reinstall, no third-party SQLite tool, and no older copy of our own app can open the DB without the licence key. The route-block flag protects the app; the scrub protects the data.

Plain version: the middleware is a guard standing in front of an open safe — good enough while the guard is there, useless once someone comes back later with their own tools. The scrub closes the safe and throws away the spare key that was taped to it.

B5. Companion policy: bounding the "stays offline forever" exposure

Because B1 means a permanently-offline device is unreachable by any revoke, recommend adding (as a separate, smaller feature): if the app has not completed a successful online verify within N days (e.g. 7–14), it auto-locks itself — same route-lock mechanism as B2 Tier 1, just triggered by staleness instead of an explicit admin signal. This is the only thing that puts a ceiling on how long a stolen-and-kept-offline laptop stays readable. It's a real UX trade-off (legitimate counsellors need periodic internet access even if they mostly work offline) and should be a deliberate, disclosed policy decision, not a silent change.

The staleness clock is computed locally from app_licenses.last_verified_at, which is already written on every successful online verify (license.py:673-679) — so no server change is needed, confirming D7.

Two constraints on this feature, decided here so they don't get re-litigated later:

Staleness never scrubs (B2 Tier 2 rule 4). It route-locks only. A timer must never be able to put a legitimate offline counsellor's DB into locked-needs-licence-key state; only an explicit admin revoked signal earns that.

Clock rollback defeats it, and that's accepted. The check compares last_verified_at against the system clock; a thief who sets the clock back freezes the timer. The existing product policy (smoke-test decision F4, 2026-06-16) is deliberately tolerant of wrong clocks because real customers have wrong clocks — adding clock-tamper detection would punish them to inconvenience a thief who can be defeated properly by Tier 2 the moment the device goes online. State this honestly in the threat table (B6) rather than pretending the staleness lock is stronger than it is.

B6. Honest threat model — what each tier actually stops (added in validation)

Attacker scenario

Today (blocked only)

Tier 1 route lock

Tier 1 + Tier 2 key-scrub

Casual thief, can't get past Windows login

Already stopped (Windows login + DB encryption at rest)

Same

Same

Thief past Windows login, uses the app

Full read/export of everything (A5)

Locked within one poll interval once online; locked at next launch regardless

Same, plus after any restart the DB is unopenable without the licence key

Technical thief past Windows login, ignores the app (own tools + db_keys.json)

Full access — DPAPI unwrap needs nothing from us

Unchanged — full access. This is why Tier 1 alone fails the stated goal

Stopped from the moment the scrub lands (device must come online once)

Thief who ALSO has the licence key string

Full access (key opens recovery wrap + all backup ZIPs)

Unchanged

Unchanged — the key is a password; no server action rewinds local crypto

Thief who imaged the disk before the revoke arrived

Full access on the copy

Unchanged on the copy

Unchanged on the copy — a scrub can't reach a copy taken earlier

Laptop kept permanently offline

Exposure unbounded

Unbounded (B1) until staleness lock (B5) fires — and clock rollback can freeze that timer

Same as Tier 1 (scrub also needs the network to be triggered)

Plain reading of the table: Tier 2 converts "thief with the Windows password" from game over into needs the licence key too. Nothing converts "thief with the Windows password AND the licence key" into anything better — that combination must be treated like a leaked password: revive is refused, the key is permanently dead (B2 Tier 1 item 5), and the customer conversation is about what was on the device, same as any breach.

PART C — Desktop-side (this repo) build checklist

#

Piece

Where

Notes

1

Handle new verify response status: "revoked" distinctly from "blocked"

backend/routers/license.py (_verify_license_impl, ~line 695)

Do not fold into existing blocked branch.

2

New persistent "hard revoked" flag, separate from app_licenses.blocked

backend/database.py — recommend app_licenses.revoked INTEGER DEFAULT 0 column

Mirrors the existing blocked column + _set_blocked() helper pattern (license.py:51-60); same table license_gate.py already reads; lives inside the encrypted DB. Must survive restarts and offline periods; only cleared by a fresh successful online verify reporting active again.

3

Force-lock on revoke; refuse correct PIN while revoked

backend/services/security.py (set_locked, verify_pin)

Correct PIN must not bypass an emergency revoke.

4

Extend reset-pin's licence re-check to refuse "revoked" too

backend/routers/security.py (~line 110 — already refuses "blocked")

One-line change; forgetting it makes Forgot-PIN a revoke bypass.

5

New middleware: block all stored-data routes when revoked, PIN or no PIN

new file alongside WorkspaceLockMiddleware (main.py:125)

Don't overload the existing PIN middleware — PIN is optional, this must not be. Allow-list smaller than _LOCK_ALLOW_PREFIXES: only /api/health, /api/licenses/ (the sole un-revoke path), /api/system/encryption-status (+ purge routes iff E7 says yes). Explicitly NOT /api/backup/auto.

6

Tier 2: scrub the dpapi entry from db_keys.json on revoke (keep recovery[])

backend/services/db_keys.py + call site in license.py's revoked branch

The piece that holds after restart (B2 Tier 2, B4). Never triggered by staleness (B5). Optional sidecar "revoked" marker in db_keys.json for pre-unlock screen copy.

7

Periodic re-verify while inside a workspace (not just on entry)

src/App.tsx (~line 472 effect)

e.g. setInterval 5–15 min. Works while PIN-locked already (main.py:91 allow-list). Log verify outcome only on CHANGE — an offline poll must not flood the 30-day Support Diagnostic Log (B3).

8

check response carries the revoked flag; auto-login respects it

backend/routers/license.py (check endpoint) + src/App.tsx auto-login

Otherwise startup flashes into the workspace off checkLicense (App.tsx:471) before the first verify.

9

activate treats revoked like invalid_key (403)

backend/routers/license.py (activate_license, ~line 410)

Prevents reuse of a permanently-killed key on any other device.

10

Frontend messaging for the revoked state

src/App.tsx, SelectionPage.tsx

Distinct copy from the existing soft "subscription paused" banner — this one should read as a hard lock, not a nudge to renew. After a Tier 2 scrub + restart, the pre-unlock screen should say "licence suspended — contact support" (sidecar marker, C6).

11

Activity-log rows: revoke received, scrub performed, revive completed

services/activity_log.py call sites

Support evidence trail; no key, no reason text with PHI — outcome + timestamp only.

12

(Companion, optional) staleness auto-lock if no successful verify in N days

security.py + startup check against app_licenses.last_verified_at

Separate feature, see B5 — route-lock ONLY (never scrubs), needs its own decision on N and messaging. Clock-rollback caveat accepted.

PART D — Web-side (separate Next.js/Supabase project) build checklist

#

Piece

Notes

1

licenses.status gains 'revoked' (or new hard_revoked BOOLEAN, see B2.1)

Keep 'blocked' semantics completely unchanged — do not let revoke and block share a column value. Concrete migration: the column was created with an inline CHECK (Fromwebsite.sql §1, status IN ('active','blocked')), so widening it means replacing the constraint, not just writing a new value: sql\nALTER TABLE licenses DROP CONSTRAINT licenses_status_check;\nALTER TABLE licenses ADD CONSTRAINT licenses_status_check CHECK (status IN ('active','blocked','revoked'));\n (Confirm the auto-generated constraint name first with \d licenses / information_schema.check_constraints — Postgres names inline column checks <table>_<column>_check by convention.)

2

Audit columns mirroring existing blocked_reason/blocked_at

e.g. revoked_reason, revoked_at

3

/api/licenses/verify returns a distinct status: "revoked" (not "expired") when licenses.status='revoked'

This is a new wire value the desktop doesn't currently know — must ship both sides together.

4

/api/licenses/activate returns invalid_key-equivalent refusal for a revoked key

Prevents reactivation elsewhere on the same key.

5

Admin one-liners (SQL, until a real admin UI exists)

sql\n-- Emergency hard-deactivate:\nUPDATE licenses SET status='revoked', revoked_reason='stolen device', revoked_at=NOW() WHERE license_key='...';\n-- Revive:\nUPDATE licenses SET status='active', revoked_reason=NULL, revoked_at=NULL WHERE license_key='...';\n

6

Extend admin_license_overview view to surface status='revoked' rows

Fromwebsite.sql §4

7

(Companion) if adopting B5, no server change needed — staleness is computed client-side from last_verified_at already cached locally

Confirm desktop already has what it needs (app_licenses.last_verified_at) before assuming this is server-side.

PART E — Open decisions before building

Single enum vs. orthogonal boolean for revoke vs. block (B2.1) — recommend the enum unless a real scenario needs both simultaneously (e.g. "revoked AND separately billing-blocked" reads as one state either way).

Mandatory PIN? Hard-deactivate only has teeth if the device gets fully locked regardless of PIN setup (per B2.3's middleware approach) — confirm the middleware-everything approach rather than relying on PIN semantics, since PIN today is optional.

Staleness window (B5) — how many days offline before auto-lock, and what messaging counsellors see when it triggers on a legitimate device that was genuinely offline (e.g. rural placement, travel).

Poll interval (B3) — balance "revoke takes effect quickly" against extra network chatter / battery on laptops that are mostly offline by design.

Legal/process layer — none of this is a substitute for a documented policy on when the founder will actually pull this trigger (org request, confirmed theft report, etc.) versus the softer billing-block path. Worth a short internal runbook once built.

Does revoke always scrub (Tier 2), or is scrub a separate stronger action? Recommendation: revoke always scrubs. The scrub is reversible with the licence key (no data loss, one key entry of friction on a false alarm), and a revoke that doesn't scrub is theatre against exactly the attacker this feature exists for (B6 row 3). Keeping them as one action also keeps the runbook to two verbs: revoke, revive. The staleness auto-lock is the one trigger that must never scrub (B5).

Is purge reachable while revoked? An org offboarding a stolen/departed device may legitimately want "erase whatever comes back online." Recommendation: yes — allow-list the purge route in the revoke middleware; erasure is strictly aligned with the intent of a revoke, and purge already has its own hard-confirm UI. If declined, the erase path is: revive → purge → re-revoke, which is clumsier but workable.

Tier 3 remote wipe in v1? Recommendation: no (B2 Tier 3) — Tier 2 covers the stolen-laptop story reversibly; a remotely-triggered irreversible destroy on a no-cloud-copy product is a false-positive catastrophe waiting to happen. Revisit only if an org contract demands it, and then with a server-side two-step confirmation.

PART F — Master Implementation Checklist

Ordered by dependency. Web contract (F2) has to exist before desktop code calling it means anything; desktop enforcement (F3) has to exist before the wire contract does anything real; testing (F4) is what proves B1/B3/B4's assumptions actually hold instead of just reading true on paper.

F1. Decisions to lock in first (blocks everything else — see PART E)

Choose enum (status: 'active'|'blocked'|'revoked') vs. orthogonal hard_revoked boolean (E1)

Decide PIN becomes effectively mandatory for the revoke path via all-routes middleware, independent of whether a PIN is configured (E2)

Pick the staleness window N for offline auto-lock, if adopting B5 (E3)

Pick the in-workspace re-verify poll interval (E4)

Write the short internal runbook: when does the founder actually pull revoked vs. blocked? (E5)

Confirm "revoke always scrubs" vs. scrub as a separate action (E6 — recommended: always scrubs)

Decide whether purge stays reachable while revoked (E7 — recommended: yes)

Confirm Tier 3 remote wipe is out of v1 (E8 — recommended: out)

F2. Web side — Supabase schema

Replace the status CHECK constraint to admit 'revoked' (see D1 — DROP + re-ADD, confirm auto-generated constraint name first)

Add revoked_reason TEXT, revoked_at TIMESTAMPTZ audit columns

Extend admin_license_overview view to surface revoked rows (Fromwebsite.sql §4)

Write + save the admin one-liners (revoke / revive) next to the existing §5a/§5b block in Fromwebsite.sql

F3. Web side — API contract

/api/licenses/verify returns distinct {"status": "revoked", "message": "..."} when licenses.status='revoked' (never reuse "expired")

/api/licenses/activate refuses a revoked key the same way it refuses invalid_key (403, key not found/not usable)

Confirm machine_id handling is unaffected (revoke doesn't touch the fingerprint-trust logic already in place for device transfer)

Document the new wire values in whatever file mirrors DeactivatePlanDoneSummary.md's "PART B — wire contract" for this feature

F4. Desktop side — backend

_verify_license_impl (backend/routers/license.py ~695) branches on "revoked" separately from "blocked"

New persistent revoke flag: app_licenses.revoked column + _set_revoked() helper mirroring _set_blocked() (license.py:51-60)

security.set_locked(True) forced the instant a revoke is received

verify_pin() refuses a correct PIN while the revoke flag is set

reset-pin licence re-check (routers/security.py:~110) extended to refuse "revoked" as well as "blocked"

New middleware blocking all stored-data routes when revoked, independent of PIN existing at all — allow-list only /api/health, /api/licenses/, /api/system/encryption-status (+ purge iff E7)

Tier 2 scrub: delete the dpapi entry from db_keys.json on revoke (keep recovery[]); optional "revoked" sidecar marker for pre-unlock screen copy

check endpoint returns the revoked flag (for auto-login gating)

activate_license() treats a revoked response like invalid_key (403)

Flag only clears on a fresh successful online verify reporting active again — never clears itself locally

Activity-log rows for revoke received / scrub done / revive done (no key, no PHI)

(If adopting B5) staleness check: track days since last successful verify (app_licenses.last_verified_at), auto-set the route-lock only (never the scrub) past N days offline

F5. Desktop side — frontend

Periodic re-verify while inside a workspace (src/App.tsx, alongside the [view]-keyed effect at ~line 472), not just on entry — logging deduped to outcome changes (B3)

Auto-login path reads the revoked flag from checkLicense and lands on the hard-lock screen, never flashes into the workspace

Distinct hard-lock messaging in App.tsx / SelectionPage.tsx for "revoked" — must read as final, not as a renewal nudge

Confirm the revoked screen has no path back into the workspace other than a fresh online verify clearing the flag

npx tsc --noEmit clean after changes

F6. Testing / verification

Simulate revoke while a workspace is open and idle mid-session → confirm lock happens within one poll interval, not just on next launch

Simulate revoke while fully offline → confirm the device stays unlocked until it reconnects (expected, per B1) and locks promptly once it does

Confirm a correct PIN cannot clear an active revoke, and Forgot-PIN (reset-pin) refuses while revoked

Scrub drill: revoke → confirm db_keys.json has no dpapi entry → restart app → confirm encryption-status reports locked and no stored-data route serves → enter licence key → confirm recovery unlock + DPAPI re-wrap works (this is the existing cross-machine-restore flow being re-used)

Confirm revive (status back to 'active') restores access on next online verify — including the post-scrub variant (revive + licence-key entry)

Confirm app close while revoked doesn't hang: the Electron before-quit backup call is refused by the middleware and the existing 10s timeout releases the quit

Confirm a revoked key cannot activate a second, different machine

Confirm existing soft blocked (billing lapse) path is completely unaffected — no shared code path accidentally hard-locks or scrubs a billing-lapsed counsellor

Confirm an offline 5-min poll for a day produces at most a handful of Support Diagnostic Log rows, not hundreds (dedupe works)

(If adopting B5) confirm staleness auto-lock fires at N days, does NOT scrub, and is clearly distinguishable from an admin-initiated revoke in the UI copy

F7. Docs / process

Update CLAUDE.md License Expiry / router reference sections to mention the new revoked state alongside existing blocked semantics

Update .claude/commands/LicenseExpiry.md with the three-state model (ok / blocked / revoked)

Update .claude/commands/WorkspaceLock.md: the "PIN is not the DB key" framing gains a sibling — "revoke IS allowed to reach the DB key path (Tier 2 scrub)"

Customer-facing copy (Help page / org onboarding doc): (a) the licence key is a password — anyone holding it can open backups and recover the database, so store it like a password (B6, honest limit #2); (b) off-device backup copies are the org's responsibility — no cloud copy exists and support cannot reconstruct data after a loss (A4)

Save the finished runbook (F1 last item) somewhere findable by future-you at 2am — include the "thief also has the key" breach script (B6 plain reading)



===========================================SUMMARY===========================================

Verdict: your doc is factually solid — every code reference in it checked out against the real code — but the design had oneserious gap, which I've now fixed in the doc: the original "hard deactivate" (a flag that makes the app refuse to serve) wouldNOT have stopped a technically capable thief. The missing move is deleting the silent-unlock ingredient from the disk.

What I validated

I re-checked every file and line number the doc cites (db_keys.py, security.py, license_gate.py, license.py, App.tsx, main.py,Fromwebsite.sql). All accurate — including the two most important background claims: deleting a Supabase licence row reallydoes map to a harmless "warning" on the desktop while destroying your audit trail (so "never delete a row" stands), and thecurrent kill switch really does leave all reading/exporting open by design.

The gap, in plain language

Your app keeps the database key on the laptop, wrapped by a Windows feature called DPAPI so that only "this Windows user onthis machine" can unwrap it. That's what lets the app open silently every morning. But it means everything needed to open thedatabase sits on the disk. Your planned revoke flag only tells our app "refuse to serve pages" — a thief who ignores our appand uses their own tools (the unwrap recipe ships in every installer) gets the data anyway. A guard in front of an open safeis useless once someone comes back later with their own tools.

The fix (now "Tier 2" in the doc): when the revoke arrives, the app also deletes the DPAPI entry from db_keys.json.Technically, that file holds two independent wrappings of the same database key — the silent DPAPI one, and a "recovery" onelocked with the exact licence-key string. Delete the DPAPI one and the database only opens by typing the licence key. Yourreal counsellor knows their key (a false alarm costs them one key entry, using the already-built cross-machine-restore unlockscreen — no new UX needed). A thief doesn't — and a fresh key bought from your own site won't work, because the wrap is boundto the exact original key string.

Honest limits I added (nothing can fix these — worth knowing at 2am)

A laptop kept offline forever never hears the revoke — your staleness auto-lock idea (B5) is the only ceiling, and I notedit's defeatable by rolling the clock back (accepted, consistent with your existing wrong-clocks policy).

A thief who also has the licence key string wins regardless — the key opens the recovery wrap and every backup ZIP. Thelicence key is a password; that's a customer-communication item, now in F7.

A disk copied before the revoke arrived keeps the pre-deletion ingredients.

Other fixes to the doc

Forgot-PIN would have been a revoke bypass — reset-pin already refuses admin-blocked licences (routers/security.py:110); oneline must extend that to revoked. Added to C/F4.

Auto-login would flash into the workspace before the first verify — the local check response must carry the revoked flag.Added.

Your 5-minute poll would flood the Support Diagnostic Log (~288 "offline" rows/day, flushing real crash evidence out of the30-day window) — log only on outcome change. Added.

Supabase migration detail: status has an inline CHECK constraint allowing only ('active','blocked') — adding 'revoked' meansdropping and re-adding the constraint, not just writing the value. Concrete SQL added to D1.

Concrete flag storage recommendation: an app_licenses.revoked column mirroring the existing blocked column, not a new table.

Three new open decisions (E6–E8) with recommendations: revoke should always scrub (reversible, so cheap on false alarms);purge should stay reachable while revoked; and Tier 3 "remote wipe" (also deleting the recovery entries — permanent, even forthe real owner) should stay out of v1, because an irreversible remote destroy on a product with no cloud copy is afalse-positive catastrophe waiting to happen.

Added a threat-model table (B6) showing exactly which attacker each tier stops, a plain-English PART 0 at the top, andmatching rows in every checklist (C, D, F) including a scrub-and-recover test drill.

One nice discovery along the way: the staleness auto-lock needs no server work at all — last_verified_at is already writtenlocally on every successful verify, confirming your D7 hunch.
