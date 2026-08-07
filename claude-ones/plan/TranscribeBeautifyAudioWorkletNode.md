# T4 Execution Plan — Live-Transcription Boundary Reconciliation (AudioWorkletNode gated behind it)

**Created 2026-08-05. Revised 2026-08-05 after owner review. Phase 0A executed 2026-08-06 — see §10.
RULED 2026-08-06 — see §11.**
Owner: Jonathan.
Status: **`[x] — REJECTED` (owner ruling 2026-08-06).** T4 as designed (1 s overlap, timestamp-trim
stitch) is closed. The IT436365 `counselling-51-min` Phase 0A result failed on four independent
grounds — a negation reversal, relocated self-harm/cutting content, a 19 s missed-speech gap, and a
16× repetition loop — any one of which is disqualifying under §5 on its own. Phases 1–6 as scoped
against this configuration do not proceed. Full ruling: §11. Canonical evidence record:
`TranscribeBeautifyBreakthrough.md` §11.12.

> ### 🚨 T4 is CLOSED — REJECTED (ruled 2026-08-06). Read §11 before anything else in this file.
>
> IT436365's Phase 0A run (§10) found four independent disqualifying problems in `counselling-51-min`:
> a positive answer reversed to negative, the self-harm/cutting span relocated during stitching, a 19 s
> missed-speech gap, and a 16× "I'm not" repetition loop. Per §5, any one of these fails the transcript
> gate on its own. The actual text is not reproduced in this file or any tracked file (§6's no-PHI
> rule); it is in the gitignored
> `private-test-debugs\benchmark_results\live-slice-replay-06082026-it436365\` folder. Reopening T4
> requires a genuinely new stitching mechanism (§4.2/§4.3) tested from scratch against §5's full gate
> set — not a continuation of Phase 1 onward against this configuration.

> ### ⚠️ Read this first — scope correction made 2026-08-05
>
> **This document is the execution plan for T4, an existing candidate.** It is *not* a new one.
> [`TranscribeBeautifyBreakthrough.md`](TranscribeBeautifyBreakthrough.md) line 648 already defines
> **"T4 — Live-transcription boundary reconciliation reopening"** with pre-registered speed thresholds
> and transcript kills. §11.11.3 step 5 already points at it.
>
> The first draft of this document invented a parallel candidate with self-authored gates. That was
> wrong in a way that matters: **T4's gates are pre-registered, and this plan may not weaken them.**
> Everything below inherits from §3.1 and T4; where this document adds anything, it adds *operational
> definitions and sequencing*, never a softer threshold.

**Governing documents — this plan is subordinate to all three:**
- Candidate definition and pre-registered gates: [`TranscribeBeautifyBreakthrough.md`](TranscribeBeautifyBreakthrough.md) **T4** (line 648) and **§3.1** (transcript gate)
- The kill this reopens: [`bugs-fixed/056-01082026(NewFindings).md`](../../bugs-fixed/056-01082026(NewFindings).md) §3
- The rejection it must not drift into: [`bugs-fixed/055-31072026(NewFindings).md`](../../bugs-fixed/055-31072026(NewFindings).md) §0C

---

## Current Status (tri-state — update every session; single source of truth)

`[ ]` not started · `[~]` in progress / partial · `[x]` complete
A candidate **rejected after measurement** is marked `[x] — REJECTED: <evidence>` (`CODEX-REVIEW.md`
§"How to use the tri-state boxes") so it is never silently reconsidered.

| Phase | Item | State | Note |
|---|---|---|---|
| **0A** | Minimal instrumentation repair | `[x]` | Done 2026-08-06, both machines run. §4.0A, §10 |
| **0B** | Noise floor — 3 serial decodes × 5 fixtures | `[ ]` | **Not T4 work anymore.** T4 closed at Phase 0A (§11) regardless of what 0B would show. May still run as an independent production-reliability check — see §11 |
| **1** | Full harness parameterisation | `[x]` — **MOOT** | T4 closed at Phase 0A (§11). Would only resume under a new post-T4 candidate |
| **2** | Overlap sweep — 1 s control / 3 s / 5 s | `[x]` — **MOOT** | Same as above; §4.2's mechanism remains a theoretically available new candidate, not a continuation |
| **3** | Bridge-window seam re-decode | `[x]` — **MOOT** | Same as above |
| **4** | Repetition-loop containment | `[x]` — **MOOT** | Same as above; the repetition failure this phase targeted is itself one of the four grounds T4 was rejected on (§11) |
| **5** | Backend feasibility qualification (throughput + thermal + net saving) | `[x]` — **MOOT** | Same as above |
| **6** | `AudioWorkletNode` capture path + in-app requalification | `[x]` — **MOOT / LOCKED** | T4 closed before this ever unlocked. Does not happen under this candidate |

**T4's own precondition — met.** T4 requires *"T2 reliability gate passed; no recorder/worklet UI before
offline survival."* T2 completed 2026-08-02 (`bugs-fixed/059`).

**Queue position — ruled 2026-08-05: queued, not parked.** T4 starts after §11.11.3 step 1 (the free
IT436365 determinism check). Phase 0A/0B may then run **in parallel with** pending MTP practitioner
review, provided they never consume the owner's clinical-review window or delay the MTP app rows.
Phase 1+ is gated on the Phase 0B result. Full ruled sequence: §8.

---

## 1. Why T4 is worth executing now

T7d closed on 2026-08-05, which changed the arithmetic:

| Phase of clock (4) | Share | Surviving lever |
|---|---|---|
| Transcription | **38.7–44.1%** | **T4 — this document, and nothing else** |
| Beautify prefill | 21.2–33.2% | none (T7d concurrent prefill closed, §11.11.6) |
| Hidden reasoning | 12.8–22.8% | MTP (decode); reasoning-off declined by owner |
| Visible output | 9.8–17.1% | MTP (decode) |

Transcription is the largest single block and now the only large block with an unexplored lever.

**The base rate is against it.** Three transcription-side candidates tested, three failed: batched
Whisper (fidelity), live transcription as designed (fidelity), transcript preparation Phase 0 (produced
a *larger* Source). Nothing here should be read as expecting success.

**The economics improve on weaker machines — a structural point worth recording.** Ordinary transcription
costs 2.6–6.25 min per fixture on IT436365 and more on a 15 W ~2-P-core fleet part. Live transcription
removes post-Stop transcription time, so **the weaker the machine, the larger the net saving** — the same
inverse-scaling shape already measured for MTP (§11.11.2). The fleet is where this candidate looks best,
which is the opposite of most levers tested so far.

---

## 2. Closed — do not re-run

- **Batched Whisper** — CLOSED-REJECTED on fidelity. Structural: independent ~30 s chunks with **no
  cross-chunk conditioning**, proven by `batch_size` 1/4/8 being byte-identical. T4's design is the
  opposite mechanism (each slice conditioned on the previous slice's own output) and must never drift
  toward it.
- **Adjacent text-dedup stitching** — rejected by transcript-preparation Phase 0; destroys genuine
  emphatic repetition. **Stitching is timestamp-bounded only. Text comparison may never delete a span.**
- **The 2026-08-01 design as tested** — 60 s slices, ~1 s overlap, timestamp-trim stitch. Killed. A rerun
  of those parameters is not an experiment.
- **Concurrent prefill during Whisper (T7d)** — closed both machines. Its lesson binds: *on a CPU-only
  stack there is no free concurrency.* T4 is exempt **only** because the CPU is genuinely idle during a
  session — Phase 5 tests that exemption rather than assuming it.

---

## 3. Instrumentation defects — found 2026-08-05 by reading the harness

Found by reading `backend/tests-benchmarks/benchmark_live_slice_replay.py`, not by re-running it. They
mean the 2026-08-01 result is directionally sound but its gate arithmetic is weaker than it reads.

### 3.1 §3.1's coverage gate has no operational definition, and the harness's is wrong `[x]` — repaired 2026-08-06

`slice_and_transcribe()` computes `last_end_s / duration_s` — that is **reach**, not coverage. A silent
hole at minute 22 scores 100%. So "coverage passed on all 5 (99.61–100.0%)" is near-meaningless.

**The first proposed repair was also wrong.** Union-of-segment-intervals ÷ full duration treats
legitimate silence as uncovered — with `vad_filter=True`, Whisper is *expected* not to emit segments
across silence, so a perfect transcript would score far below 99% and the gate would fail everything.

**Correct definition — three separate measurements** (this is the operational definition §3.1 was
missing, not a replacement for its 99% threshold):

| Metric | Formula | Denominator | Catches |
|---|---|---|---|
| **Audio-input coverage** | union of audio ranges actually submitted to Whisper ÷ full recording duration | recording duration | slicing bugs — audio never fed to the model at all |
| **Speech coverage** | candidate-covered speech intervals ÷ **reference VAD speech intervals** | *speech*, not silence | the fidelity question §3.1 actually asks |
| **Largest missed speech gap** | longest reference-speech interval absent from candidate, in seconds | — | one big hole hiding behind a good percentage |

Only **audio-input coverage** should approach 100% of recording duration. §3.1's ≥99% applies to
**speech coverage**. Reference VAD intervals come from `get_speech_timestamps`, already imported by the
harness for cut-point selection — cheap to compute.

### 3.2 The repetition metric cannot see the hallucination it was added for `[x]` — repaired 2026-08-06

`count_adjacent_duplicate_chars()` compares **whole adjacent sentences**. The pilot's own hand-found loop
— *"…a comment that I have a comment that I have a comment that I have…"* (28 words) — is
**intra**-sentence and invisible to it. The 5/5 repetition signal is understated.

**Repair:** n-gram detector (any 4-gram repeating ≥3× within a 50-word window), reported per fixture
**and per slice index**, so repetition can be attributed to specific seams.

### 3.3 The noise floor has never been measured `[ ]` — still true; the `--no-frozen-reference` flag (§4.0A) fixes the underlying defect but Phase 0B's 3× repeat itself is unbuilt, see §10.3

`load_or_make_serial_reference()` reads a **frozen single decode** from
`benchmark_results/clock4-baseline-31072026-jp-start/sources_8t/{fixture}.source.txt`. Every comparison
is one non-deterministic stitched run against one frozen reference.

`056` §3 records the consequence without naming it: the pilot found **0** missing spans on
`counselling-31-min`; the full run — identical fixture, identical code, identical VAD/thread/beam
settings — found **1**.

This is a direct violation of §3.2 step 2 (*"establish the within-condition control arm before comparing
anything across conditions"*), a rule added **2026-08-05**, four days *after* the experiment ran. A
sequencing artifact, not negligence — but it must be repaired before a new number is trusted.

⚠️ The frozen `sources_8t` references are **jp-start artifacts**. Phase 0B generates its own.

---

## 4. Phases

### 4.0A Phase 0A — Minimal instrumentation repair `[x]` · **DONE 2026-08-06 — see §10**

Phase 0B costs ~15 full decodes (≈40–90 min of decode on IT436365). **Do not spend them gathering
metrics already known to be defective.** Repair only what 0B reads:

- `[x]` `--no-frozen-reference` — force a fresh serial decode; never read `sources_8t`
- `[x]` Coverage triplet per §3.1 above (audio-input, speech, largest missed speech gap)
- `[x]` N-gram repetition detector per §3.2 above
- `[x]` Missing-span report emits **full surrounding context** (±25 words) for hand classification

Also added, beyond the original spec (needed before a second machine could run this safely): a
required `--machine` label (an output folder must never default to a stale/wrong machine name again —
this repo already has one real incident of exactly that class, §11.8.4 of `TranscribeBeautifyBreakthrough.md`)
and `--out` support so runs route straight into `private-test-debugs`, matching every other
`benchmark_*.py` script's convention. Committed as `3e488bf`/`5cd6910` — **on `ui-improvement-bulk-run`,
not `prompt-improve`; §6's branch rule was not followed for this commit, flagged for the owner to
resolve.**

Deferred to Phase 1: overlap/slice CLI, bridge-window support, throughput telemetry. 0B does no slicing,
so it needs none of them.

**Extend `benchmark_live_slice_replay.py`. Do not hand-roll in `tmp/`** — §11.11.4 records this as a
repeat offence class (two prior ad-hoc harnesses bypassed the evidence contract).

---

### 4.0B Phase 0B — Noise floor `[ ]`

**Question:** how many missing spans ≥5 words does the metric report when *nothing has changed*?

**Method.** Decode each of the 5 fixtures **serially, end to end, 3×**, production settings
(`beam_size=2`, `vad_filter=True`, `cpu_threads=8`, bundled `base`). Diff each pair with the same
`word_diff_report()` used for stitched comparison. **Run on IT436365** — jp-start failed its own
determinism check 2026-08-05; IT436365 produced byte-identical Sources across both T7d arms (`ff0f5c4d…`).

#### Two independent gates — this table is the one a future agent will misread, so it is explicit

> **The noise floor is an attribution tool. It is NEVER a clinical-safety allowance.**

| Gate | Question | Standard | May the noise floor relax it? |
|---|---|---|---|
| **Attribution** | Is stitched behaviour worse than ordinary serial variability? | statistical, vs the measured floor | **Yes — that is its only purpose** |
| **Absolute clinical** | Any omission involving risk, safeguarding, negation, qualification, distress, treatment choice, homework/intervention, medication, dates, or plans? | **§3.1: zero, of any length** | **NO. Never. At any noise level.** |

**Pre-registered outcomes:**

| Result | Meaning | Action |
|---|---|---|
| 0 missing spans, all pairs, all fixtures | Metric is clean | Attribution gate = zero. Proceed to Phase 1. |
| 1–2 spans between identical serial runs | Reference itself is noisy | Record the floor per fixture; attribution gate becomes a band. **Absolute clinical gate stays at zero.** Proceed to Phase 1. |
| Large/variable counts between identical runs | Metric cannot resolve the effect | **Unmeasurable by this method. Stop. Close T4.** |
| **Any pair differs on a clinically material span** | **The status quo already fails §3.1** | **Stop and escalate — see below.** |

**That fourth row is not hypothetical and needs a pre-registered response.** If two ordinary serial
decodes disagree on clinically material content, then *production transcription as shipped today* is less
reliable than assumed. That outcome:
- **does not license T4** — "live is no worse than serial" is not a safety argument if serial is unsafe;
- **opens a separate defect** against current Whisper settings, at higher priority than T4;
- is a genuinely valuable finding and must be recorded as such, not buried in a T4 result table.

**Classification is a human job and must be auditable.** Only the owner can rule a span clinically
material — the same scarce-clinical-time constraint as §11.11.3 step 2. Every classified span is recorded
**with its reasoning** so the ruling is not re-litigated on each subsequent run.

**Exit evidence:** per-fixture noise-floor table (missing spans, inserted spans, word delta, coverage
triplet, repetition counts) across 3 serial repetitions, written into this document.

---

### 4.1 Phase 1 — Full harness parameterisation `[ ]`

- `[ ]` `--overlap-s`, `--slice-target-s` as CLI args (currently constants `OVERLAP_S = 1.0`,
  `SLICE_TARGET_S = 60.0`)
- `[ ]` Bridge-window re-decode support (§4.3)
- `[ ]` **Throughput telemetry** (§4.5) — per-slice wall, queued-audio duration, pending-slice count,
  backlog trajectory, final backlog at Stop
- `[ ]` Emit the Phase 0 noise-floor band alongside every stitched result, so no reader compares against
  zero by reflex

**Exit evidence:** re-run the 2026-08-01 configuration unchanged; confirm the repaired metrics reproduce
that run's *direction* (12 missing spans, 4/5 fixtures). If repaired instrumentation contradicts the
original result, that is itself the finding — record and re-rule.

---

### 4.2 Phase 2 — Overlap sweep `[ ]`

T4's *"materially larger 3–5 second overlap."*

**Mechanism hypothesis, stated so it can be wrong.** [Inferred, unmeasured] Whisper's decoder is weakest
in the first ~1–2 s of a window, where it has least acoustic context. A 1 s overlap is roughly the *same
width* as the damage zone and cannot cover it. 3–5 s should.

**Matrix:** overlap ∈ {1 s control, 3 s, 5 s} × 5 fixtures. Slice target fixed at 60 s — one variable at
a time (`CODEX-REVIEW.md` §"change one variable only").

**Success rule — deliberately not strict monotonicity.** Whisper's segmentation shifts with context
window, so `12 → 3 → 4` is a success, not a refutation. Require:

1. **Clear directional reduction from the 1 s control** — total missing spans across all 5 fixtures fall
   by ≥50%, and no individual fixture worsens by more than the Phase 0 noise floor; **then**
2. the absolute §3.1 gate decides ship/kill.

Do not require every intermediate value to improve.

**Throughput coupling (see §4.5).** 5 s overlap on a 60 s slice is ~8% more decode. It is paid *during*
the session, so it does not affect clock (4) — but it consumes the RTF and re-decode budget, and Phases 2
and 3 draw on the **same** budget. Fidelity cannot be tuned without watching throughput.

---

### 4.3 Phase 3 — Bridge-window seam re-decode `[ ]`

T4's *"neighbour-boundary reconciliation before a boundary is final."* Run if Phase 2 reduces but does
not close the gap.

**Rejected as too weak:** choosing whichever neighbouring slice has more surrounding context. Both
neighbours decoded the disputed speech **near an edge**, so both are inside the damage zone. Picking the
better of two bad decodes does not attack the mechanism.

**Design:**

```
neighbouring slices disagree on the overlap region
        ↓
extract a 15–30 s bridge window centred on the seam
        ↓
decode the bridge separately
        ↓
condition it on the already-stable earlier transcript only
        ↓
use its timestamp-bounded result for that seam
```

Only uncertain boundaries are re-decoded, so cost scales with disagreement rather than with duration.

**The trap this must not fall into.** Agreement-checking compares text, and text-comparison stitching is
what transcript-preparation Phase 0 rejected. The discipline: text agreement may only decide **which
decode of a given timestamp range to keep**. It may never delete a span present in only one decode.
**Over-inclusion is recoverable by a practitioner reading the Source; silent loss is not.**

**Budget:** T4 caps re-decode/reconciliation at **≤20% of audio**. Bridge windows count against it, and
so does Phase 2's overlap. Exceeding the cap fails T4 regardless of fidelity.

**Gate:** §3.1 in full, plus no increase in inserted spans over Phase 2's best arm.

---

### 4.4 Phase 4 — Repetition-loop containment `[ ]`

**Independent second gate; failed 5/5 on 2026-08-01.** Every fixture showed positive word delta (+4.35%
to +6.11%) and higher adjacent-duplicate counts than serial (5→75, 83→142, 77→116, 267→326, 46→169).
Shorter per-slice context raises repetition-loop hallucination.

A fidelity pass on Phases 2–3 does **not** clear this. Fabricated repeated text in a clinical Source
reaches Beautify as evidence. §3.1: *"zero whole duplicated exchange and no new generalising
repetition-loop mechanism."*

- `[ ]` Quantify with the §3.2 n-gram detector; attribute to slice indices
- `[ ]` Test whether `TAIL_WORDS_FOR_PROMPT = 200` drives it — a too-long conditioning tail can seed the
  loop it is meant to prevent
- `[ ]` Decide detect-and-flag vs suppress. **Default to flag** — suppression is text-based deletion,
  see §4.3's trap

**Gate:** repetition metric within the Phase 0 noise-floor band, all 5 fixtures.

---

### 4.5 Phase 5 — Backend feasibility qualification `[ ]`

> **This is a feasibility qualification, not the final product qualification.** Backend replay cannot
> measure renderer→backend transfer, PCM conversion/resampling, IPC queue behaviour, packaged-app module
> loading, renderer lifecycle, mic disconnection, or **recording and transcribing simultaneously**.
> Phase 6 repeats it in the real Electron path.

#### 5a. Throughput — T4's pre-registered thresholds `[ ]`

- `[ ]` Full live replay **RTF < 1.0** on the target machine
- `[ ]` Projected **p90 Stop→final-Source tail ≤ 60 s**
- `[ ]` **≤20% of audio** requiring final re-decode/reconciliation (shared with Phase 3)

**Average RTF < 1.0 is not sufficient, and this is the systems point.** A run can average below 1.0 while
temporarily backlogging, producing a bad Stop tail. Record explicitly:

- maximum queued audio duration
- maximum number of pending slices
- per-slice processing wall (distribution, not mean)
- whether backlog **grows** across the session
- final backlog at Stop

#### 5b. Net saving — the economic gate `[ ]` · **thresholds pre-registered by owner ruling 2026-08-05**

**A 10%-Beautify-slowdown threshold is a diagnostic, not an economic decision.** If live transcription
removes 3–4 minutes of post-Stop transcription and costs 40–60 s of heated Beautify, that is a large win
being killed by the wrong number. Beautify slowdown is recorded as **diagnostic context**, never as a
kill on its own.

**Formula — every term is measured on the post-Stop side of the clock:**

```
Net saving = ordinary post-Stop transcription wall
           − final live-transcription backlog/tail
           − post-Stop reconciliation wall
           − additional heated-Beautify wall
```

⚠️ **Do not subtract during-session overlap or bridge-window processing.** It happens *before* Stop, so
it costs the counsellor nothing directly. Its cost is already represented — twice over, and that is
deliberate:

- **If it kept up**, it is genuinely free, and 5a's RTF/backlog telemetry proves it kept up.
- **If it did not keep up**, the shortfall appears as `final live-transcription backlog/tail` in the
  formula above. That is the *only* correct place it enters, and it must not also be subtracted as
  during-session cost — that would double-count.
- Its **non-time** costs (thermal, responsiveness, fan noise in-room) are gated separately by 5c.

**Pre-registered thresholds — an absolute AND a relative bar, both required:**

| Machine | Median net saving | Every fixture | p90 |
|---|---|---|---|
| **IT436365** (i5-1135G7/16 GB) | **≥90 s AND ≥15%** | **≥60 s** | no regression vs the ordinary post-Stop baseline's Stop→durably-saved-draft p90 |
| **135U/16 GB** (fleet-representative qualification) | **≥120 s or ≥15%, whichever is greater** | — | no regression |

**Why both bars:**
- The **relative** bar (≥15%) stops a large absolute number looking impressive merely because the session
  was exceptionally long.
- The **absolute** bar (≥90–120 s) ensures the implementation complexity, sustained CPU use, testing
  burden, and new failure surface buy something the counsellor genuinely feels. A 35–45 s result is
  statistically interesting and does **not** justify live audio transport, reconciliation, lifecycle
  handling, and a permanently-running second inference path. **T4 exists to be a minutes-scale
  breakthrough, not another small optimisation.**
- The **every-fixture ≥60 s** floor stops a good aggregate hiding a session where the feature adds all
  the complexity and almost none of the benefit.

#### 5c. Thermal and acoustic behaviour `[ ]`

- `[ ]` No unacceptable fan, responsiveness, or thermal-throttling behaviour
- `[ ]` **Fan noise during a session with a client present is a distinct product failure** — it is not
  the same as fan noise during post-session processing, and net-saving arithmetic does not excuse it.
  A counselling room is quiet; a 15 W part decoding for 45 minutes may be audible.

**Method:** on IT436365 (and a 135U/16 GB if ever available), full-session replay at realistic pace, then
immediately Beautify the resulting Source; compare against a cold-machine control, order counterbalanced.

---

### 4.6 Phase 6 — `AudioWorkletNode` capture + in-app requalification `[ ]` · **LOCKED**

Unlocks only when 0–5 are `[x]` and passing. T4's own gate: *"no recorder/worklet UI before offline
survival."*

**Verified facts (2026-08-05):**

- **The graph already exists.** `SessionsPage.tsx:2969-2983` / `MeetingDashboard.tsx:501-514` build an
  `AudioContext`, `createMediaStreamSource` for mic, a `GainNode` at 1.5 for system loopback, merged into
  `createMediaStreamDestination`. A worklet is a **tap off the existing `dest`**, not a rewrite.
- **There is no chunking today.** Both recorders call bare `mediaRecorder.start()` with **no timeslice**
  (`SessionsPage.tsx:3070`, `MeetingDashboard.tsx:573`); `ondataavailable` fires once, at stop. Any claim
  that PRIVATE already streams chunks is wrong.

Work items:

- `[ ]` **Dual path, not replacement.** Keep `MediaRecorder`/Opus for the retained `audio_queue` copy
  (encrypted, max-10 cap, excluded from backups). Add the PCM tap *alongside*. Raw PCM is ~10–20× the
  bytes and must never become the stored artifact.
- `[ ]` **Buffer before transport.** Accumulate ~250–500 ms in the processor, post with a transfer list.
  Posting every 128-sample render quantum through IPC is measurably worse than today.
- `[ ]` **Secure context + module path.** `audioWorklet.addModule()` needs a secure context and a real
  URL. Dev (`localhost`) is fine; the packaged renderer scheme must be verified. Vite must emit the
  processor as its own asset — `new URL('./x.js', import.meta.url)`, not a normal import.
- `[ ]` **Worklet constraints.** No DOM, `window`, Node, IPC, or allocation-heavy work in `process()`.
  Bridge is `MessagePort` → renderer/worker → backend.
- `[ ]` **Codec-loss check.** Today's path is lossy Opus before Whisper sees it; PCM removes that
  round-trip. [Inferred] This is a *quality* argument and probably does **not** fix seam loss — seams are
  a decoder-context problem, not an audio-quality one. It may never be used to justify skipping 0–5.
- `[ ]` **Repeat 5a/5b/5c in the real Electron path**, now including simultaneous recording (Opus encode
  + PCM tap + disk writes) — sustained load that replay never applies.
- `[ ]` **Four Fates walk** (`fable-user-reality`): navigate away mid-session; mic disconnects at minute
  30; force-kill at minute 30; 3-hour session.

---

## 5. Gates — inherited, not invented

**Transcript (§3.1, verbatim standard — one critical failure stops the candidate even if timing is
exceptional):** exact timeline coverage recorded, ≥99% (per §3.1's definition above); zero contiguous
missing span ≥5 words across the frozen five-fixture set; **zero clinically material omission of any
length** involving risk, safeguarding, negation, qualification, distress, treatment choice,
homework/intervention, medication, dates, or plans; zero whole duplicated exchange and no new generalising
repetition-loop mechanism; no loss of self-correction, uncertainty, role-play/hypothetical boundaries, or
speaker ambiguity; **aggregate word-count parity alone never passes.**

**Throughput (T4):** RTF < 1.0; p90 Stop→final-Source ≤ 60 s; ≤20% of audio re-decoded.

**Economic (§4.5b):** net Stop→draft improvement ≥ owner-set threshold.

**Product (§4.5c):** no unacceptable thermal, responsiveness, or acoustic behaviour in-room.

**Content class over percentage.** *The percentage is not the safety criterion, the content class is.*
One span of the `counselling-38-min` class — *"You said something so important just now"* immediately
before naming why a treatment modality was preferred — fails on its own, at any percentage, at any noise
floor.

Failing any gate closes T4 again as `[x] — REJECTED: <evidence>`. Gates are not relaxed after seeing
the number.

---

## 6. Inherited process rules — not optional

- **Machine separation.** jp-start is comparison-only. Never average jp-start and IT436365 numbers.
- **Determinism-sensitive arms run on IT436365** (§11.11.6).
- **Within-condition control arm on every A/B** (§3.2 step 2). Phase 0B *is* this plan's control arm.
- **Extend a contract-validated harness; never hand-roll in `tmp/`** (§11.11.4).
- **Fixtures are read-only evidence.** `private_storage/sessions/Unsorted/counselling-*.mp3` — preserve
  exact bytes between conditions; never upload; never re-transcribe a frozen Source a comparison depends on.
- **No PHI in tracked files.** Missing-span contexts stay in the ignored `benchmark_results/` tree.

---

## 7. What closes T4 permanently

- Phase 0B returns "unmeasurable" → method cannot resolve the effect. Close.
- Phase 2 shows no clear directional reduction from the 1 s control → the seam hypothesis is wrong; if
  Phase 3 also fails, close.
- Re-decode budget cannot be held ≤20% while meeting §3.1 → close.
- RTF ≥1.0 or backlog grows across a session → close.
- Net saving is negative or trivial → close regardless of fidelity.
- Any phase that can only pass by deleting text on a text-comparison basis → close.

---

## 8. Sequencing — **owner ruling 2026-08-05: T4 is queued, not parked**

T4 is the next independent speed candidate and is **explicitly queued**. It must not interrupt the free
IT436365 MTP determinism check, and must not delay already-prepared MTP quality work.

**The ruled sequence — T4 and MTP interleave rather than serialise:**

| # | Work | Owner ruling |
|---|---|---|
| 1 | IT436365 MTP determinism check | **First.** Free, already-collected data, decides the MTP critical path. T4 does not touch this. |
| 2 | **T4 Phase 0A** | Begin after step 1. Instrumentation only — no model matrix, no decode time. |
| 3 | **T4 Phase 0B** | May run **while MTP practitioner review is pending** — provided it does not consume the owner's clinical-review window. |
| 4 | MTP quality ruling + the two counterbalanced app rows | Proceeds on its own schedule; T4 must not displace it. |
| 5 | **T4 Phase 1+** | Only if the Phase 0B result permits. |

**Why interleave rather than serialise.** These are largely independent workflows: MTP is a *Gemma
output-quality and application-path* question; T4 Phase 0A/0B is a *Whisper determinism and
measurement-validity* question. Machine time and owner time are the only shared resources, and 0A needs
neither.

**T4 must never displace** the free MTP determinism reading, an available practitioner-review session, or
the two already-planned counterbalanced MTP app rows.

**Phase 0B's value is not confined to T4.** It may expose a defect in the **currently shipped** serial
transcription path (§4.0B, fourth outcome row). That is an independent reason not to leave it parked
indefinitely.

**Two efficiencies:**
- Phase 0B and step 1 answer the *same underlying question* — does this stack reproduce itself? — on two
  different components (Whisper vs llama-server). If step 1 returns non-deterministic on IT436365, expect
  a non-zero floor and define the attribution gate as a band from the outset.
- Phase 5 needs fleet-class hardware — the same blocker as the outstanding 135U/16 GB qualification, and
  now also the source of 5b's ≥120 s threshold. If that machine becomes available, schedule both as one
  visit.

---

## 9. Correction to `TranscribeBeautifyBreakthrough.md` `[x]` — applied 2026-08-05

§11.11.6 previously ended: *"Treat the MTP quality gate as the critical path; there is no second speed
candidate waiting behind it."* T4 sat in §11.11.3 **step 5** alongside §10.4 as "retaining existing
independent gates" — which reads as parked, not queued. That phrasing is why two consecutive sessions
(and the first draft of this document) treated live transcription as closed.

`[x]` §11.11.6's closing paragraph replaced with the owner's ruled text (2026-08-05), and §11.11.3 step 5
split so T4 is a numbered, queued item rather than a parenthetical. Both now point here.

---

## 10. Phase 0A results — both machines report (2026-08-06)

**Full evidence (per-fixture tables, both machines, all numbers) lives in exactly one place:
`TranscribeBeautifyBreakthrough.md` §11.12. Do not duplicate the tables here** — this repo has
already had two separate incidents of a duplicated fact drifting between documents (§11.7's
superseded list, §11.11.6's stale closing line), and a two-file evidence set for the same run is the
same failure mode waiting to happen again. This section stays short on purpose.

**Headline:** both machines found lost content and elevated repetition on every fixture tested.
IT436365 (decision-grade, §11.2) is worse than jp-start (comparison-only): 10 missing spans ≥5 words
against a gate of zero, 2 of 5 fixtures fail the ≥99% speech-coverage gate, and — the item that
matters most — **one span in `counselling-51-min` describes self-harm/cutting behaviour**, which fails
§5's gate "at any percentage, at any noise floor," independent of Phase 0B or anything else measured.
Not reproduced here (§6, no PHI in tracked files); the source data is in
`private-test-debugs\benchmark_results\live-slice-replay-06082026-it436365\`.

**Consequence for the phase table above:** Phase 0B (§4.0B) is now lower priority — if the owner
rules the self-harm span clinically material, T4 closes as `[x] — REJECTED` regardless of what Phase
0B would show. Running it later would mainly check whether the defect is specific to live-stitching
or already present in shipped serial transcription (§4.0B's fourth outcome row — a separate, likely
higher-priority defect either way, not a T4 question).

**Next action:** owner classification of the flagged spans. Full list, priority order, and exact file
paths: `TranscribeBeautifyBreakthrough.md` §11.13, step 1. Human step; no model executes it.

---

## 11. Owner ruling — T4 REJECTED (2026-08-06)

**Ruling:** `[x] — REJECTED`. Owner review of the IT436365 `counselling-51-min` Phase 0A result (§10)
found four independent transcript-gate failures in a single fixture, any one of which is disqualifying
on its own under §5:

1. **Negation reversal** — a positive answer rendered as its negative ("it did help" → "it didn't
   really help"), plus other positive→negative flips. Fails §5's named `negation` content class
   directly.
2. **Relocated self-harm/cutting content** — the span already flagged in §10 above, moved out of its
   original position during stitching. Fails §5 "at any percentage, at any noise floor."
3. **Completeness** — a missed speech gap of up to 19 seconds, alongside 335 additional words versus
   the serial baseline for this fixture.
4. **Repetition-loop containment (§4.4's gate)** — one chunk repeats "I'm not" approximately 16 times,
   the same failure class §4.4 already expected from the 2026-08-01 run (5/5 fixtures).

**Why Phase 0B was not required first.** §4.0B's exit table already anticipated that an
absolute-clinical-gate failure stops the process regardless of noise floor. A negation reversal and a
relocated risk-content span are not statistical questions a 3×-serial noise-floor run could resolve or
excuse — §5's gate applies "independent of the noise floor," and this ruling exercises that clause
directly rather than waiting on Phase 0B.

**Scope of the closure.** T4 as designed — 1 s overlap, timestamp-trim stitch (§4.0A/Phase 0A's
configuration) — is closed. Phases 1–6 built on that configuration do not proceed (tri-state table
above updated to `MOOT`). The overlap-sweep and bridge-window mechanisms (§4.2/§4.3) remain
theoretically available as a **new** candidate — they were designed precisely to test whether more
context around cut points fixes this class of error — but reopening means testing that new mechanism
from scratch against §5's full gate set, not resuming Phase 1 against the rejected configuration.

**What remains open, and is not T4 work:** whether the same defect classes already exist in currently
*shipped* serial transcription (§4.0B's fourth outcome row) is an independent, potentially
higher-priority production-reliability question. It may still be worth running Phase 0B's 3×-serial
method for that purpose alone — but it neither reopens nor is required by this ruling.

Canonical evidence record (do not duplicate tables — §6 of this document already asks for that
discipline): `TranscribeBeautifyBreakthrough.md` §11.12's "Owner ruling" block.
