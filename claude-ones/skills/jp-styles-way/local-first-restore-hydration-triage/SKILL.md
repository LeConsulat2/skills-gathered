---

name: local-first-restore-hydration-triage
description: Use this when local-first data exists somewhere in the app but does not appear in the expected screen after app restart, PIN unlock, route entry, draft/session restore, Home-card navigation, sidebar navigation, autosave, or one-shot localStorage prefill — or when clicking a rendered row/card does nothing because lookup state is empty. Prioritize restore-key and hydration-path analysis before assuming data loss.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Local-First Restore & Hydration Triage Skill

## Purpose

Use this skill for bugs where the app has not necessarily lost data, but the current screen fails to restore, hydrate, or attach the right local state.

Typical symptoms:

* data appears on Home but not inside the expected page
* draft/session/audio exists in the database but not in the editor
* Unfinished Notes rows/cards render but clicking does nothing
* app restart changes what appears
* first entry after PIN unlock behaves differently from later navigation
* Home-card entry works but sidebar/direct entry does not
* client-attached records restore correctly, but walk-in/no-client records do not
* one-shot `localStorage` prefill works once, then silently fails
* a page assumes `clients`, `sessions`, or profile data is already loaded when it is not

Treat these as **restore-key / hydration-path bugs**, not immediate data-loss bugs.

Solved reference cases: `bugs-fixed/015-02072026.md` — Issue 5 (walk-in audio restore after restart) and Issue 8 (PIN-boot clients hydration dead click). Read these first; they are worked examples of this skill's method with exact files and line numbers.

## Role Discipline

You are the Advisor.

Do directly:

* classify the restore/hydration bug
* inspect restore keys and route-entry paths
* compare where the data exists vs where it fails to appear
* inspect PIN/unlock/client hydration timing
* write implementation briefs for Worker
* verify diffs and tests yourself

Delegate to Worker:

* implementation edits
* migration edits
* repetitive file changes
* test creation

Do not trust Worker summaries without checking the diff, migration safety, and runtime verification notes.

## Investigation Order

Do not start by broad-refactoring restore logic.

Follow this order.

### 1. Separate "data lost" from "data not restored here"

Write down:

```markdown
Data existence:
- Where does the data still appear?
- Home card?
- DB row?
- diagnostic log?
- queue list?
- another route?

Missing view:
- Where does the user expect it to appear?
- Which page/panel?
- Which entry path?
- After restart, unlock, route change, or autosave?
```

Example:

```markdown
Data exists:
- Untranscribed audio appears on Home's aggregate card.

Missing view:
- Same recording does not restore inside the walk-in draft after app restart.
```

If the data appears anywhere, do not call it data loss yet.

### 2. Classify the bug

Use one or more labels:

* restore-key mismatch
* route-entry hydration gap
* PIN-unlock hydration race
* one-shot localStorage prefill failure
* stale always-mounted page state
* client-attached vs walk-in/no-client mismatch
* pre-save record identity gap
* aggregate Home query vs page-specific query mismatch
* stale closure over empty hydrated data
* first-load 423 boot window

Example:

```markdown
Primary: client-attached vs walk-in/no-client restore-key mismatch
Secondary: pre-save session identity gap
Related: Home aggregate query restores broader data than in-page query
```

### 3. Find where the data exists

Search narrowly for the source of truth:

```bash
grep -R "audio_queue\|all-drafts\|drafts\|prefill_\|loadClients\|workspace-unlocked" -n backend src
grep -R "localStorage.setItem\|localStorage.getItem\|removeItem" -n src
grep -R "selectedClient\|selectedSession\|restoredQueueItems" -n src/pages src/components
```

Ask:

```markdown
Which query finds the data when it appears?
Which query fails to find it when it disappears?
Are those queries using the same key?
```

Common keys to compare:

* `client_id`
* `session_id`
* `draft_id`
* `workspace_type`
* `status`
* `prefill_session_id`
* `prefill_status_filter`
* selected client/session state
* route state
* localStorage one-shot keys

### 4. Compare Home aggregate restore vs in-page restore

Home often uses a broad aggregate query.

The page often uses a narrower query.

Ask:

```markdown
Does Home show this because it queries all pending records?
Does the page hide this because it filters by client_id only?
What key would uniquely attach this record to the current page?
```

Bad pattern:

```ts
if (!selectedClient?.id) {
  setRestoredQueueItems([]);
  return;
}
```

This may be correct for client-attached sessions but wrong for walk-in/no-client drafts.

Better pattern:

```ts
if (selectedClient?.id) {
  restore by client_id;
} else if (selectedSession?.id) {
  restore by session_id;
}
```

Only use `session_id` if it uniquely identifies the current walk-in draft.

### 5. Inspect PIN / boot / unlock hydration timing

For first-load bugs after PIN lock or workspace unlock, inspect:

* app boot status checks
* 423 responses during locked state
* one-shot `loadClients()` calls
* profile fetch after unlock
* `handleUnlocked`
* auto-login path
* sidebar-triggered hydration
* always-mounted pages that survive navigation

Ask:

```markdown
Did the first hydration attempt fail because the workspace was locked?
After unlock, what explicitly re-runs the hydration?
Is there a path where `clients=[]` becomes treated as final?
```

Danger pattern:

```ts
useEffect(() => {
  if (profile) loadClients();
}, []);
```

If this runs during a PIN-locked 423 window and never re-runs after unlock, the app can enter a workspace with permanently empty hydrated state.

### 6. Inspect one-shot localStorage handoffs

Many route-entry flows use one-shot keys.

Check:

```bash
grep -R "prefill_" -n src
```

Ask:

```markdown
Who writes the key?
Who consumes it?
When is it removed?
What happens if the target page is already mounted?
What happens if required data has not hydrated yet?
```

Common trap:

```ts
const id = localStorage.getItem("prefill_session_id");
localStorage.removeItem("prefill_session_id");
if (!sessions.length) return;
```

This loses the instruction before the page has enough data to execute it.

### 7. Account for always-mounted pages

If a page stays mounted while navigation changes, do not assume mount effects re-run.

Ask:

```markdown
Is the page remounted, or only shown/hidden?
Does selected state survive navigation?
Does an effect depend on active panel, selected workspace, or loaded data?
```

Always-mounted page bugs often look like route bugs but are actually stale state bugs.

### 8. Check pre-save identity gaps

Some local-first workflows create data before the final DB row exists.

Examples:

* recording audio before a draft has a `session_id`
* autosave creating the draft row later
* Save as Draft creating the row after temporary local state already exists

Ask:

```markdown
Was the child record created before the parent row had an id?
Is there a back-fill step after the parent id becomes known?
Is the back-fill safe if the child job is currently transcribing?
```

Good pattern:

```markdown
1. Create child record with nullable foreign key.
2. Once parent id exists, PATCH child record to attach it.
3. On restore, match by the strongest available key.
4. Keep old/null rows recoverable through Home aggregate view.
```

### 9. Migration safety for restore-key fixes

If the fix needs a new column, require:

```markdown
- nullable column
- PRAGMA table_info guard
- ALTER TABLE only if missing
- re-runnable init_db()
- no destructive migration
- old rows still recoverable
- new rows get the stronger key
```

Never require old data to be perfectly migrated unless there is a safe deterministic mapping.

## Worker Brief Template

```markdown
You are fixing a local-first restore/hydration bug.

Bug summary:
- [What exists where]
- [What fails to appear where]
- [When it happens: restart / unlock / route entry / autosave / Home card / sidebar]

Classification:
- Primary: [restore-key mismatch / PIN hydration race / one-shot prefill failure / etc.]
- Secondary: [if any]

Known broken sequence:
1. [exact steps]

Known working or partial recovery sequence:
1. [exact steps]

Likely files:
- [file paths]

Focus areas:
- Compare Home aggregate query vs in-page restore query.
- Identify the restore key currently used.
- Check client-attached vs walk-in/no-client path.
- Check whether the page is already mounted before localStorage prefill is consumed.
- Check whether PIN-locked boot causes 423 during first hydration.
- Check whether clients/sessions/profile are reloaded after unlock.
- Check whether selected state survives navigation.

Constraints:
- Do not broad-refactor.
- Do not globally reset page state on every navigation.
- Do not treat visible absence as data loss until DB/Home/queue sources are checked.
- Prefer the smallest stronger restore key.
- Preserve old rows and pre-migration recovery.
- Add regression tests if existing test setup supports it.
- Otherwise document manual verification steps.

Completion criteria:
- Existing data still appears from Home aggregate recovery.
- The same data restores in the expected page when a unique key exists.
- App restart does not lose the restore link.
- PIN unlock rehydrates required state.
- Home-card, sidebar, and direct route entry reach equivalent hydrated state.
- Walk-in/no-client records do not bleed into unrelated walk-in drafts.
- Pre-migration rows remain recoverable.
```

## Advisor Verification Checklist

```markdown
[ ] The fix identifies where the data actually existed.
[ ] The fix targets the restore key or hydration path, not only the visible symptom.
[ ] Home aggregate and in-page restore behavior are both understood.
[ ] PIN/unlock 423 timing is handled if relevant.
[ ] One-shot localStorage keys are not consumed too early.
[ ] Always-mounted page state is accounted for.
[ ] Client-attached and walk-in/no-client paths are both covered.
[ ] New DB columns are nullable and migration-safe.
[ ] Old/pre-migration records remain recoverable.
[ ] Runtime verification includes app restart or unlock if that was part of the bug.
```

## Anti-Patterns

Avoid:

```markdown
- Calling it data loss before checking Home/DB/queue sources.
- Fixing by globally resetting all state on route change.
- Showing all unassigned records inside every walk-in draft.
- Consuming and deleting prefill localStorage before data is hydrated.
- Treating `clients=[]` after a locked boot as final.
- Assuming entering from Home and entering from sidebar initialize the same state.
- Adding a non-null DB column for existing local data.
- Breaking old rows that lack the new restore key.
- Trusting Worker summaries without checking migration and runtime behavior.
```

## Key Principle

In a local-first app, "missing from this screen" usually means one of these before it means data loss:

```markdown
- the restore key is too weak
- the correct key does not exist yet
- the app hydrated while locked
- the page consumed a one-shot prefill too early
- the page stayed mounted with stale state
- Home uses an aggregate query but the page uses a narrow query
- client-attached and walk-in/no-client paths diverged
```

Find where the data still exists, then find why this route cannot attach it.
