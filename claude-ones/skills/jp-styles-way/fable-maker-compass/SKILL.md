---
name: fable-maker-compass
description: Activate explicitly on "fable maker compass" / "compass check" / "does this serve the wedge". Also fits, unprompted, when deciding whether a feature deserves to exist, when scope is growing mid-build, when pricing/positioning comes up, or when a plan has many parallel workstreams and needs a "what actually matters" cut. Encodes big-picture-first discipline: the one-sentence product truth (the wedge), the calm-conviction stance ("if you don't use it, you're at a loss - and I don't mind"), feature admission tests, and kill criteria so conviction never hardens into stubbornness.
---

# Fable Maker Compass

## Purpose

The other two Fable skills answer *how users behave* and *how to design for it*. This
one answers the question that comes first and gets skipped most: **does this deserve to
be built at all, and does it strengthen the one reason this product wins?**

It encodes a stance the maker described exactly right:

> "If you don't use it, you are at a loss. I don't mind if you don't use it — I know
> the benefits clearly."

That is not arrogance. It is the position you *earn* by knowing precisely what your
product does, for whom, at what price, against what alternative — so precisely that a
non-buyer is making a legible mistake rather than expressing a mystery you must chase.
A maker without this clarity chases every objection with a feature; a maker with it
ships a coherent product and lets the wrong customers walk.

## Activation

Explicit triggers:
- "fable maker compass" / "compass check" / "does this serve the wedge"

Self-activate, without being asked, when:
- a new feature is proposed (by the user, a pilot, or your own brainstorming)
- scope grows mid-build ("while we're here, we could also...")
- pricing, positioning, or competitor comparison comes up
- a plan has 5+ parallel workstreams and needs a ruthless ordering
- the user asks "should I build X or Y first"

## The Wedge

Every product that survives has ONE sentence that explains why a rational buyer picks
it over the alternative. For this app, today:

> **Fully offline clinical notes with local AI — the data never leaves the laptop —
> at $20/month, where the cloud alternative (Heidi ~$120/month) requires trusting
> client PHI to someone else's server.**

Three components, all required:
- **The moat** (what's structurally hard to copy): offline + local AI + privacy posture
- **The price wedge** (the number a buyer can defend to their manager): 20 vs 120
- **The named alternative** (what they'd otherwise do): Heidi/Cliniko, or Word + memory

Rules for the wedge:
- It is written down, dated, and updated deliberately — never drifted.
- Every feature, every piece of UI copy, and every pricing decision is tested against
  it. The Network Transparency panel serves the wedge; a prettier chart theme doesn't.
- **Price on the wedge, not on cost or on fear.** $20 against $120 is a story a buyer
  tells their practice manager in one sentence. Pricing at $8 "to be safe" would delete
  the story and signal a toy. (Memory already records this: "price high not $15.")

## Big Picture First

The maker's stated method — *"making the correct big picture of what you want, then
building"* — formalized:

1. **The picture is a person in a moment**, not an architecture diagram: *a counsellor,
   end of day, four sessions behind on notes, on a mediocre laptop, in an institution
   that would never approve a cloud tool.* Every subsystem in this codebase is legible
   from that one image — offline AI, batch beautify, drafts, backups, activity log.
2. **Features are admitted into the picture; the picture is not stretched to fit
   features.** When something doesn't fit (a standalone meetings product vs. Teams
   Copilot — decided 2026-06-12), it is repositioned or cut, even after it's built.
3. **The picture has a boundary you can recite**: what this product will NOT do
   (no cloud, no PHI leaves the machine, no "AI" branding in the UI). The boundary is
   as load-bearing as the features — it's what the buyer is buying.

## The Feature Admission Test

Before any new feature enters a plan, answer in writing:

```markdown
Feature: [name]
1. WEDGE: Does it strengthen the moat, the price story, or the named-alternative
   contrast? Which one, in one sentence? (If none → it's decoration; park it.)
2. MOMENT: Which behavior fact / user moment does it serve? (cite the ledger —
   see fable-domain-lens. "A pilot asked" is a moment; "it would be cool" is not.)
3. COST OF COHERENCE: What does it complicate — settings surface, support burden,
   the privacy story, the Four Fates matrix (see fable-user-reality)?
4. THE FIVE-CUSTOMER TEST: With only 5 paying customers, would this still be the
   best use of the week it costs? (Validation > features — memory, 2026-06-12.)
5. KILL CRITERIA: What observation, by when, would prove this feature failed and
   should be removed? (A feature admitted without kill criteria can never be
   removed, only accumulated.)
```

A feature that passes 1, 2, and 4 gets built. A feature that fails 1 but passes 2 is a
*candidate for a different product* — write it to the backlog with that label, don't
let it dilute this one.

## Conviction Without Stubbornness

"I don't mind if you don't use it" is only healthy while it stays falsifiable:

- **Conviction** = holding price and boundary steady when ONE prospect objects,
  because the wedge math is written down and still true.
- **Stubbornness** = holding them steady when a *pattern* of the RIGHT buyers (the
  person in your picture) bounces off the same point. Three private-practice
  counsellors independently rejecting the same thing is data, not noise.
- The dividing line is the ledger: objections get recorded with who said them and
  whether the objector matches the picture. Objections from outside the picture
  (an enterprise IT department wanting SSO, when the product targets solo
  practitioners) are priced at zero — that's what "I don't mind" means.

Corollary for spend: money and weeks go to what the *buyer of the wedge* needs to say
yes — code signing, the restore drill, the transparency panel, a trial — before they
go to features the existing user would enjoy.

## Ordering Many Workstreams

When a plan has more items than the next month can hold, sort by exactly one key:
**distance from a stranger paying.** Everything is either on the payment path
(signing, installer smoke test, verify contract, pilot outreach) or it isn't. Ties
broken by risk-of-embarrassment (a restore drill that's never been run is a trust
bomb, not a task). This ordering already exists in memory ("tag → restore drill →
signing → five counsellors → next feature") — the skill is *re-deriving and obeying it
every time scope tempts you sideways*.

## Verification Checklist

```markdown
[ ] The wedge sentence exists in writing, is dated, and was consulted (not assumed).
[ ] Every feature in the plan has a written admission test; failed features were
    parked with a label, not smuggled in.
[ ] Every admitted feature has kill criteria.
[ ] Price was tested against the wedge story, not against fear.
[ ] Objections were logged with source and picture-match; conviction was checked
    against the pattern, not the loudest voice.
[ ] The plan is ordered by distance-from-a-stranger-paying, and the ordering was
    stated, not implied.
```

## Anti-Patterns

```markdown
- Chasing a non-buyer's objection with a feature instead of checking picture-match.
- Pricing low "to be safe" — deleting the one-sentence story the buyer needs.
- Admitting a feature because it's already half-built ("sunk cost admission").
- A backlog where product-ideas and payment-path blockers sit in the same list unranked.
- Stretching the picture to justify a feature you're excited about.
- Conviction with no ledger behind it — that's just mood.
- Building for the 100th customer's edge case before the 1st customer exists.
```

## Key Principle

The compass is one image (the person in the moment), one sentence (the wedge), and one
sort key (distance from a stranger paying). Everything else — features, pricing,
objections, scope — is tested against those three and either admitted, parked, or
priced at zero. Calm conviction is the *output* of that discipline, not a personality
trait: you can say "if you don't use it, that's your loss" only because you can show
the working.

Sibling skills: `fable-domain-lens` (where the picture's facts come from),
`fable-user-reality` (how the admitted features must behave), `fable-mode` (auditing
the result).
