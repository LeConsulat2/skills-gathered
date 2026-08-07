---

name: ui-state-regression-triage
description: Use this when a UI bug involves disabled controls, missing hover/cursor, unclickable rows/cards, first-load behavior, route-entry differences, stale selected state, or workflow busy-state leakage. Prioritize targeted state/route analysis before broad reproduction tooling.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# UI State Regression Triage Skill

## Purpose

Use this skill for UI regressions where the app visibly renders but interaction state is wrong.

Typical symptoms:

* button/card/row is visible but cannot be clicked
* hover cursor looks disabled when action should be available
* disabled styling does not match actual behavior
* first app load behaves differently from later navigation
* entering a screen from Home works, but entering from sidebar/panel/direct route does not
* controls are blocked after Beautify, Transcribe, Save, Export, Cancel, Restore, or similar workflow
* user must leave and re-enter through a specific path before UI starts working

Treat these as **state-gate bugs**, not simple click bugs.

## Role Discipline

You are the Advisor.

Do directly:

* classify the bug
* inspect relevant state gates and route-entry paths
* compare working path vs broken path
* write implementation briefs for Worker
* verify diffs and tests yourself

Delegate to Worker:

* implementation edits
* test creation
* repetitive file modifications

Do not trust Worker completion summaries without checking the diff and test output.

## Investigation Order

Do not start with broad reproduction tooling unless necessary.

Follow this order:

### 1. Parse the user report into symptoms

Write down:

```markdown
Symptom A:
- What is visibly wrong?
- Which UI element?
- Which workflow?

Symptom B:
- What entry path is broken?
- What entry path works?
- What exact user sequence triggers it?
```

Example:

```markdown
A. After Beautify, trying to Transcribe shows disabled hover/cursor incorrectly.
B. On fresh app open, entering Unfinished Notes immediately makes note cards/rows unclickable. Going to other panels and back does not fix it. Returning Home and re-entering through the Home unfinished draft card makes it work.
```

### 2. Classify the bug before searching widely

Use one or more of these labels:

* route-entry parity bug
* first-load hydration race
* stale selected item/session/client state
* global busy boolean leaking across workflows
* disabled predicate too broad
* cursor/disabled styling mismatch
* overlay or pointer-events blocker
* async cleanup failure

For the example above, classify as:

```markdown
Primary: route-entry parity bug
Secondary: first-load hydration/stale state bug
Related: disabled predicate/cursor mismatch between Beautify and Transcribe
```

### 3. Inspect the last relevant commit/checklist first

If the user mentions a checklist or last commit, inspect that before random searching.

Preferred commands:

```bash
git show --stat HEAD
git show HEAD -- path/to/relevant/file
git log --oneline -5
```

If the user names a file, inspect it directly first.

Avoid reading build/deployment docs unless the bug is build/runtime-environment related.

### 4. Compare working entry path vs broken entry path

This is the highest-value step.

Find:

* Home/dashboard card click handler
* sidebar/panel/direct route handler
* route state passed during navigation
* selected client/session/draft initialization
* panel mount/useEffect logic
* list item click handler

Ask:

```markdown
What does the working Home entry path initialize that the broken direct/sidebar path does not?
```

Look for differences in:

* selected client ID
* selected student ID
* selected session ID
* selected draft ID
* active panel
* current workspace
* pending draft list
* loaded client/session map
* route state
* query params
* localStorage/sessionStorage restore
* initial load flags

### 5. Inspect disabled and cursor predicates

Search narrowly for the UI elements and state gates.

Useful search terms:

```bash
grep -R "cursor-not-allowed\|pointer-events-none\|disabled=" -n src
grep -R "beautif\|transcrib\|isProcessing\|busy\|loading" -n src/pages src/components
grep -R "unfinished\|draft" -n src/pages src/components src/utils
```

For each disabled condition, answer:

```markdown
Is this global, or scoped to the current item/session/client?
```

Bad pattern:

```ts
disabled={transcribing || beautifying}
```

Better pattern:

```ts
disabled={
  transcribingForSessionId === session.id ||
  beautifyingForSessionId === session.id
}
```

Only use scoped state where the workflow is item-specific.

### 6. Check for stale closures and hydration races

Inspect `useEffect` dependencies around:

* initial data load
* draft/session loading
* selected item setup
* active panel changes
* Home card navigation
* sidebar navigation
* app restart restore

Look for:

* empty dependency arrays that should include data/state
* click handlers depending on stale selected IDs
* derived state initialized once before data arrives
* guards like `if (!clients.length) return`
* state that is only set by one navigation path

### 7. Only then reproduce live if needed

Use Playwright/dev server only after targeted static inspection, or if the cause is still unclear.

Do not install browsers, start servers, or run full app reproduction before:

* comparing entry paths
* checking disabled predicates
* inspecting relevant state initialization

Live reproduction is useful, but it should confirm a narrowed hypothesis, not replace triage.

## Worker Brief Template

When delegating, give the Worker this structure:

```markdown
You are fixing a UI state-gate regression.

Bug summary:
- [Symptom A]
- [Symptom B]

Classification:
- Primary: [route-entry parity / hydration / disabled predicate / etc.]
- Secondary: [if any]

Known broken sequence:
1. [exact steps]

Known working sequence:
1. [exact steps]

Likely files:
- [file paths]

Focus areas:
- Compare Home/dashboard entry handler vs sidebar/panel/direct entry handler.
- Check selected draft/session/client initialization.
- Check disabled/cursor predicates for Beautify and Transcribe.
- Check whether global busy booleans block unrelated controls.
- Check whether first-load hydration leaves stale or missing IDs.

Constraints:
- Do not broad-refactor.
- Do not change unrelated UX.
- Prefer minimal state-scoping fix.
- Add regression tests if existing test setup supports it.
- Otherwise document manual verification steps.

Completion criteria:
- Fresh app launch → enter Unfinished Notes immediately → unfinished note rows/cards are clickable.
- Sidebar/panel entry and Home-card entry initialize equivalent state.
- Navigating away and back does not break clickability.
- Beautify/Transcribe disabled cursor appears only when the action is genuinely unavailable.
- No unrelated client/session/draft is blocked by another workflow’s busy state.
```

## Advisor Verification Checklist

Before approving, check:

```markdown
[ ] Diff targets the actual state gate or route-entry mismatch.
[ ] Fix does not only hide the symptom.
[ ] Home entry and panel/sidebar entry now share equivalent initialization.
[ ] Disabled predicates are scoped correctly.
[ ] Cursor/hover state matches actual clickability.
[ ] First-load behavior is handled.
[ ] Async success/failure/cancel cleanup is not broken.
[ ] Manual repro sequence is documented or automated test exists.
```

## Anti-Patterns

Avoid:

```markdown
- Starting Playwright before inspecting the entry-path difference.
- Reading BUILD.md for a UI state bug unless launch/build behavior is directly implicated.
- Searching the whole project with many broad terms before naming the state gates.
- Treating “click does nothing” as a DOM-only issue.
- Trusting that visible UI means state has hydrated correctly.
- Fixing by globally resetting state on every panel switch.
- Disabling all controls with one global busy boolean.
```

## Key Principle

When one navigation path works and another does not, the bug is usually not the button.

It is usually one of these:

```markdown
- different initialization
- missing route state
- stale selected ID
- async data not hydrated yet
- global busy/loading flag leaking
- disabled predicate applied too broadly
- invisible overlay/pointer-events issue
```

Find the difference between the paths before doing anything expensive.
