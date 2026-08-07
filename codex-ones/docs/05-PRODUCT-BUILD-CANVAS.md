# Product build canvas: convert a useful instinct into a supportable product

Complete this before choosing a model or framework. Short, concrete answers are better than polished paragraphs.

## 1. Picture

Describe one person in one moment:

- Who are they?
- What has just happened?
- What are they trying to produce or decide?
- What do they do today?
- What pressure are they under?
- What would success look like ten minutes later?

Weak: “Analysts need AI insights.”

Strong: “At 9:10 Monday, an intake analyst has two reports with different application totals and a 10:00 leadership briefing. They need to identify the definition/freshness difference, not receive a third unexplained number.”

## 2. Wedge

Name the smallest recurring job worth solving end to end.

Use this admission test:

- Does it occur often enough to matter?
- Is the pain observable rather than hypothetical?
- Can the first version avoid a high-risk decision?
- Can the user verify the output from evidence?
- Would five real users choose it over their current workaround?

Write explicit non-goals. A boundary creates trust and makes evaluation possible.

## 3. Behaviour ledger

For each critical situation, record:

| Situation | Observable current behaviour | Product obligation | Falsifiable check |
|---|---|---|---|
| What triggers the work? | What the person actually does | What the product must support | How you know it works |

Prefer recent observed behaviour over remembered domain intuition. Domain expertise generates hypotheses; fresh users and operational evidence test them.

## 4. Evidence and decision ledger

List:

- measured facts and owners;
- assumptions;
- transformations;
- unresolved questions;
- recommendations;
- decisions, decision makers, dates, and expiry/review dates.

Do not let a conversation be the only place a decision exists.

## 5. Data and decision boundaries

Answer:

- What is the minimum data needed?
- Which fields can enter model context?
- Which facts remain deterministic?
- Who can interpret, recommend, approve, and act?
- What must the system refuse?
- What becomes an exception rather than a guess?

If the product cannot work without broad raw access, re-examine the wedge and build a purpose-specific view.

## 6. State under real life

Test every important state through the Four Fates:

- **Wander** — user navigates away and returns.
- **Parallel** — user starts another task while this runs.
- **Switch** — user changes record, project, tab, or device.
- **Vanish** — browser, network, worker, or process disappears.

For each transition choose deliberately:

- **Allow** it because the state is safe and durable.
- **Absorb** it without disrupting the work.
- **Guard** with a warning or confirmation.
- **Disable** only when no safer design exists.

Persistent work should outlive the screen that started it.

## 7. Capability map

Inventory every capability:

| Capability | Read/write | Identity | Data class | Side effect | Approval | Timeout/retry | Audit |
|---|---|---|---|---|---|---|---|

One chokepoint should own each cross-cutting concern: authorization, filesystem paths, database writes, audit events, model configuration, and external calls.

## 8. Architecture hypothesis

Choose the lowest level from the architecture ladder. Write why the next simpler level fails a named requirement. If you cannot, use the simpler level.

## 9. User-facing system

Design defaults, empty states, progress, failure, recovery, and first run before adding delight.

Use plain professional vocabulary. Name features by the benefit or job, not by the underlying AI technique. Show:

- what is happening;
- what source and freshness apply;
- what the user can safely do next;
- what is provisional or blocked;
- whether leaving the page is safe;
- where the reviewed result will live.

A committed visual system is useful when it strengthens hierarchy and trust. Avoid generic “AI glow,” excessive glass, decorative metrics, or marketing claims that outrun the product. Restrained motion and a calm interface are often more credible for serious work.

## 10. Pilot and kill criteria

Define before launch:

- eligible users and use cases;
- excluded users/data/actions;
- success measures;
- serious-error thresholds;
- evaluation set;
- training and support owner;
- rollback/kill mechanism;
- end date and review meeting;
- conditions that stop the pilot.

A kill criterion is not pessimism. It prevents a weak experiment from becoming permanent infrastructure by inertia.

## 11. Production journal

After each release, record:

- what changed;
- evidence and assumptions;
- tests and drills run;
- known gaps;
- real user behaviour observed;
- incidents and near misses;
- cost and latency;
- decisions and owners;
- next review date.

Checklists become scripts where possible. Repeated manual verification is a candidate for a test, not a tradition.

