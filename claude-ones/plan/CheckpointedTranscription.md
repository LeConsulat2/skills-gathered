# Checkpointed Canonical Transcription — live/checkpointed ASR feasibility (item 9)

## ▶ CURRENT STATUS — single source of truth (overwritten in place, never appended)

**Last updated: 2026-08-07 (later same day). Stage 0 + Stage 1 COMPLETE. Stage 2 harness BUILT,
self-tested, and run twice more on jp-start at the real ~10 s granularity (production config +
temp-zero), on top of the earlier coarse-granularity smoke test. VERDICT: mechanically solid
(VAD finalization and checkpoint round-trip proven correct in all three runs), but NOT
byte-identical — a real, root-caused, structural mechanism (Whisper's global feature-normalization
max-clip), not an implementation bug. Under production config the gap shrinks a lot (~1.2–2.3%
word delta vs a previously-seen ceiling of ~1.10%) but is unconfirmed as noise-vs-signal on n=1.
The speed signal is genuinely encouraging: per-tick processing ran far faster than the simulated
10 s arrival cadence, and the "tail after last audio arrival" was ~5 s both times — suggestive
that a real live implementation could keep up in real time, which is the necessary precondition
for Stage 3 to be worth doing. Full numbers: `benchmark-reports/JP-START-i7-CHECKPOINTER-Stage2-31min-20260807.md`.
NEXT (not scheduled): repeat production-config Stage 2 runs (for variance) and a second fixture,
before any owner ruling on proceeding to Stage 3 / AudioWorklet work. **Exact commands for this
are in the "▶ NEXT TEST HANDOVER" block immediately below.**

### ▶ NEXT TEST HANDOVER — exact commands, copy-paste ready

Whoever (or whichever agent) picks this up next does not need to re-derive anything above. Run
these from `backend/`, python is always `env\Scripts\python.exe`. **A same-day rerun without
`--label` now refuses instead of silently overwriting today's evidence** (guard added
2026-08-07, closing a real gap found while writing this handover) — the labels below are chosen
to be safe and self-documenting, keep that habit for anything added later.

**Revised 2026-08-07 (later same day): jumping straight to the multi-fixture pass instead of the
originally-planned "one more fixture" step.** Owner is willing to bring additional 40-50 min
recordings too. Combining variance-check and generalization-check into one run is strictly more
efficient than three separate rounds — each production-config run already needs to decode the
fixture 4 times (2 serial reps + redriven + incremental), so running all 5 `DEFAULT_FIXTURES` at
once naturally gives a 2nd/3rd independent production-config data point for `counselling-31-min`
*and* first reads on the other four, in one pass.

**1. Multi-fixture production-config sweep (the priority run):**
```
env\Scripts\python.exe -u tests-benchmarks\benchmark_checkpointed_whisper.py --machine jp-start --out "C:\Users\wooin\Documents\private-test-debugs\benchmark_results" --mode checkpointed --serial-reps 2 --label multifixture
```
No `--fixture` flag = all 5 of `DEFAULT_FIXTURES` (`counselling-31-min`/`-38-min`/`-45-min`/
`-49-min`/`-51-min`), ~214 minutes of audio total. **Budget ~1–1.5 hours** (Run 1 today processed
the 31-min fixture with `--serial-reps 2` in ~10 minutes total; the incremental arm's per-tick
VAD-rescan overhead scales roughly with fixture duration, so scale that up by each fixture's
length — this is exactly the kind of long, no-judgment-needed run to hand to a background
Sonnet/Haiku subagent to babysit, same pattern as the 2026-08-07 session used). Writes ONE
combined `RESULT.json` covering all 5 fixtures in one output folder.

Read, per fixture: does `incremental vs serial1/serial2/redriven` land in the same -1% to -2.5%
neighborhood seen on `counselling-31-min` today, or does any fixture blow far past it? A
consistent small-percent gap across all 5 is a very different, more reassuring finding than one
fixture being fine and another spiking — write both possibilities up honestly, don't average
them into one number.

**2. Optional, only if the owner brings new 40-50 min recordings not already in
`DEFAULT_FIXTURES`:** drop the `.mp3` file(s) into
`private_storage/sessions/Unsorted/` (read-only fixture convention — do not touch the existing
five), then add `--fixture <basename-without-extension>` (repeatable) to the command above, e.g.
`--fixture counselling-31-min --fixture new-recording-name`. This is genuinely additive evidence
(reduces the risk that all 5 conclusions share some quirk of these specific recordings) but is
not required to unblock the owner-ruling point below — the existing 5 already span 31–51 minutes.

**3. Deferred, lower priority: temp-zero-at-real-granularity on a fixture other than
`counselling-31-min`** (confirms the global-max-clip mechanism generalizes rather than being
specific to this one recording's loudness profile) — only worth doing if run 1's production-config
numbers raise a specific question a temp-zero read would answer, not as a routine step:
```
env\Scripts\python.exe -u tests-benchmarks\benchmark_checkpointed_whisper.py --machine jp-start --out "C:\Users\wooin\Documents\private-test-debugs\benchmark_results" --mode checkpointed --fixture counselling-45-min --serial-reps 1 --temperature-zero-only --label stage2-fixture2-temp0
```

**After the multi-fixture run:** write a NEW dated report file,
`benchmark-reports/JP-START-i7-CHECKPOINTER-Stage2-multifixture-<DDMMYYYY>.md` — **do not edit
`benchmark-reports/JP-START-i7-CHECKPOINTER-Stage2-31min-20260807.md` in place**, that file is a
frozen single-fixture snapshot now (same "don't merge across dated runs" convention the IT436365
reports already use). Cross-link the two from each other. Then update this doc's CURRENT STATUS
block. That combination is the owner-ruling point, not a further-testing point — do not silently
proceed to Stage 3 / AudioWorklet design without that ruling, per the plan's own gating rule.

### 🚨 HEADLINE FINDING — shipped serial transcription is NOT deterministic (jp-start, n=1 fixture)

Three back-to-back serial decodes of the **same** audio with the **currently shipped**
configuration produced **three different transcripts**:

| Run | wall | segments | sha256 (16) | temperatures used |
|---|---|---|---|---|
| serial 1 | 82.31 s | 285 | `ea49fb14f4751e1a` | 0.0, 0.6 |
| serial 2 | 85.06 s | 316 | `f3200b28ebdd498f` | 0.0, 0.6 |
| serial 3 | 90.09 s | 315 | `00b0e9fa34df2bc2` | 0.0, 0.8 |

Pairwise (`counselling-31-min`, 1901 s, en): 1↔2 −0.93% words, **1 missing ≥5-word span**,
9 replaced; 1↔3 −1.10%, **1 missing**, 10 replaced; 2↔3 −0.17%, 0 missing, 2 replaced.
**Zero n-gram repetition incidents in any run.**

**Why (mechanism, from source):** the default temperature ladder
`[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]` is live in production. When a window trips the
compression-ratio or log-prob threshold, `generate_with_fallback` retries at temperature > 0,
which switches from beam search to **sampling** (`sampling_temperature`, `beam_size=1`).
Sampling draws from ctranslate2's RNG, so the *stream position* differs per run. A different
sample changes that window's tokens, which changes (a) `all_tokens` conditioning for every
later window and (b) where `seek` lands — so a single divergence **cascades**. That is the
segment-count spread (285/316/315), not a cosmetic wording difference.

**Blast radius measured (from the re-driven arm's `window_trace`, 2026-08-07):** of its **68
windows, exactly ONE (1.5%) fell back to sampling** — temperature 0.6, at `seek` 67700 (≈40%
of the way through the VAD-concatenated audio). The other 67 ran at temperature 0.0. So a
**single stochastic window is enough to shift ~1% of the whole transcript and ~30 segment
boundaries**, because its sampled tokens re-condition every later window's prompt *and* move
where `seek` lands. Serial runs 1–3 show the same shape (`temps` sets `{0,0.6}`, `{0,0.6}`,
`{0,0.8}` — run 3 escalated a rung further, meaning 0.6 also failed there).

Two readings follow, and they matter for how this is fixed: the stochastic **surface** is tiny
(a couple of marginal windows per session, presumably the passages where the model was least
confident), but its **blast radius is everything downstream**. It also means the inter-run
"missing ≥5-word span" is most likely one divergence propagating, **not** ten independent
transcription errors — do not read the replaced-span counts as ten separate defects.
(Aside: `prompt_len` maxes at 227 tokens, the expected `max_length // 2 - 1` conditioning cap.)

**Consequences — these outrank the Stage 1 result in importance:**

1. **This is a partial answer to breakthrough open item 7** ("do the T4 defect classes already
   exist in shipped serial transcription?"). On jp-start, n=1 fixture: **YES for missing
   ≥5-word spans and for ≥5-word replacements; NO for repetition loops.** jp-start is
   comparison-only, so this is descriptive — the decision-grade version is the same harness
   in `--mode baseline` on IT436365.
2. **It does NOT resurrect T4.** T4 failed with 12 missing spans across 5 fixtures, a 16×
   repetition loop, and a ~19 s missed-speech gap; the shipped serial band here is 0–1 missing
   spans and zero repetition. T4 was still clearly worse. What changes is the *framework*: a
   gate phrased as "zero missing ≥5-word spans versus the serial reference" is unachievable
   even by the shipped product, because the reference is itself a random draw. **Future
   transcript gates must be stated against a measured band, not an assumed-exact baseline.**
3. **It weakens this doc's own Stage 1 gate**, see below. It also means the frozen
   `sources_8t` reference transcripts used by older harnesses are one sample, not ground truth.

### Stage 1 result — NOT FALSIFIED, but the test was blunted

Re-driven arm: 75.75 s, 269 segments, `67da0730ed39583d`, temps 0.0/0.6, **68 windows**,
final state `{seek: 165785, all_tokens_len: 4837, prompt_reset_since: 2206, idx: 269}`.
Distances to the three serial runs: −0.14% / +0.80% / +0.97%; missing spans 1 / 0 / 0;
replaced 2 / 8 / 7; zero n-gram repetition.

Every one of those sits **inside** the serial↔serial band (up to 1.10%, 1 missing, 10
replaced), so the preregistered kill condition did not fire. **But "inside a wide noisy band"
cannot distinguish a faithful loop from a subtly buggy one** — the re-driven arm looks like
another draw from the same distribution, which is what a correct implementation *and* several
incorrect ones would both look like. Treat Stage 1 as **provisionally passed, pending a sharp
test**. Do not build Stage 2 on this evidence alone.

Encouraging structural confirmation, independent of the noise: the checkpoint state really is
tiny and serializable — 3 ints plus a ~4.8k-token list across 68 windows.
⚠️ The re-driven arm's 75.75 s is **not** a speed result (see Operational notes).

### ✅ BOTH DIAGNOSTIC ARMS COMPLETE (2026-08-07) — mechanism fully resolved

Both arms: `counselling-31-min`, jp-start, 3 serial reps + re-driven, run sequentially.

**Arm B `--temperature-zero-only` (ladder collapsed to `[0.0]`) — DECISIVE, everything
byte-identical.** All three serial reps *and* the re-driven arm produced hash
`d83d8189dc0ff960`, 1132 segments, 4644 words. Zero differing spans anywhere.
**Therefore: float/threading non-determinism is REFUTED** — ctranslate2 int8 CPU decode on 8
threads is bit-exact reproducible, cold rep and warm rep alike. **And, by elimination, VAD is
proven stateless across calls** (a leaking Silero LSTM state would have desynchronised these
reps too; it did not). The sampling RNG is the *only* cross-run state in the whole pipeline.

**Arm A `--reseed-each-rep` — surprising, and more useful than the outcome I preregistered.**
Re-pinning the seed before every decode did **not** make the three reps match each other.
Instead the arm reproduced the *entire baseline run hash-for-hash, in order*:

| | baseline run | reseed run |
|---|---|---|
| serial 1 | `ea49fb14f4751e1a` (285 seg) | `ea49fb14f4751e1a` (285 seg) |
| serial 2 | `f3200b28ebdd498f` (316 seg) | `f3200b28ebdd498f` (316 seg) |
| serial 3 | `00b0e9fa34df2bc2` (315 seg) | `00b0e9fa34df2bc2` (315 seg) |
| re-driven | `67da0730ed39583d` (269 seg) | `67da0730ed39583d` (269 seg) |

So `ctranslate2.set_random_seed()` **does not reset the generator the sampling path actually
consumes** — but the process as a whole is *perfectly reproducible*. The variation across reps
is not wall-clock randomness; it is a **deterministic function of how many sampling draws have
already happened in that process**.

**The precise, honest product statement — replaces any looser "transcription is random" claim:**
the **first** transcription after app start is exactly reproducible across app restarts; a
**second** transcription of the same audio *in the same process* differs from the first. A
counsellor who re-transcribes a recording without restarting gets a different Source; one who
restarts first gets their original Source back.

**Benchmarking rule this establishes (applies to every future A/B, not just this one):**
compare **rep-index to rep-index across processes** — never rep 1 against rep 2 inside one
process, which silently measures RNG position instead of the lever. The 2026-08-07 ctranslate2
4.7.2-vs-4.8.1 A/B already did this correctly (cold-vs-cold, warm-vs-warm), so its
99.6%-word-identity reading stands; this is a rule for the future, not a retraction.

### ⚠️ The temperature ladder is load-bearing anti-hallucination machinery — do not disable it

Arm B is a **diagnostic setting only**, and its own output proves why it must never ship:
with the ladder collapsed, the transcript grew to **4644 words (+27%) in 1132 segments with 6
n-gram repetition incidents**, versus **3644 words, ~300 segments, 0 repetition incidents**
under production config. That is textbook degenerate looping, normally caught by the
compression-ratio threshold and retried at a higher temperature. **Any future "make
transcription deterministic" proposal that works by removing or flattening the ladder is
rejected in advance on this evidence.** The 1.5%-of-windows stochastic path is buying real
quality.

### ✅ STAGE 1 PASSES SHARPLY — the re-driven loop is byte-exact

Under Arm B's deterministic conditions the re-driven checkpointable loop produced a transcript
**byte-identical to all three shipped serial decodes** (`d83d8189dc0ff960`, 64 windows). This
is the sharp identity test the noisy baseline could not provide. The window loop, VAD handling,
feature extraction, prompt construction, `seek` advancement, and segment splitting are all
confirmed faithful. The only untested branch is the sampling fallback, which is inherently
stochastic and cannot be identity-tested by construction.

**Methodological unlock for Stage 2: `--temperature-zero-only` is the identity-test setting.**
Checkpointed incremental replay must be proven byte-identical to serial *under temp-0*, then
separately shown to behave sanely under production config. Never again gate correctness against
the noisy production-config baseline.

### 🚨 STAGE 2 FINDING (2026-08-07) — the incremental arm FAILED its own identity gate, root cause confirmed

Stage 2 (`benchmark_checkpointed_whisper.py --mode checkpointed`) was built, self-tested
(`--self-test`, pure-logic only), then smoke-tested end-to-end on real audio: jp-start,
`counselling-31-min`, `--temperature-zero-only --arrival-chunk-s 60` (a coarse granularity
chosen only to make the smoke test fast, not the intended production granularity).

| Arm | wall | windows | segments | sha256 (16) |
|---|---|---|---|---|
| serial rep 1 | 117.25 s | — | 1132 | `d83d8189dc0ff960` |
| redriven (Stage 1) | 110.16 s | 64 | 1132 | `d83d8189dc0ff960` (byte-identical to serial) |
| incremental (Stage 2) | 135.09 s | 67 | **316** | `983d10e0cfccaa7e` |

incremental-vs-serial: **not byte-identical**, word delta **-22.7%**, 33 replaced-≥5-word spans,
2 inserted spans, 0 missing spans. This is far outside the Stage 0/1 noise band (which tops out
at ~1.10% word delta, 10 replaced spans) — the preregistered kill condition fires. The good news
first, because it is real and worth keeping: **VAD finalization was perfect** —
`vad_matches_ground_truth_full_file=True`, `vad_revision_violations=0` (the `finalized_vad_chunks`
proof — every VAD chunk but the last is exact, no margin needed — held on real audio, not just
on paper) — and the **checkpoint round-trip worked** (state serialized to a real JSON file,
Python objects destroyed, reloaded from disk only, continuation proceeded correctly). The VAD
and checkpointing mechanisms are not what failed here.

**Root cause, confirmed by direct measurement, not inferred:** `FeatureExtractor.__call__` (read
from `faster_whisper/feature_extractor.py`) does
`log_spec = np.maximum(log_spec, log_spec.max() - 8.0)` — a clip floor relative to the **GLOBAL
max over the entire array passed to the call**, not a per-frame or tail-only quantity. Stage 1's
"causal per frame except at the array tail" mechanism fact describes the STFT/windowing step
correctly but did not account for this separate, whole-array normalization coupling (that
mechanism fact stands for STFT; this is an addition, not a correction to it). A direct diagnostic
(feature-extractor-only, no decode) on `counselling-31-min` confirmed it: features computed over
the first ~20% of VAD-finalized audio (11 of 57 chunks) differ from the same frame range computed
over the FULL session's audio by up to **0.18 absolute** (on the extractor's roughly-unit-scale
output) even in the very first window (frames 0–3000), with 83% of compared frames showing some
difference. Since a growing prefix's audio is a strict subset of the eventual full session, its
running max can only be **<=** the true final max — so quiet/background frames decoded early get
clipped against a floor that is too low relative to what serial's single full-array pass would
use. Under `beam_size=2` at temperature 0.0, a persistent per-frame numerical difference across
nearly every window is enough to flip beam decisions and cascade — exactly the mechanism that
explains 4.7 segments/window (incremental) vs 17.7 segments/window (redriven/serial) on the same
audio: this is not one bad window, it is most windows drifting from very early on.

**This is a structural property of Whisper's own feature extractor, not a bug in the loop
implementation, and not fixable by tuning `--feature-tail-margin-frames`** (that margin guards a
different, much smaller STFT tail-padding edge effect and was never the mechanism here — verified
by the diagnostic testing the *first* window, far from any array tail). A live/incremental
encoder pipeline structurally cannot know the true session-wide loudness max until the session
ends, because `log_spec.max()` is only monotonically non-decreasing as more audio arrives. Two
honest paths forward, neither yet attempted: (a) accept this as a real, unavoidable source of
extra drift and measure whether it stays inside a *widened* but still-defensible band under
**production config** (not temp-zero, which is deliberately decode-brittle by design and may be
overstating real-world impact — production's temperature-fallback ladder and content-aware
retries may tolerate this better than forced-beam temp-0 did); or (b) treat it as a hard kill for
byte-identity and reframe Stage 2's success criterion around the Stage-0-style measured-band
comparison instead, same as production serial transcription itself already requires (see the
Headline Finding above — "future transcript gates must be stated against a measured band, not an
assumed-exact baseline" applies here with extra force). **No ruling made yet — path (a) is the
next run, in progress.**

**Follow-up (2026-08-07, same day): path (a) run complete, plus a repeat of the temp-zero test
at the REAL granularity (the smoke test above used a coarse 60 s arrival chunk only to run
fast).** Both delegated, `counselling-31-min`, jp-start, `--arrival-chunk-s 10` (the harness
default, i.e. the intended production granularity):

| Run | config | incremental vs serial1 | vs serial2 | vs redriven | incremental temps used |
|---|---|---|---|---|---|
| production (`--serial-reps 2`) | normal ladder | -2.28% / 12 replaced | -1.36% / 7 replaced | -1.19% / 9 replaced | `[0.0]` only |
| temp-zero (`--serial-reps 1`) | `[0.0]` forced | -23.32% / 23 replaced | n/a (1 rep) | -23.32% / 23 replaced (redriven was byte-id. to serial) | `[0.0]` |

**Granularity is exonerated.** Real 10 s granularity reproduced the coarse 60 s smoke test's
temp-zero verdict almost exactly (-23.32% vs -22.7%, both ~similar replaced-span counts) — this
is not a granularity artifact, it is the global-max-clip mechanism, confirmed a second way.

**Production config shrinks the gap by roughly 10x but does not clearly close it.** The
previously-established serial-to-serial ceiling (this doc's Headline Finding, same fixture) is
~1.10% word delta / 10 replaced spans. Incremental-vs-serial1 here (-2.28% / 12 replaced) sits
just outside that ceiling on both axes; incremental-vs-serial2 (-1.36% / 7) and
incremental-vs-redriven (-1.19% / 9) sit close to or just inside it. This is a **single run, one
fixture** — not enough to call either a clean pass or a confident kill. Two mechanism notes worth
carrying forward: (1) the reference (serial/redriven) escalated temperature on some windows in
this run (`[0.0, 0.6]`/`[0.0, 0.8]`) while incremental's own decode **never** escalated
(`[0.0]` throughout, all 67 windows) — part of the measured gap is therefore "incremental never
needed its own escape valve" rather than pure word-choice drift, and that is itself informative:
the perturbed features did not push incremental into degenerate/low-confidence territory by the
compression-ratio/log-prob thresholds, they just produced a different-but-plausible transcript.
(2) Production's incremental run hashed **byte-identical** to the temp-zero run's incremental
output (`391e1cddb5c1e4e2` both times) — consistent with note (1): if incremental never
escalates, temp-zero and production-ladder decoding are the same computation for it.

**Speed signal (informal, not Stage 3, but genuinely encouraging).** `final_arrival_decode_s`
(work remaining after the last simulated audio arrival) was **5.08 s** (production) / **5.03 s**
(temp-zero) — both times, out of a full ~31-minute session. 191 ticks completed within a ~345 s
total incremental-arm wall time, i.e. **~1.8 s of harness-side work per 10 s of simulated
arrival on average** — comfortably under the real-time budget a live implementation would need
to keep up during the session. This is an offline simulation processing ticks back-to-back as
fast as possible, not a true real-time measurement, but it is the first evidence that the
mechanics *could* keep pace with real-time arrival, which is the load-bearing precondition for
Stage 3 to be worth attempting at all.

**No owner ruling yet.** Before proceeding to Stage 3 / any Electron or AudioWorklet work, this
needs: (a) repeat production-config runs on the same fixture to see the incremental arm's OWN
run-to-run variance (is -1.2% to -2.3% typical, or was this one draw unlucky?), and (b) at least
one more fixture, since a single 31-minute recording cannot establish a general result. Full
distilled writeup for the owner: `benchmark-reports/JP-START-i7-CHECKPOINTER-Stage2-31min-20260807.md`.

### Open questions for the owner (not scheduled, no work started)

- **Is same-session re-transcription divergence a product issue?** Now precisely characterised
  above. It is orthogonal to live transcription and may matter more.
- **Should production pin the RNG per transcription?** It would make re-transcription
  reproducible and would sharpen all future benchmarking — but it makes an arbitrary draw
  repeatable, not *better*, and `set_random_seed()` is now known not to do it. Needs a real
  fix investigation plus an owner ruling; **not** a silent default change.

### ⏸ Standing resume pointers (unchanged by the above)

- **When the owner next has the i5 (IT436365):** (a) breakthrough item 7 =
  `--mode baseline --serial-reps 3 --machine it436365 --out $BenchOut` (budget 1.5–2.5 h for
  all five fixtures); (b) breakthrough item 2 = the free `no_mtp` `output_sha256` comparison in
  the two `cpu-mtp-audio-qualification-04082026-it436365-v9-*` folders, which exist only on the
  i5 (confirmed absent from both jp-start trees).
- Branch `prompt-improve`. Owner has given standing instruction (2026-08-07) to commit at
  reasonable stages going forward — no longer "commit only on instruction" for this doc's
  own work. Harness code (`benchmark_checkpointed_whisper.py`, Stage 2 additions) and this
  doc's updates are committed as each stage lands; breakthrough plan item 9 status still
  needs syncing to `[-]` if not already done.

This is the scoped execution doc for **open item 9** of
[`TranscribeBeautifyBreakthrough.md`](TranscribeBeautifyBreakthrough.md)'s CURRENT STATUS block
(live/checkpointed transcription — "the AudioWorklet question"). Branch: `prompt-improve`.
Owner priority (recorded 2026-08-07): first pass answers *"does this even work / does it look
faster"*; clinical-quality review is deferred to the owner, manually, later.

### What this is — and what it is NOT

The candidate is a **checkpointable canonical faster-whisper loop**: reproduce the *exact*
serial `WhisperModel.transcribe()` computation — same VAD, same feature frames, same 30 s
window schedule, same token conditioning, same fallback ladder — but with the loop state made
explicit and resumable, so windows can be decoded *during* the session as audio accumulates
instead of all-at-once after Stop.

**This is not T4** (CLOSED-REJECTED 2026-08-06). T4 *sliced the audio* into ~60 s pieces and
decoded each with prompt-stitching — a different segmentation from serial, which is where its
drift came from. Here the audio is **never sliced**: the serial segmentation is reproduced by
construction, and only the *schedule* of when each window gets decoded changes. This is the
exact mechanism the breakthrough plan's Corrections section names as the only legitimate
reopening path, gated on offline identity before any Electron/AudioWorklet work.

### Mechanism facts (verified against `faster_whisper==1.2.1` source, 2026-08-07)

- Under production config (`word_timestamps=False`, default `clip_timestamps`, no
  hallucination threshold), the **entire cross-window mutable state of
  `generate_segments()` is four values**: `seek` (frame index), `all_tokens` (token history),
  `prompt_reset_since` (int), `idx` (segment counter). Trivially serializable.
- `encode()`, `generate_with_fallback()`, `get_prompt()`, `_split_segments_by_timestamps()`
  are **pure functions of their inputs** (plus the model weights). The checkpointable loop can
  therefore **re-drive `WhisperModel`'s own building blocks** — no raw-ctranslate2
  reimplementation, which removes most of the "dies at the identity check" risk the
  breakthrough plan feared. We pin `faster-whisper==1.2.1` (already pinned in
  requirements.txt), so private-API drift is a controlled risk.
- VAD (`get_speech_timestamps`) is a **causal** state machine over 512-sample windows
  (min_silence 2000 ms, speech_pad 400 ms, Silero LSTM state runs forward only). Prefix-VAD
  equals full-file VAD on every chunk whose closing silence has fully elapsed before the
  prefix end — so an incremental VAD with a **finalization margin** reproduces offline chunk
  boundaries exactly, except the trailing open chunk (which is simply not final yet). If a
  session has no 2 s pause for a long stretch, the live loop *lags but is never wrong* — it
  degrades toward today's decode-at-Stop behaviour. Correctness never depends on
  finalization happening early. (To be *proven* per fixture in Stage 2, not assumed.)
- Log-mel features over the concatenated speech audio are causal per frame except at the
  array tail → the **high-water rule**: a window at `seek` may be decoded early only if
  `seek + nb_max_frames` is fully backed by finalized audio; the final short window (zero-pad
  via `pad_or_trim`) is decoded only at true session end. Language detection = first
  window, once ≥30 s of finalized speech features exist.
- VAD→original timeline restoration is `SpeechTimestampsMap` arithmetic — pure, replayable.

### Operational notes on the harness (verified against source, 2026-08-07)

- **The re-driven arm's wall time is NOT a like-for-like speed number, by construction.** It
  takes `language` from the serial arm (skipping the language-detection window) and always runs
  4th in the process, so the model is warm. Identity is unaffected; **never quote redriven wall
  time as a speed result** — Stage 3 carries the speed question with its own design.
- **i5 (item 7) run sizing:** all five fixtures = 214 min of audio; at the i5's measured
  transcription rtf 0.13–0.21 (production log, RunID `7ca64019`), 3 reps ≈ **1.5–2.5 hours
  unattended**. Budget for it, or narrow `--fixture` for a first read.
- Faithfulness points confirmed line-by-line against `generate_segments()`: `content_frames`
  arithmetic, the no-speech skip's `seek += segment_size`, prompt-reset placement *after* the
  segment-emission loop, `previous_tokens` computed *before* encode, the
  `start == end or not text.strip()` drop happening *before* `all_tokens.extend`, and the
  words=None branch of `restore_speech_timestamps`. The `word_timestamps` seek-adjustment and
  hallucination-skip branches are unreachable under production config and are deliberately
  absent — if production ever enables `word_timestamps`, this loop must be revisited.

### Stage ladder and gates

| Stage | What | Gate / kill condition |
|---|---|---|
| **0. Serial determinism baseline** | N× production `transcribe()` per fixture in one process, pairwise `word_diff_report` + n-gram repetition + transcript SHA256 | Defines what "identity" *can* mean on this machine (byte-identity vs a measured run-to-run band). No pass/fail — it is the ruler. **Doubles as breakthrough item 7's harness** (3× serial reliability on IT436365). |
| **1. Re-driven whole-file loop** | Our loop over the model's own building blocks, same process, options object taken *from the serial arm's returned `info.transcription_options`* (no hand-copied config drift) | **KILL** if serial↔redriven distance exceeds the Stage 0 serial↔serial band (any ≥5-word missing/inserted/replaced span not also seen between two serial reps). |
| **2. Checkpointed incremental replay** | Audio fed as growing prefixes (~5–10 s arrival granularity), incremental VAD + finalization margin, high-water window rule, checkpoint state serialized/restored across a simulated process boundary | Same identity gate as Stage 1, all 5 fixtures. Plus: checkpoint round-trip produces identical continuation. |
| **3. Speed shape** | Measure Stop→final-Source with the live loop (only the tail + unfinalized region remains at Stop) + in-session duty cycle | Report only — owner reads it against the i5's measured 6.6–7.4 min per ~49-min session. **Only after this**: any Electron/AudioWorklet capture design. |

### Preregistration (per breakthrough plan §0.3) — Stages 0+1

- **Hypothesis:** a re-driven canonical loop reproduces serial `transcribe()` output within
  the machine's own serial run-to-run band; loop state is checkpointable at every window
  boundary. **Single lever:** loop control/scheduling only — model, config, VAD, features,
  fixtures all pinned to production (`base`/int8/`cpu_threads=8`/`beam_size=2`/
  `vad_filter=True`/clinical initial_prompt/no word_timestamps/language auto-detect).
- **Minimum useful speed effect:** `N/A — enabling/reliability work` (Stage 3 carries the
  speed question; the prize sized from production logs is the i5's ~6.6–7.4 min
  transcription block collapsing to roughly the tail at Stop).
- **Kill conditions:** Stage 1/2 gate above. Transcript-quality kill = any clinically-material
  span class (risk/safeguarding/history/intervention/screening) present in serial and absent
  or replaced in the candidate, beyond the Stage 0 band.
- **Machine:** jp-start (comparison-only; identity is a correctness question, so this is
  legitimate first ground — but no timing claim from it, and the decision-grade identity +
  item-7 run belongs to IT436365). Office load uncontrolled; that is *part of* the
  determinism question, not a confound to it. Power state recorded per run.
- **Runtime/model:** `faster-whisper==1.2.1`, `ctranslate2==4.8.1` (post-bump — note the
  frozen 4.7.2-era CLOCK4 references are gone from this repo and would be invalid anyway),
  bundled base model dir via `config.WHISPER_BUNDLED_DIR`. `ctranslate2.set_random_seed()`
  pinned from `PRIVATE_AI_SEED` (default 20260807) and recorded; per-window chosen
  temperature recorded so we know whether the sampling path (where a seed matters) ever ran.
- **Fixtures:** the five frozen recordings in `private_storage/sessions/Unsorted/`
  (read-only). First decisive run: `counselling-31-min` only (minimum decisive before any
  matrix, rule §0.2.9); full 5-fixture pass only after the single-fixture read.
- **Artifacts:** `benchmark_checkpointed_whisper.py` under `backend/tests-benchmarks/`,
  output to `--out $BenchOut` (private-test-debugs sibling; never
  `backend/benchmark_results/`). Transcript text/diff-span contexts land only in the out
  dir; console prints counts only (no PHI in tracked files or reports).
- **Why not an accidental repeat of a closed candidate:** T4/batched-Whisper/live-slice all
  *changed the segmentation*; this candidate's defining property is that the segmentation is
  byte-equal to serial by construction. The closed ledger's reopening requirement ("a new
  mechanism, not a rerun") is met — this is the mechanism the Corrections section itself
  prescribes.

### Execution log (newest first)

- **2026-08-07 (6):** Two follow-up Stage 2 runs (delegated, jp-start, `counselling-31-min`,
  real `--arrival-chunk-s 10`): production config and temp-zero. Temp-zero reproduced the smoke
  test's verdict almost exactly (-23.32% vs -22.7%), exonerating arrival granularity as the
  cause. Production config shrank the gap ~10x (-1.2% to -2.3% depending on which serial rep it's
  compared against) but sits at/just past the previously-seen serial-to-serial ceiling on the
  worst pairing — inconclusive on n=1. Speed signal encouraging: ~5 s of remaining work after
  the last simulated audio arrival, both runs. Full numbers in "🚨 STAGE 2 FINDING" above and
  `benchmark-reports/JP-START-i7-CHECKPOINTER-Stage2-31min-20260807.md`. No owner ruling yet; more reps + a second
  fixture needed before any Stage 3 decision.
- **2026-08-07 (5):** Stage 2 harness built (`finalized_vad_chunks`, `run_checkpointed_incremental`,
  `--mode checkpointed` + `--arrival-chunk-s`/`--feature-tail-margin-frames`/
  `--checkpoint-fraction`). `--self-test` clean. Smoke test on real audio (`counselling-31-min`,
  temp-zero, 60 s arrival granularity) FAILED the identity gate (-22.7% words, 33 replaced
  spans); VAD finalization and checkpoint round-trip both worked correctly. Root cause confirmed
  by a direct feature-extractor diagnostic (not guessed): the global `log_spec.max()-8.0` clip.
  Full detail in "🚨 STAGE 2 FINDING" above. Production-config run at the intended ~10 s
  granularity delegated next, to see whether real-world divergence is tolerable or a hard kill.
- **2026-08-07 (4):** Arms A + B COMPLETE. Arm B byte-identical throughout → float/threading
  determinism confirmed, VAD statelessness confirmed by elimination, **Stage 1 passed
  byte-exact**. Arm A reproduced the baseline run hash-for-hash → process-level reproducibility
  with rep-position-dependent RNG; `set_random_seed()` does not reset the sampling generator.
  Temp-0 shown to be quality-destructive (+27% words, 6 repetition incidents) — diagnostic only.
- **2026-08-07 (3):** Harness gained three diagnostic flags — `--reseed-each-rep`,
  `--temperature-zero-only`, `--label` (the last is *required* whenever a diagnostic flag is
  used, so an arm can never overwrite the production-config baseline's evidence). Arms A and B
  launched sequentially. `--self-test` clean; label guard verified to refuse.
- **2026-08-07 (2):** First identity run COMPLETE (~5.8 min wall,
  `checkpointed-whisper-identity-07082026-jp-start`, ctranslate2 4.8.1, seed 20260807).
  Stage 0 returned **non-deterministic shipped serial transcription**; Stage 1 not falsified
  but weakly tested. Full numbers and consequences in the Headline Finding above.
- **2026-08-07 (1):** Doc created; Stage 0+1 harness `benchmark_checkpointed_whisper.py` built
  (`--self-test` clean); §0.3 preregistration recorded before any run.

### Standing rules inherited from the breakthrough plan

jp-start comparison-only / IT436365 decision-grade, never merged; pin the seed; control arm
within condition before across conditions; extend contract-validated harnesses; fixtures and
`private-test-debugs` are read-only; no PHI in tracked files; work on `prompt-improve`; no
merge/push without owner instruction.
