# PRIVATE Transcribe & Beautify Breakthrough — rolling execution plan

## ▶ CURRENT STATUS — the only thing a new session needs to read

**Last updated: 2026-08-07.**

> ### 🔒 How this block is maintained — read before editing anything
>
> **This block is OVERWRITTEN, never appended to.** It lives at the top of the file so its address
> never changes. Do **not** add a `§11.14`, a new dated handover section, or a second "start here"
> banner — that is exactly what broke this document before (four pointers, three of them stale,
> one actively contradicting the current status). When something changes: **edit this block**, and
> add the evidence to the archive below.
>
> Everything from §1 to §11.13 is the **evidence archive** — dated, accurate as a record of what ran,
> and never the instruction. Cite it; don't hand it over.

### Where things stand in one line

The engine-flag and GPU search spaces are exhausted with measurements. **CPU-MTP is the one lever
that worked and it is already shipped.** The critical path is now a **human** one: nobody has
confirmed that the notes coming out are clinically acceptable.

### Settled — do not reopen without a genuinely new mechanism

| Closed | Why | Where |
|---|---|---|
| Reasoning budget, ubatch, Flash attention, upward threads, n-gram speculation | All measured, no keepable win | §11.11.1, `053`/`054` |
| Batched Whisper | Drops clinically material speech | `055` §0C |
| Transcript preparation Phase 0 | Prepared Source is 4.5–11.1% *larger* | `TranscriptPreparation.md` |
| Gemma iGPU / Vulkan / `-ngl` target placement | Architectural — Iris Xe shares system DRAM, so offload buys no bandwidth and prefill is bandwidth-bound | §11.11.1 |
| whisper.cpp GPU arms (T7b.0) | 16.88% / 13.93% journey ceiling vs a ≥20% gate | §11.9 |
| T7d concurrent prefill during Whisper | No free concurrency on a CPU-only stack; failed on both machines within 0.6 s of the same net | §11.11.6 |
| **T4 live transcription (1 s overlap, timestamp-trim stitch)** | **REJECTED 2026-08-06** — negation reversal, relocated self-harm span, 19 s missed-speech gap, 16× repetition loop | §11.12, `TranscribeBeautifyAudioWorkletNode.md` §11 |
| Reasoning-off | **Owner decision, not an engineering closure.** Timing was clean; owner declined the lever | `055` §0B |

**Shipped and working:** CPU-MTP draft-ahead decoding, on by default when the draft GGUF is present.
18–24% faster note-writing, and its benefit **scales inversely with machine strength** — it helps the
weak fleet most. Kill switch is `PRIVATE_AI_DISABLE_MTP=1`.

### Open — in priority order

1. **`[~]` MTP blind practitioner review — the critical path, and it needs a human.** Rescoped
   question is *"are these notes clinically acceptable?"*, **not** *"is MTP worse?"*, scored against
   Source on a blinded mixed set from both arms. Give the pre-existing incomplete-Risk-Level finding
   (§11.10, 4 of 6 fixtures) at least equal weight. This blocks a shipping decision on something
   already live. No model can execute it.
2. **`[ ]` IT436365 MTP determinism check — free, ~5 minutes of reading, no new run.** Compare the
   three `no_mtp` `output_sha256` values per fixture in the two
   `cpu-mtp-audio-qualification-04082026-it436365-v9-*` folders (exclude v9 row 12, interrupted).
   ⚠️ jp-start already ran this and **FAILED** it — different hashes at temperature 0.0 with a pinned
   seed. If IT436365 also differs, byte-identity is off the table for every future A/B. Either way,
   **write the outcome into this block.**
3. **`[x]` COMPLETE 2026-08-07 — fixed `word_diff_report`'s `replace` blindness.**
   `word_diff_report` now branches on `tag == "replace"` too (new `replaced_spans_ge_5_words` key,
   additive — existing keys unchanged), wired into the row/print/SUMMARY output alongside missing
   spans. Also fixed the sibling defect the Sol Max review actually traced T4's duplication to: the
   segment-ownership filter (`slice_and_transcribe`) checked only `mid < official_start`, never an
   upper bound, so a segment in a slice's right-hand overlap was kept unconditionally and then kept
   again out of the next slice's left-hand overlap. Extracted as a pure, unit-tested
   `segment_owner_slice(mid_s, boundaries_s)` (half-open `[start, end)` per slice) and both call sites
   updated. `_self_test()` gained: an ownership test (every mid across a boundary set maps to exactly
   one slice, including exact-boundary edge cases) and a `replace`-opcode test (a same-length
   substitution that previously vanished under both `missing_spans_ge_5_words` and
   `inserted_spans_ge_5_words` now lands in `replaced_spans_ge_5_words`, and does not double-count
   under the other two). `--self-test` passes. **Known residual limit, unchanged by this fix and
   out of scope for it:** `MIN_DIFF_SPAN_WORDS = 5` still gates `replace` the same as delete/insert,
   so a short flip (e.g. dropping a single "not") stays invisible — that is a threshold-sensitivity
   question, not an opcode-coverage one. File: `backend/tests-benchmarks/benchmark_live_slice_replay.py`.
4. **`[ ]` Two counterbalanced real-application MTP rows** — only after item 1 clears. Reuse the
   frozen ~45-minute Source; never re-transcribe it. Check whether `activity_log`'s existing
   `beautify-single` timestamps already yield Source→durable-draft before building renderer
   instrumentation (§11.10's blocker was an unavailable surface, not a design flaw).
5. **`[ ]` Write the two T4 Phase 0A summary reports** into `benchmark-reports/` — the only remaining
   T4-specific action. Narrative only, no raw transcript content, content-class descriptions only.
6. **`[x]` MEASURED 2026-08-07, jp-start (comparison-only) — inconclusive, then adopted anyway by
   owner ruling for live/dev use.** New harness: `backend/tests-benchmarks/benchmark_ctranslate2_version.py`
   (one lever only — ctranslate2 version, which is a property of which venv it runs from; extends
   `benchmark_whisper_threads.py`'s helpers rather than re-implementing them). N=1 trial per version
   on the real `counselling-31-min.mp3` fixture: control (4.7.2) cold-pass 87.2s vs candidate (4.8.1)
   cold-pass 95.4s (candidate **9% slower**); control warm-pass 115.5s vs candidate warm-pass 98.9s
   (candidate **14% faster**). Both readings come from the same two runs — jp-start's own pass-to-pass
   thermal/scheduling noise (32% swing within the unchanged 4.7.2 control alone) is larger than the
   effect being measured, so **direction is genuinely unresolved at this sample size**, not just the
   size of the win. Output text was reassuring: 99.6% word-identical, zero missing/inserted ≥5-word
   spans (verified with the item-3 `word_diff_report` fix above), only 4 small `replace`-class
   substitutions — consistent with ordinary cross-backend rounding, not content loss. **Owner ruling
   (Jonathan, 2026-08-07): adopt anyway for live testing** — cost/reversibility was judged low (DLL
   footprint identical to 4.7.2: same three DLLs, near-identical sizes; within
   `faster-whisper==1.2.1`'s own declared `ctranslate2<5,>=4.0` range) against a real, if unproven,
   upside. **`backend/env` is now live on `ctranslate2==4.8.1`; `backend/requirements.txt` pins it**
   (`faster-whisper==1.2.1` line, with an inline comment noting the 2026-08-07 trial). Revert via
   `pip install ctranslate2==4.7.2` if needed. One real-world data point since adoption (RunID
   `4189e0ce`, 2026-08-06 — timestamps are UTC, same calendar day as this measurement in
   NZ local time): a genuine 4-item Transcribe & Beautify bulk run on jp-start completed cleanly,
   `rtf` 0.058–0.0727 per item — no crashes, no quality complaints, but **not a controlled
   comparison** (different audio than the A/B above). **This item invalidates the frozen-fixture
   evidence rule for any future ctranslate2-version work**: the CLOCK4_SOURCES frozen references and
   every prior Whisper benchmark in this file's archive were captured under 4.7.2 — a future
   comparison against them is no longer apples-to-apples on jp-start/dev machines now running 4.8.1.
   Sizing context (unchanged): transcription is 38.7–44.1% of clock (4), so even upstream's full
   claimed ~23% packed-GEMM microbenchmark win, if it ever holds on real Whisper decode, nets
   ≈9–10% of total session time (~30s on a 45-minute session) — real but small, and still unverified
   in either direction. The original "isolated env only, never upgrade in place" caution (still the
   right default for future dependency-bump experiments) was deliberately overridden here by an
   explicit owner ruling weighing low reversal cost against the uncertainty above — not a precedent
   that unverified speed candidates get shipped by default.
7. **`[-]` PARTIALLY ANSWERED 2026-08-07 on jp-start — and the answer is YES.** Question: do the
   T4 defect classes already exist in **currently shipped serial transcription**? First evidence
   (1 fixture, `counselling-31-min`, 3 serial reps, production config, ctranslate2 4.8.1):
   **three decodes of identical audio produced three different transcripts** — 285/316/315
   segments, three distinct hashes, up to −1.10% words, **1 missing ≥5-word span** and up to 10
   ≥5-word replacements between reps; **zero repetition-loop incidents**. Mechanism is the live
   default temperature ladder: a window tripping the compression-ratio/log-prob threshold retries
   at temperature > 0, which is **sampling**, and one divergent sample cascades through
   `all_tokens` conditioning and `seek`. **This does not resurrect T4** (12 missing spans, a 16×
   repetition loop and a ~19 s gap are far outside this band) — but it retires the *framework* of
   gating transcripts against an assumed-exact serial reference; future gates state a measured
   band. jp-start is comparison-only, so **the decision-grade version is still owed**:
   `benchmark_checkpointed_whisper.py --mode baseline --serial-reps 3 --machine it436365`
   (budget 1.5–2.5 h for all five fixtures). Full numbers, consequences, and two in-flight
   diagnostic arms (RNG-reseed / temperature-zero) are in
   [`CheckpointedTranscription.md`](CheckpointedTranscription.md).
8. **`[ ]` 135U/16 GB fleet qualification** — no such machine available. Do not wait for one; it
   blocks nothing above.
9. **`[-]` ACTIVE 2026-08-07 — live/checkpointed transcription (the AudioWorklet question),
   scoped and started.** Owner approved starting; scoped execution doc (stage ladder, gates,
   §0.3 preregistration, its own Current Status block) is
   [`CheckpointedTranscription.md`](CheckpointedTranscription.md) — **that file is now the
   single source of truth for this item; keep only the pointer here.** Session-1 findings that
   de-risk the plan's worst case: under production config the entire cross-window mutable state
   of `generate_segments()` is four values (`seek`/`all_tokens`/`prompt_reset_since`/`idx`),
   and `encode`/`generate_with_fallback`/`get_prompt`/`_split_segments_by_timestamps` are pure —
   so the checkpointable loop **re-drives `WhisperModel`'s own building blocks** (pinned
   `faster-whisper==1.2.1`), no raw-ctranslate2 reimplementation needed. Harness:
   `backend/tests-benchmarks/benchmark_checkpointed_whisper.py` (Stage 0 serial-determinism
   baseline + Stage 1 re-driven identity arm; its `--mode baseline --serial-reps 3` on IT436365
   **is** item 7's protocol — one script serves both). Not T4: audio is never sliced; serial
   segmentation is reproduced by construction, only the decode *schedule* changes.

### Corrections from the Sol Max 5.6 review (2026-08-06) — independently verified

- **The T4 harness had a stitching defect.** Adjacent slices shared **2 seconds**, not 1
  (`:337-341`), and the only ownership rule was `mid < official_start` with **no matching
  `mid >= official_end`** (`:355-367`), so the right-hand overlap was kept twice and then globally
  sorted. **Measured: 2,217 segments decoded, 0 dropped** across both 2026-08-06 runs — the trim
  never fired once. The duplicated text also fed the next slice's 200-word prompt.
- **What that does and doesn't change.** It explains the word inflation, the repetition loop, and the
  *relocated* span. It does **not** explain the ~19–20 s missed speech or the 2/5 fixtures under 99%
  speech coverage — duplication cannot cause loss. **The rejection stands; the lesson was
  over-claimed.** "This configuration is unsafe" holds. "Slicing audio is fundamentally unsafe" was
  never established.
- **AudioWorklet is UNTESTED, not rejected.** There is no `AudioWorkletNode`, `addModule`, or
  `registerProcessor` anywhere in the app; both recorders call bare `mediaRecorder.start()` with no
  timeslice. It was locked behind a gate that a *different* thing failed.
- **pydub is a NO-GO as a remedy** — wrong layer. It cannot preserve Whisper's token history, seek,
  prompt-reset, fallback, language, or VAD state.
- **If live ASR is ever reopened**, the proposed mechanism is a *checkpointable* canonical
  faster-whisper loop that preserves decoder state, gated on exact offline identity before any
  Electron work — not a wider overlap on the rejected stitcher. Unstarted, unscoped, high risk of
  dying at the identity check.

### Standing rules — machine, branch, evidence

- **jp-start is comparison-only. IT436365 is decision-grade.** Never average or merge their numbers.
- **Pin `PRIVATE_AI_SEED` in every harness.** An unseeded harness is a contract violation — it has
  already cost one 36-row bundle.
- **Every A/B carries a within-condition control arm** before anything is compared across conditions.
- **Extend a contract-validated harness; never hand-roll in `tmp/`.** Two prior incidents.
- **No PHI in tracked files.** Flagged-span text stays in the gitignored `private-test-debugs` tree.
- ⚠️ **Branch discrepancy, unresolved.** This plan declares `prompt-improve`, but the Phase 0A
  commits (`3e488bf`, `5cd6910`) landed on `ui-improvement-bulk-run`. Flagged for the owner.

### Companion documents — cite, don't hand over

| Doc | Role |
|---|---|
| `TranscribeBeautifyAudioWorkletNode.md` | **Closed sub-plan.** T4's execution history and full rejection ruling. Not an active queue |
| `thoughts/SolMaxReview.md` | **Review, not a plan.** Its actionable findings are already promoted into this block |
| `benchmark-reports/temp-handover-for-i5.md` | Machine-specific extract for IT436365 |


**Created:** 1 August 2026
**Branch:** `prompt-improve` — ⚠️ but see the branch-discrepancy note in Current Status above
**Overall status:** ACTIVE — not complete
**Production defaults:** frozen until a candidate passes its speed, quality, and reliability gates
**Primary sources of truth:** `CLAUDE.md`, `thoughts/AfterSolMaxAndFable.md`, and
`bugs-fixed/056-01082026(NewFindings).md`

This file is the execution controller for the next phase of the PRIVATE Transcribe & Beautify
initiative. It synthesises the three sources above. When an older plan, handover, or command example
conflicts with this file, the later measured correction wins. Historical evidence remains intact;
stale claims are corrected additively rather than erased.

---

## 0. Operating contract

### 0.1 Tri-state task notation

- `[ ]` NOT STARTED
- `[-]` ACTIVE
- `[x]` COMPLETE

There may be no more than three `[-]` tasks at once. `BLOCKED`, `CONTINUE`, `SHIP`, and `KILL` are
decisions recorded inside a task; they do not replace the tri-state marker. A task becomes `[x]`
only after its evidence, decision, tests, result document, registry entry, and focused commit are
complete.

### 0.2 Non-negotiable execution rules

1. Work only on `prompt-improve`. Do not merge to `main` and do not push without explicit owner
   instruction.
2. Preserve production defaults until a candidate passes all named gates. A large timing win never
   overrides a critical transcript or generated-note quality failure.
3. Preserve fixture bytes and all raw evidence. `examples/` and `examples-raw/` are read-only.
   `C:\Users\wooin\Documents\private-test-debugs\benchmark_results` is also read-only.
4. New raw runs land under `backend/benchmark_results/<experiment-id>/` unless a later owner-approved
   writable evidence root is named. Never move, rewrite, or “tidy” the read-only sibling evidence.
5. Every benchmark Python invocation uses the project venv and unbuffered output:
   `backend\env\Scripts\python.exe -u ...` (or `env\Scripts\python.exe -u ...` from `backend/`).
6. Silent redirected output is not proof that a process died. Check process state and artifacts.
7. An external termination on a managed device is not attributed to EDR without authoritative
   evidence. Local absence of an event is also not proof of the opposite.
8. No closed candidate is rerun unless its task below names a materially new reopening mechanism.
9. Run the minimum decisive test before an extended matrix. Stop early on a preregistered critical
   failure or a useful-effect miss that cannot change the product decision.
10. Do not declare the initiative complete after one successful phase.

### 0.3 Before/after protocol for every active task

Before execution, record in the task:

- exact hypothesis and single allowed lever;
- minimum useful speed effect or an explicit `N/A — enabling/reliability work` ruling;
- transcript and generated-note quality kill conditions;
- machine, power state, office load, runtime, model, fixture, and artifact path;
- cold/warm state, bounded thermal stabilisation, repetitions, and balanced schedule;
- exact audio, Source, prompt, template, model, tokenizer, and binary hashes that apply;
- why the work is not an accidental repeat of a closed candidate.

After execution:

- retain raw artifacts and validate the manifest/runtime attestation before reading timing;
- compare transcript/note outputs under §3;
- separate measured observations from inference;
- assign `CONTINUE`, `SHIP`, `KILL`, or `BLOCKED`;
- update this plan, a dedicated `bugs-fixed/` result record, and the registry in §8;
- run proportionate tests and make one focused phase-level commit.

---

## 1. Objective and governing metrics

The retired objective was “30–40% faster” against an invalid ≈711-second composite. It must not be
used as a denominator or silently converted into a new SLO.

The product objective is:

> Minimise predictable time from Stop to a **durably saved reviewable draft**, and minimise the
> time the practitioner is attention-locked, on the weakest representative supported hardware,
> subject to zero regression in Source fidelity, clinical attribution, inspectability, and crash
> recovery.

The required clocks are reported separately:

1. Stop → exact editable Source durably committed.
2. Source committed → first visible draft text.
3. Source committed → reviewable draft durably saved.
4. Stop → reviewable draft durably saved (the governing compute/product clock).
5. Start/Stop → user safely free to navigate or do non-AI work.

Bulk reports enqueue → first draft, drafts/hour, and enqueue → last draft. “Practitioner marked
complete” is a human clinical milestone and is never relabelled as model completion.

No signed 135U product SLO exists yet. Absolute gates will be set from a real Core Ultra 5 135U /
16 GB production journey, not derived from the retired composite.

---

## 2. Current measured state

### 2.1 What today actually established

| Evidence | Measured result | Current meaning |
| --- | --- | --- |
| `jp-start` composed cold clock | 31.68 min audio → 4.09 min; 43.50 → 5.70; 49.45 → 5.53; 51.58 → 7.01 | Machine-specific composed baseline, not an observed production journey and not a fleet SLO |
| `IT436365` Whisper, 5 fixtures | 2.59 / 3.59 / 4.03 / 3.93 / 6.25 min | Dell-class i5-1135G7 evidence; 1.6–2.0× `jp-start` where comparable |
| `IT436365` Beautify, 12 rows | median 4.42 / 7.18 / 8.00 / 10.11 min | Complete attested Dell-class baseline at `-t -1 -tb -1`, auto/3072 |
| `IT436365` composed Stop→draft | 7.00 / 11.21 / 11.93 / 16.36 min | 1.71–2.34× `jp-start`; ratio grows with session size |
| `IT436365` thread screen | `-t 4`: +0.18%; `-t 6`: +4.85% vs auto | No useful lever on this non-hybrid 4c/8t machine; outputs changed |
| Live 60 s/~1 s slice replay | 12 missing ≥5-word spans on 4/5; coverage 99.61–100%; +4.35–6.11% words | `KILL` exact tested mechanism on fidelity; do not build UI |
| Naive unrelated-request warm-up | prompt −12.963 s; total −21.704 s; output hash changed | `KILL` as an output-neutral shortcut; narrower mechanism only remains open |
| Bulk structuring recovery | code fix + 7 isolated tests | **Superseded 2 Aug by T2**: the real force-kill showed that path had never produced a note; auto-resume is now removed by owner ruling (§6 T2, `059`) |
| IT436365 production Beautify (Support Diagnostic Logs, 26–27 Jul) | same ~41.5k-char Source: **9.59 min cold** vs JP-START **4.15 min** = **2.31×**; i5 warm 3.95 vs cold 7.81 min at an identical 12,327-token prompt (n=1 warm) | Descriptive production evidence, **not contract-valid** — corroborates the 1.7–2.3× gap; cannot support a shipping decision (`059` §10) |

Measured and inferred claims stay separate. The IT436365 termination cause is unknown. MDE/EDR is
only a hypothesis and must not be reported as the cause without portal/administrator evidence.

### 2.2 Pre-T0 evidence limitations, subsequently confirmed

These were preliminary observations before Task T0. The completed T0 audit subsequently confirmed
them and recorded the final `LEGACY-INCOMPLETE` rulings in §8 and the dedicated result artifact:

- the final IT436365 Beautify manifest contains machine/runtime/model/fixture/output hashes, but its
  `power_plan` is `null` and one dirty path is malformed as
  `ackend/benchmark_beautify_first_run.py`;
- the five IT436365 Whisper rows record timings, transcript hashes, CPU identity and AC state, but
  `ram_total_gb` is `null` and the rows do not attest exact audio, model, tokenizer, Whisper binary,
  dependency, git, or power-plan hashes/state;
- therefore the narrative results remain useful legacy evidence, but they do not automatically
  satisfy the stronger evidence contract in §4.

Timing from a manifest that fails the new contract may be described historically; it cannot be
promoted into a new shipping decision.

---

## 3. Shared quality protocol

### 3.1 Transcript gate

For any ASR/output-changing candidate:

- exact timeline coverage is recorded; minimum acceptable coverage is 99%;
- zero contiguous missing span of five or more words across the frozen five-fixture set;
- zero clinically material omission of any length involving risk, safeguarding, negation,
  qualification, distress, treatment choice, homework/intervention, medication, dates, or plans;
- zero whole duplicated exchange and no new generalising repetition-loop mechanism;
- no loss of self-correction, uncertainty, role-play/hypothetical boundaries, or speaker ambiguity;
- aggregate word-count parity alone never passes the gate.

One critical failure stops the candidate even if its timing is exceptional.

### 3.2 Generated-note gate

Use the existing staged funnel:

1. Validate evidence contract and timing gate before owner review time is spent.
2. **Establish the within-condition control arm before comparing anything across conditions
   (added 2026-08-05 — this step is mandatory and was the gap that wasted a 36-row run).** Repeat
   the **control** condition against itself, same fixture, same pinned seed, n≥2, and record whether
   its outputs are byte-identical. Until this is known, a between-condition output difference cannot
   be attributed to the lever, because the product's own run-to-run variance is unmeasured.
   - Control reproduces itself → between-condition differences are real effects of the lever, and
     steps 3–6 are meaningful.
   - Control does **not** reproduce itself → the variance band is at least as wide as any observed
     between-condition difference. Blind pairs comparing one output against one other output are
     uninterpretable; either widen to a distribution (n≥3 per condition, scored on a rubric) or
     accept the lever on mechanism grounds and say so explicitly.
   - **§4.1 already requires the seed to be recorded and forbids required fields silently becoming
     `null`.** An unseeded harness is a contract violation, not a stylistic choice — see §11.10.
3. Check finish reason, truncation, headings/order, export reopening, placement, empty fields, and
   exact output hashes.
4. Produce a risk-directed Source↔output diff for factuality, attribution/provenance, role-play,
   risk/safeguarding, negation, dates, appointments, interventions, follow-up, omissions, and
   unsupported fields.
5. Use fresh opaque case IDs and separate blind-key custody. Hash the completed scorecard before
   unblinding.
6. A single critical regression is a kill, regardless of timing. “No regression” is comparative;
   it does not certify an already-defective control as clinically adequate. **Corollary, and it has
   already fired once:** when both arms carry the same defect, that is a finding about the product,
   not about the lever, and it belongs in the defect record rather than the lever's verdict
   (§11.10 — incomplete Risk Level / template sections in 4 of 6 jp-start fixtures, including one
   where both arms failed).

### 3.3 Reliability gate

- audio and Source are never lost;
- Source is committed before draft finalisation;
- recovery is idempotent and lands exactly once in the intended session/template/model snapshot;
- cancellation preserves Source and leaves no hidden runnable orphan;
- navigation, renderer reload, backend restart, sleep/wake, and app relaunch have explicit outcomes;
- runtime configuration is resolved from truthful startup evidence, never assumed from requested
  flags or `/props` alone.

---

## 4. Evidence contract for all new runs

Every run has a hashed preregistration spec and an immutable postflight manifest. Required fields
may not silently become `null`.

### 4.1 Preregistration spec

- experiment ID, hypothesis, decision threshold, early-stop rules, and one allowed lever;
- target machine eligibility and named workload/load/power strata;
- complete scheduled row matrix generated before execution, including balanced per-fixture order;
- bounded thermal stabilisation duration and its start/end timestamps;
- exact fixture/audio/Source/template/prompt/model/tokenizer/binary/DLL/dependency hashes;
- requested runtime, seed, context, threads, batch threads, reasoning, cache, KV, Flash, and
  speculative settings;
- transcript/note/reliability kill conditions and blind-key custody mode;
- expected artifact root and minimum free disk space.

### 4.2 Runtime/postflight attestation

- hostname/pseudonym, CPU string, physical/logical topology, RAM configuration, OS build;
- AC/battery percentage, power plan, office-idle or office-light load, available RAM;
- git commit, branch, exact dirty-file paths and hashes;
- complete raw startup log plus parsed effective threads/batch threads, backend/device, context,
  batch/ubatch, KV, Flash, reasoning, speculation, model allocation and server version;
- per-row monotonic sequence, start/end time, cold/warm state, stage timings, token counts, output
  hashes, finish/cancel/failure state, and parent spec hash;
- post-run fixture hashes and a manifest validity verdict with named reasons.

Timing is not interpreted until the validator returns `VALID`.

---

## 5. Borrowed-machine playbook

This applies to a colleague’s 135U, 235U, 1355U, or similar machine.

1. Confirm explicit permission and a practical test window. Do not weaken institutional security
   controls or request administrator access merely to obtain a benchmark.
2. Use `prompt-improve` at the exact preregistered commit. Record all dirty files; do not call a
   copied/modified tree clean.
3. Verify the project venv, production model, bundled server and Whisper model hashes before loading
   a fixture. Do not rename model files.
4. Record exact CPU/RAM/DIMM/OS, AC and battery state, Balanced/other power plan, available memory,
   and office-idle/office-light load. Do not infer P/E/LPE placement from CPU marketing names.
5. Stabilise for a preregistered bounded five minutes before the first row and between condition
   blocks. Record the actual window; do not wait indefinitely for an unobservable “perfect” thermal
   state.
6. Run the minimum decisive production journey first. Validate the manifest before reading timing.
7. Only if the minimum test passes its reliability/quality gates, run the balanced thread/Whisper
   screen. Do not use the stale forward-then-reverse commands as the schedule; generate and retain
   a balanced per-fixture schedule.
8. Use `python -u`. If output is quiet, inspect the process and artifacts. If externally terminated,
   record `UNKNOWN EXTERNAL TERMINATION`; do not label it EDR without authoritative evidence.
9. Stop on battery change, unexpected load, runtime mismatch, fixture/hash mismatch, critical
   transcript/note defect, or an effect too small to change the decision.
10. Copy nothing into the read-only sibling evidence tree. Preserve the local raw run and write a
    repository result document linking its exact path and hashes.

---

## 6. Rolling task queue

### [x] T0 — Evidence-contract validator and today-evidence audit

**Decision class:** enabling reliability work; not a speed candidate.
**Activated:** 1 August 2026.
**Hypothesis:** a versioned, fail-closed preregistration/manifest validator can prevent the known
machine-attribution, requested-vs-resolved runtime, malformed-path, missing-hash, and silent-null
failure classes before timing is interpreted, without touching production execution.
**Allowed lever:** benchmark tooling and tests only. No production router/service/frontend/default
change and no model inference.

**Preregistered speed threshold:** `N/A — enabling/reliability phase`. It is not permitted to claim
a product speed improvement. Validation runs outside model timing and must not change any existing
timed field.
**Transcript kill conditions:** any fixture/audio/Source byte or timestamp changes; any validator
write to an evidence input; acceptance of a missing or mismatched required input hash.
**Note-quality kill conditions:** any model request/output change; acceptance of a missing output
hash, finish reason, truncation, heading/export status, or required runtime field for a run type
that produces notes.
**Reliability kill conditions:** false `VALID` for a required-field/hash/config mismatch; mutation
of the inspected artifact; non-deterministic verdict for identical input; test access to the live
clinical DB/storage.

**Machine/power/load:** `JP-START`; Intel Core 7 240H; 10 physical/16 logical cores; 31.6 GiB,
2×16 GB DDR5-5600; AC connected, battery 100%; Windows Balanced plan; office-idle.
**Runtime:** project venv Python 3.12.8; PowerShell 5.1.26100.8875; branch `prompt-improve`; starting
commit `54bb62b426909fe53fba8743217c42bd66cc0eda`. The initial planning snapshot contained only this
new untracked plan; the immutable run spec later captured the exact ten-file dirty implementation
state and per-file hashes before the audit began.
**Model/fixtures/cold-warm/thermal:** N/A; no model/audio/clinical fixture and no timed inference.
Tests use generated temporary JSON in isolated temp directories. No thermal stabilisation is
required because timing is not read.
**Artifact path:**
`backend/benchmark_results/evidence-contract-01082026-jp-start/tooling-v1-final/` for the final
bundle and sibling `tooling-v1-final-inputs/` for preregistration/test-isolation material; dedicated result record
`bugs-fixed/057-01082026(NewFindings).md`.
**Not a repeat:** prior work added partial machine/thread attestation to the Beautify harness. It
did not build the complete immutable spec/postflight validator, Whisper evidence coverage,
artifact self-validation, or registry required here.

**Minimum decisive implementation:**

- versioned schema/validator shared by benchmark tooling;
- pure read-only CLI validation with named failure reasons and non-zero exit on invalid evidence;
- tests for missing/null fields, malformed dirty paths, hash mismatch, schedule imbalance,
  requested/resolved runtime mismatch, artifact mutation detection, and deterministic verdict;
- audit the IT436365 Beautify baseline, all three thread-screen runs, and all five Whisper rows
  from the read-only sibling, recording measured deficiencies without modifying them;
- update §8 and the dedicated result record; run targeted tests; focused commit.

**Completion gate:** validator/tests/docs complete; no production files/defaults changed; current
legacy artifacts receive honest `VALID`, `LEGACY-INCOMPLETE`, or `INVALID` rulings with reasons.

**Measured result (completed 1 August 2026):** the v1 tooling bundle independently validates
`VALID` with an empty issue list. The isolated suite passed 154/154 with child return code `0`.
All 22 legacy core files remained byte/hash/mtime-identical. All nine legacy subjects rule
`LEGACY-INCOMPLETE`: 4/4 Beautify and 5/5 Whisper, each with 11 incomplete findings and zero
errors/warnings. Product speed effect is 0 seconds (0%); no model ran and no output/default changed.

**Inference:** the old i5 measurements remain descriptive history but cannot support a new ship
decision. New cross-laptop runs must be produced through the v1 contract; T0 does not prove any
speed or note/transcript quality candidate.

**Decision:** T0 tooling `SHIP`; overall initiative `CONTINUE`. Full ruling and raw hashes:
`bugs-fixed/057-01082026(NewFindings).md`.

### [x] T1P — Borrowed-i5 v1 package integration and offline handoff validation

**COMPLETED 2 August 2026. Decision: tooling `SHIP`; T1 unblocked.** Full record and the exact
run-today procedure: [`bugs-fixed/058-02082026(NewFindings).md`](../../bugs-fixed/058-02082026(NewFindings).md).
Commits `6982cdc` + `03e0121` on `prompt-improve`; 136 tests pass; no production file or default
changed; product speed effect 0 s (0%).

Three corrections this task forced, which supersede the §10 handover where they conflict:

1. **A `journey` bundle can never rule `VALID` straight off a machine** — it requires a completed
   practitioner transcript/note review. A new **`PENDING-REVIEW`** verdict (CLI exit 3) now covers
   "machine evidence sound, human review outstanding", and `apply-review` seals a *second* bundle
   that rules `VALID` without ever mutating the original.
2. **§10.4's renderer-instrumented journey was NOT built** (multi-day). A journey now preregisters
   `observation_mode`; this runner is `backend_service`, which measures clocks 1/3/4 honestly and
   records `time_to_free_ms` as an explicit unobserved null. The validator rejects a backend run
   that reports a number for it. §10.4 remains open and is still required for clock 5.
3. **The bundled b9585 silently disables `--cache-reuse`** (captured from a real startup log), so
   `note_cache_reuse_tokens` preregisters `0`. `CLAUDE.md`'s engine-defaults list is stale on this
   point.

The original activation text is retained below for its preregistration record.

---

**Decision class:** enabling reliability work; not a speed candidate and not the borrowed-machine
model run.
**Activated:** 1 August 2026.
**Hypothesis:** a benchmark-only adapter and exact handoff command can turn the existing production
journey entry points into a create-only v1 evidence bundle on the borrowed i5, fail closed before
model execution when its local hashes/runtime/attestation are incomplete, and preserve the full
transcript/note quality evidence needed for T1 without changing production behaviour.
**Allowed lever:** benchmark adapters, offline tests, handoff documentation and generated local
evidence only. No production router/service/frontend/default change and no model inference on
JP-START.

**Preregistered speed threshold:** `N/A — package-preparation phase`; product timing effect must be
reported as 0 seconds (0%). T1 remains a measurement phase with no candidate shipping threshold.
**Transcript kill conditions:** any mutation of audio/Source/fixture inputs; acceptance of missing or
mismatched audio, Source, prompt, model, Whisper-binary or dependency hashes; relaxation of §3.1;
or an adapter path that can omit the raw transcript and transcript-quality case record.
**Note-quality kill conditions:** acceptance of a missing prompt, raw/final note, DOCX, output hash,
token/finish/truncation status, heading/export check or §3.2 scorecard; any output mutation by an
offline package test.
**Reliability kill conditions:** any non-create-only bundle/result write; access to live clinical
DB/storage; requested/resolved runtime mismatch accepted as valid; legacy output treated as v1;
failure to stop before model execution on incomplete borrowed-machine preregistration; or a handoff
that depends on an unrecorded local path.

**Machine/power/load:** `JP-START`; Intel Core 7 240H; 10 physical/16 logical cores; 31.6 GiB
2×16 GB DDR5-5600, 13.5 GiB available and 469.3 GiB free at activation; AC connected, battery 100%;
Windows Balanced; office-idle. No timed inference, so condition ordering and bounded thermal
stabilisation are `N/A`.
**Runtime:** project venv Python 3.12.8 at
`backend/env/Scripts/python.exe` (SHA-256
`1c4e9fbd9259294528031a567cef76b0a45254b66d612cf58de267928d1defbb`); PowerShell
5.1.26100.8875 (executable SHA-256
`7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5`); branch
`prompt-improve`; starting commit `c4452e70e32684e17db0464b694863e67c60f648`, clean.
**Model/fixtures/cold-warm:** no model, audio or clinical fixture is executed on JP-START. Offline
tests use generated temporary metadata and inert byte fixtures in isolated temporary directories;
cold/warm is `N/A`. The borrowed machine's exact audio, Source, prompt, model, tokenizer, Whisper
binary and dependency hashes remain deliberately unfilled and are a fail-closed T1 activation gate.
**Artifact path:** planned create-only root
`backend/benchmark_results/t1p-i5-package-01082026-jp-start/`; dedicated result record
`bugs-fixed/058-01082026(NewFindings).md`.
**Not a repeat:** T0 proved and audited the generic v1 contract. It did not connect a production
journey handoff to that contract, generate the borrowed-machine preregistration material, or prove
that incomplete local setup stops before either model starts.

**Minimum decisive implementation:** an exact adapter/runner and handoff command; offline tests for
the fail-closed preflight and complete transcript/note/journey bindings; one synthetic create-only
round trip that independently validates; raw artifact hashes and a dedicated result record. Keep
T1 `[ ]` until the real i5 fields are filled and the machine is physically available.

**Completion gate:** package can be copied to the i5 and preflighted without model execution; the
synthetic bundle validates independently; all package tests and the existing evidence suite pass;
production code/defaults and all source fixtures remain unchanged. Final decision is one of
`SHIP`, `KILL`, or `BLOCKED`, with T1 remaining a separate later decision.

### [x] T1 — Borrowed weak-tier minimum decisive production journey

**COMPLETED 2 August 2026 on IT436365.** Stop→durable draft = 611.6 s (≈10.2 min) cold, on a real
43.5-minute recording (transcription 34.4%, Beautify 65.6%) — the composed journey floor this
section called for. Two real bugs in the T1 runner itself were found and fixed along the way; the
row's bundle is **PENDING-REVIEW**, awaiting a practitioner transcript/note read + `apply-review`
before it can rule VALID. This measurement establishes a conservative weak-tier floor; it does not
substitute for or close the separate 2-P-core 135U hybrid-topology question (§11.2, §11.7 item 2).
Full record: `bugs-fixed/060-02082026.md` §1–§5.

**Present decision (superseded, retained for history):** `BLOCKED` until the intended borrowed
machine is physically available. Per the owner’s latest direction, prepare the IT436365-class
i5-1135G7/16 GB package first. A valid i5 run may establish a conservative weak-tier journey floor,
but it does not substitute for or close the separate 2-P-core 135U hybrid-topology question.
**Hypothesis:** the borrowed machine’s actual Stop→durably-saved-draft journey and
time-to-free will determine whether compute latency or workflow captivity is the governing product
problem, while validating crash/cancel/navigation behaviour under fleet-realistic constraints.
**Speed threshold:** measurement phase—no candidate ships. Establish p50/p90 only after valid rows;
do not import the retired 711-second/30–40% target.
**Quality/reliability kills:** any Source/audio loss, wrong-session landing, duplicate landing,
critical transcript/note defect, unresolved runtime mismatch, or invalid manifest.
**Minimum decisive sequence:** first run one cold frozen 45-minute-class recorded-synthetic
scenario through the real production journey. Validate evidence and transcript/note quality before
opening a warm-new-Source row. Navigation, cancellation, and force-kill/relaunch are later
reliability rows, not part of the first minimum row. Do not claim p50/p90 until a separately
preregistered schedule has enough valid repetitions. Extended matrices remain closed until the
minimum row passes.

`056` §5/§8.8 supplies parameter inventory only. Its prepared forward-then-reverse command order is
superseded by this plan’s balanced schedule and evidence contract.

Before activation, fill the exact borrowed-machine attestation, load, hashes, schedule, artifact
path, and quality case IDs in this section.

### [x] T2 — Durable-job force-kill/relaunch verification on an available machine

**COMPLETED 2 August 2026 on JP-START. Decision: `SHIP`.** Two independent defects were found by the
real force-kill — the `056` §2 recovery path had **never** produced a note — and were fixed. The
owner then ruled that **automatic resume is the wrong behaviour**: reopening the app must not start
an unattended multi-minute generation, because the Source is durable and the counsellor re-runs
Beautify from the session themselves. The startup hook is now
`cleanup_interrupted_structuring()`, which retires the leftover queue row and its audio and **runs
no model** — the queue settles in **2,030 ms** instead of 145,077 ms of model work, and all eight
assertions pass against the revised expectation (a note appearing on its own is now a *failure*).
Full record:
[`bugs-fixed/059-02082026(SYLC).md`](../../bugs-fixed/059-02082026(SYLC).md).
Product speed effect **0 seconds (0%)**; no default, prompt, model, engine flag, schema or frontend
file changed.

**ACTIVATED 2 August 2026 on JP-START** under §9 rule 4: the borrowed-i5 package is ready (T1P
`SHIP`) and the borrowed machine is not physically present, so T1 cannot run in this window. This
is not a substitute for T1 and does not touch the 135U question.

**Gate:** activate only after the borrowed-i5 package is ready and borrowed hardware remains
unavailable, or fold the recovery case into a later T1 reliability extension after its minimum
cold row passes. — *satisfied: T1P complete, i5 absent.*
**Hypothesis:** the existing `structuring → transcribed → resumed finalisation` fix lands the draft
exactly once after a real app/process death, with Source intact and no orphan; navigation/cancel
paths release the user without corrupting state.
**Speed threshold:** compute change `0%`. For every minimum recovery row, time-to-free is measured
from the user’s navigate/cancel action to an interactive non-blocked destination and must be ≤10
seconds. Relaunch recovery is a separate reliability clock from process start to exactly one
durably saved draft; its deadline must be preregistered from an observed control before activation.
**Quality/reliability kills:** any lost/changed Source, wrong template/session/model target,
duplicate draft, orphan queue row, automatic “complete” status, or inability to cancel/retry
honestly.
**Minimum decisive scope:** exercise only the real bulk
`structuring → transcribed → resumed finalisation` force-kill/relaunch path first. The seven
isolated tests recorded in `056` did not kill and relaunch the real app/process, so this is not an
accidental repeat. Renderer-held single-session chaining is a distinct later subphase and cannot
be inferred from the bulk result.

#### T2 preregistration (filled before execution, per §0.3)

**Single allowed lever:** none — this is reliability verification, not a speed candidate. No
production default, prompt, model, or engine flag is varied. Product speed effect must be reported
as 0 seconds (0%).

**Observation mode:** `backend_service`. The runner drives the real FastAPI process and the real
services; it never renders a frame, so `time_to_free_ms` is recorded as an explicit unobserved
null with a stated reason — the same honesty rule T1P established
(`bugs-fixed/058-02082026(NewFindings).md` §3.2). **The ≤10 s time-to-free bar above is therefore
NOT evaluated in this row**; it stays open for the §10.4 renderer work. Clocks measured here are
`structuring start → run finished` (control) and `relaunch process start → durably saved note`
(recovery).

**Falsifiable prediction, recorded before the run.** Code reading of
`backend/routers/audio_queue.py` predicts the resume will **fail** on the bulk-upload path:

- `BulkAudioUploadModal.tsx:286` calls `api.uploadAudioQueueItem(file)` with no `sessionId`, so the
  queue row is created with `session_id = NULL`;
- with `session_id` NULL, `_run_transcription_queue` takes the **insert branch**
  (`audio_queue.py:531-540`), which creates a new session and calls `_finalize_group` with a
  *local* `resolved_session_id` — it never writes `session_id` back onto the queue row;
- `init_db()` rolls the crashed row `structuring → transcribed` (`database.py:1146`);
- the adoption sweep that could repair `session_id` only matches
  `status IN ('pending','failed')` (`database.py:1185`), so it skips a `transcribed` row;
- `resume_interrupted_structuring()` requires `session_id IS NOT NULL`
  (`audio_queue.py:299`), so it skips the row too.

Predicted observable outcome: Source intact, **no note**, **one orphan queue row**, **one orphan
audio file**. If instead the note arrives, this prediction is wrong and must be recorded as wrong.

**Machine/power/load:** `JP-START`; Intel Core 7 240H; 10 physical / 16 logical; 31.6 GiB
(2×16 GB DDR5-5600), 17.9 GiB available; AC connected, battery 100%; Windows Balanced
(`381b4222-f694-41f0-9685-ff5bb260df2e`); office-idle; 469.7 GiB free disk.
**Runtime:** project venv Python 3.12.8; branch `prompt-improve` at commit `999adf7`; the only dirty
path is the new untracked `backend/tests-benchmarks/benchmark_t2_durable_job.py`. Backend launched in the production
form `python -m uvicorn main:app --host 127.0.0.1 --port <ephemeral>` — **no `--reload`**, because
dev reload is what orphaned `llama-server.exe` in `bugs-fixed/043`.
**Model/fixtures:** production model `gemma4-e2b-qat`
(`gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf`, 2,620,368,960 bytes); Whisper `base` from
`backend/whisper_base/`, beam 2, VAD on, as production resolves it; template `private`
(PRIVATE default schema). Audio fixture
`private_storage/sessions/Unsorted/counselling-31-min.mp3` — 45,626,242 bytes, SHA-256
`2cb10382dbed8fac5e5487c93af4178b9093a0128ea038b57dd661945e3c2f41`, read-only, never modified or
moved. A real full-length counselling fixture is used deliberately: the recovery mechanism is
Source-length-independent, and the shortest real fixture keeps two full runs inside one window.
**Cold/warm:** both rows are cold — fresh isolated DB, fresh process, `llama-server` cold-started
inside the measured span. No thermal stabilisation block is preregistered because no cross-condition
timing comparison is made; the recovery clock is compared only against its own control-derived
deadline.
**Force-kill target/process identity:** the `uvicorn` process the runner spawned, killed with
`taskkill /F /T /PID <pid>` — the same hard kill Electron performs on Windows app close, and the
closest available stand-in for a power loss. The PID and `taskkill` return code are recorded.
**Isolation:** throwaway `PRIVATE_DB_DIR` and `PRIVATE_STORAGE_DIR` under the artifact root;
`PRIVATE_AI_DEBUG=0` and `PRIVATE_AI_DEBUG_DIR` unset so no `debug/` artifact is written anywhere;
the runner refuses to start if either resolves to the real `backend/` or `private_storage/`.
**Named production deviation:** `MODELS_DIR` derives from `STORAGE_DIR`, so the isolated storage
root reaches the real model through a directory *junction* (`mklink /J`). The real
`private_storage/models/` is only ever read and gains no link — the pre-release no-symlink rule
targets that directory, which is untouched.
**Artifact path:** `backend/benchmark_results/t2-durable-job-02082026-jp-start/` (create-only);
dedicated result record `bugs-fixed/059-02082026(SYLC).md`.
**Row order:** `control` first (uninterrupted, observes the control clock) → derive and record the
recovery deadline → `kill` row. The deadline is not chosen after seeing the recovery time.
**Not a repeat:** the seven tests in `test_audio_queue_resume.py` mock `_finalize_group` and seed
`session_id`, so none of them can reach the insert branch, the real beautify, the real cleanup, the
real startup thread, or the real `init_db()` rollback.

**Preregistered pass conditions (all must hold):** R1 Source byte-identical across the kill;
R2 note arrives after relaunch; R3 exactly one session (no duplicate draft); R4 zero orphan queue
rows; R5 zero orphan audio files; R6 recovery inside the preregistered deadline; R7 session status
not auto-set to `complete`; R8 a second relaunch changes nothing (exactly-once).

**Observed control (row ran 2 August 2026, before the kill row was launched):** on
`counselling-31-min` the uninterrupted run reached `structuring` at 96,297 ms and finished at
252,405 ms — **observed structuring wall 156,108 ms**. The run was clean and correct:
`structured: 1`, note 2,965 chars, session left at `draft`, `audio_queue` empty, zero audio files
left on disk. Applying the rule fixed in advance —
**deadline = round(observed structuring wall × 2) + 120,000 ms** — the
**preregistered recovery deadline is 432,216 ms**. It was written here before the kill row started,
so it cannot have been chosen after seeing the recovery time.

#### T2 measured result

The preregistered prediction was **correct**: the first kill row left the Source intact and produced
no note, one orphan queue row, and one orphan audio file. Isolating the cause then required a
second, unpredicted defect to be found.

| Check | `kill/` (no fix) | `kill-fixed/` (fix 1) | `kill-fixed2/` (both) | `kill-cleanup/` (**shipped**) |
| --- | --- | --- | --- | --- |
| R1 Source byte-identical | PASS | PASS | PASS | **PASS** |
| R2 note behaviour | no note (bug) | no note (bug) | note recovered | **no unattended note — by design** |
| R3 no duplicate session | PASS | PASS | PASS | **PASS** |
| R4 no orphan queue row | FAIL | PASS | PASS | **PASS** |
| R5 no orphan audio file | FAIL | PASS | PASS | **PASS** |
| R6 settled/recovered | FAIL | FAIL | 145,077 ms | **2,030 ms** |
| R7 not auto-`complete` | PASS | PASS | PASS | **PASS** |
| R8 second relaunch inert | PASS | PASS | PASS | **PASS** |

**Owner ruling, 2 August 2026 — automatic resume removed.** Once the auto-resume was proven to work
end to end, the owner ruled it should not exist: reopening the app must never kick off an
unattended, uncancellable multi-minute generation. T2's own R1 evidence supports this — the Source
is committed before structuring and survives a hard kill, so the interrupted work is sitting in an
ordinary draft the counsellor can structure whenever they choose (the Home "Unfinished Notes" card
already surfaces it; no new affordance needed). `resume_interrupted_structuring()` became
`cleanup_interrupted_structuring()`: it retires the leftover row and its audio, runs inline, and
starts no model. Because it deliberately does **not** filter on `session_id`, it also retires rows
stranded by earlier builds — **closing the "already-stranded rows" migration question outright**.

- **Defect 1:** the insert branch of `_run_transcription_queue` — the branch a real bulk *upload*
  takes, because `BulkAudioUploadModal` uploads with no `sessionId` — never persisted
  `audio_queue.session_id`, so the row failed the recovery query's `session_id IS NOT NULL` filter
  and was stranded permanently: invisible to `/process` (`pending` only) and refused by `/reset`
  (`failed` only).
- **Defect 2, the load-bearing one:** `_finalize_group` read `_queue_state['running'] == False` as
  "the user pressed Stop", which is exactly the state a freshly started process is in. Every
  resumed beautify was cancelled on its first token, the note discarded, and the queue rows and
  audio deleted anyway. **The `056` §2 recovery path had therefore never produced a note in any
  case, including the merge-branch case it was written for**, while reporting `resumed_groups: 1`.
- Both fixed in `backend/routers/audio_queue.py`; unit cover 7 → 12 tests, each fix separately
  verified to fail without it. `R1` confirms Source-first durability is genuinely sound — the
  transcript survived a hard `taskkill /F /T` byte-for-byte in every run. Defect 1's fix is kept
  even though cleanup no longer needs it: the row must point at the session holding its transcript
  (the frontend restores a recording inline there), and a *stale* `session_id` reaches the same
  branch. Defect 2's `cancel_check` parameter was removed as dead code once no startup caller
  remained, with the trap it documented moved into `_finalize_group`'s docstring.
- **Not evaluated here:** the ≤10 s time-to-free bar. `observation_mode` is `backend_service`, so
  `time_to_free_ms` is an explicit unobserved null — it still needs the §10.4 renderer work.
  Navigation/cancel rows and renderer-held single-session chaining also remain open, as does the
  owner decision on rows already stranded on existing installs (`059` §8).

### [ ] T3 — 135U topology-aware thread and Whisper screen

**Gate:** T1 valid and reliable; correct hardware present.
**New mechanism:** downward/topology-aware tuning on a 2-P-core hybrid U-series CPU. This is not the
closed upward `-t 9/-tb 16` oversubscription test and not the completed non-hybrid IT436365 screen.
**Gemma conditions:** `-t {-1,2,4,6,8}`, `-tb -1` fixed; balanced per-fixture order; minimum screen
before extension. Never lower `-tb`.
**Whisper conditions:** `{2,4,6,8}` threads at production beam/VAD/model settings; balanced order.
**Speed threshold:** candidate must improve median/p90 by at least 10% with no worse tail/noise to
enter the blind quality funnel; otherwise `KILL` without an extended matrix.
**Quality kills:** Gemma thread output gets full blind gate; Whisper gets §3.1. No fleet default is
changed from one machine or from timing alone.

### [x] T4 — Live-transcription boundary reconciliation reopening — REJECTED 2026-08-06 (owner ruling)

**Gate:** T2 reliability gate passed; no recorder/worklet UI before offline survival.
**New mechanism:** 60-second-class VAD cuts with materially larger 3–5 second overlap and/or
neighbour-boundary reconciliation before a boundary is final. This is explicitly not a rerun of
the killed ~1-second timestamp-midpoint stitch.
**Hypothesis:** boundary agreement can eliminate the 12 seam-loss spans while retaining real-time
throughput and a small Stop tail.
**Speed threshold:** full live replay RTF <1.0 on the target machine; projected p90 Stop→final Source
tail ≤60 seconds; no more than 20% of audio may require final re-decode/reconciliation.
**Economic gate (pre-registered by owner ruling 2026-08-05 — absolute AND relative, both required):**
net Stop→durably-saved-draft saving on **IT436365** must be **median ≥90 s AND ≥15%**, with **every
fixture ≥60 s** and no p90 regression; on a **135U/16 GB** the bar is **≥120 s or ≥15%, whichever is
greater**. Net saving = ordinary post-Stop transcription wall − final live-transcription
backlog/tail − post-Stop reconciliation wall − additional heated-Beautify wall. During-session
overlap/bridge cost is **not** subtracted (it precedes Stop; a shortfall surfaces as backlog/tail,
and its non-time cost is gated separately as thermal/responsiveness/in-room fan noise). A 35–45 s
result does not justify the complexity — T4 is a minutes-scale candidate or it is closed.
**Execution plan:** [`TranscribeBeautifyAudioWorkletNode.md`](TranscribeBeautifyAudioWorkletNode.md).
**Transcript kills:** §3.1 across all five fixtures, including zero missing ≥5-word spans, zero
clinically material loss of any length, ≥99% coverage, and no new whole duplicated exchange or
generalising repetition-loop regression.
**Decision:** one critical loss is `KILL`, regardless of moved time.

**RULED 2026-08-06 (owner review, `counselling-51-min`, IT436365): `[x] — REJECTED`.** Four independent
transcript-gate failures found in one fixture, any one of which is disqualifying on its own:
1. **Negation reversal** — "It did help" rendered as "It didn't really help" (and other positive→negative
   flips). Fails §3.1/§5's named `negation` content class directly — the clearest possible instance of
   the gate, independent of the self-harm finding below.
2. **Relocated self-harm/cutting content** — the span flagged in §11.12, moved out of its original
   position during stitching. Fails "at any percentage, at any noise floor" per §5.
3. **Completeness** — a missed speech gap of up to 19 seconds, on top of 335 additional words versus the
   serial baseline for this fixture.
4. **Repetition-loop containment (§4.4's independent gate)** — one chunk repeats "I'm not" approximately
   16 times, the same failure mode already expected from the 2026-08-01 run (5/5 fixtures).

No Phase 0B noise-floor run was needed to rule on this fixture: §5's absolute clinical gate is explicitly
noise-floor-independent, and a negation reversal is not a statistical question. T4 as designed (1 s
overlap, timestamp-trim stitch) is closed. Full reasoning: `TranscribeBeautifyAudioWorkletNode.md` §11
and this file's §11.12. Reopening requires the wider-overlap/bridge-window mechanism (§4.2/§4.3 of the
execution plan) tested as a **new** candidate against these same gates from scratch — not a rerun of
this configuration.

### [ ] T5 — Narrow fixed-prefix warm-start spike

**Gate:** T0 complete; practitioner review may be closed independently. This is now the first
available-machine acceleration experiment because it requires no new hardware and claims output
preservation rather than changed semantics.
**New mechanism:** a minimal system/evidence-prefix-only ping with no real Source and no unrelated
full Beautify completion. This is not the rejected naive warm-up.
**Hypothesis:** the stable prefix can be reused without changing the final numerical path/output.
**Speed threshold:** median long-fixture Source→draft saving ≥15 seconds and ≥5% across at least
three balanced cold/warm pairs, with no p90 regression.
**Quality kill:** final output must be byte-identical for every pair. Any output difference is
`KILL` for this small-effect shortcut rather than escalation to an expensive blind programme.
**Other kills:** any real Source in the warm-up, incorrect cache attribution, extra model restart,
or thermal debt erasing the end-to-end win.

### [x] T6 — Reasoning-off reconsideration

**CLOSED by owner ruling; tested/reconsidered and excluded from the acceleration plan.** Timing
direction on `jp-start` was already measured (`−14.3%` of composed clock), a clean matrix was begun,
and the owner stopped/re-declined the candidate because of remembered output-quality regression.
This plan must not suggest, schedule, or silently reintroduce `reasoning-off`. Reopening requires a
new explicit owner instruction; speed pressure alone is not a reopening mechanism.

### [ ] T7 — Heterogeneous CPU+iGPU acceleration track (workload-first, output-safe)

**Corrected 3 August 2026.** The owner’s written goal in `thoughts/SYLC-CUDA-CPU.md` §3 was to use
CPU and GPU together where that maximises useful work, not merely move Gemma layers to a GPU. The
former plan narrowed this to llama.cpp `-ngl` and missed that goal. `bugs-fixed/061-03082026.md`
records the correction and is the cold-start execution guide.

There is no 135U available. T7 discovery runs on IT436365 and does not wait for borrowed hardware.
A future 135U is product qualification, never a prerequisite for finding a useful mechanism now.

**Marker semantics:** T7a–T7e carry their own markers. The parent is derived: `[-]` while any child
is active and `[x]` only after every child is closed or a track-level decision is recorded.

**Track-wide rulings:**

- Choose the backend by workload: OpenVINO/Vulkan for Whisper, independent MTP-draft placement for
  Gemma, and Vulkan or SYCL only where a specific prefill/draft mechanism needs it. There is no
  permanent “Vulkan-only” ruling.
- A requested flag is never device-placement proof. Retain logs proving selected device, fallback,
  model/runtime versions, and effective placement.
- Every timing claim uses a fresh same-machine control and a composed Stop→draft projection.
  Percentages never transfer from JP-START or hypothetical 135U hardware.
- Output preservation is co-equal with speed. Cache/prefill reuse must be byte-identical; Whisper
  must pass §3.1; MTP must preserve the target/sampling contract and pass deterministic identity
  plus §3.2 whenever production outputs differ.
- Standalone spikes write no production code, change no default, touch no live clinical storage,
  and keep binaries/models outside the production bundle.
- `reasoning-off` is closed by owner ruling and excluded from this track.

#### [x] T7a — llama.cpp partial layer offload / PR #22789

**Decision: STOPPED / NOT THE NEXT ACTION.** Official b9585 `-ngl 18` asserted before serving on two
Intel iGPU generations. IT436365 `-ngl 999` served, but its one smoke request was slower than
`-ngl 0` on both prefill (16.5 vs 44.1 tok/s) and decode (8.1 vs 11.6 tok/s). The balanced matrix
did not run, so those rates are directional, but they are enough to deprioritise this mechanism.

The exact b9585 + PR #22789 source/toolchain preparation under Windows Temp is unbuilt. Do not
resume it: the patch may repair split-input allocation, but `-ngl` remains sequential layer
placement across a dependency chain, not concurrent useful-work division. Do not try adjacent
`-ngl` counts. Reopening requires an official scheduler fix plus independent comparable-hardware
evidence of a material end-to-end win. Full rationale/provenance: `061`; raw result: `060` §8.

<details>
<summary>Historical 2–3 August T7a plan and prepared-build instructions — provenance only; do not execute</summary>

##### Historical T7a plan snapshot — no task marker; do not execute

**Historical state before the 3 August correction:** a narrow patched-scheduler experiment was
prepared and not run. The exact source/toolchain provenance is retained, but `061` now explicitly
cancels the build as the next action. The paragraphs below preserve the former preregistration only;
none of their activation/build/timing instructions remain authorised.

**Official-b9585 T7a.0 smoke qualification RAN 2 August 2026 on IT436365 and FAILED — the timed
matrix never started.** 1 of 3 conditions (`-ngl` ≈half, i.e. `18`) crashed with
`GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS) failed` during compute-graph reservation,
before the server reached "listening" — not an OOM, not a driver rejection; RAM/commit stayed
healthy throughout. `-ngl 0` and `-ngl 999` both loaded and served correctly, but `-ngl 999`'s
single smoke request was markedly slower than `-ngl 0` on both prefill and decode (not a balanced
n=3 measurement). This met the KILL rule's "≥1/3 of runs hitting … failed model load" bar on its
face; §11.3d records the later owner decision to stop the official-binary path. Full record:
`bugs-fixed/060-02082026.md` §8.

**Decision class:** feasibility spike; timing/stability only. Not a ship decision and not a quality
candidate.
**Gate:** an Intel-iGPU machine is physically available AND the spike displaces no scheduled T1/T2
work. On a borrowed machine, T1's minimum decisive row and its copy-back complete first; a window
where T1's practitioner review is outstanding is an acceptable slot. IT436365-class (Iris Xe,
16 GB) is an eligible host precisely because it is the weakest relevant iGPU: it yields a
conservative lower bound, not a fleet answer.
**Hypothesis:** offloading some or all Gemma layers to the Iris Xe via an official prebuilt
llama.cpp Vulkan Windows binary raises prefill throughput materially on production-shaped requests
without regressing decode throughput, on the same pinned model and fixtures.
**Allowed lever:** exactly one — compute backend/`-ngl` (`--n-gpu-layers`: requests layer-granular
GPU offload of N transformer layers with the remainder on CPU — the built-in hybrid split, not
all-or-nothing; exact effective placement and per-operation fallback are determined from the tested
build's retained logs and runtime evidence, never asserted from documentation or memory).
Conditions: production CPU binary control
(bundled b9585, production flags); Vulkan binary at `-ngl 0` (build/version/backend-skew control);
`-ngl` ≈half;
`-ngl 999` (full offload). Everything else pinned at production parity where representable: same
GGUF (hash-verified), context 32768, explicit `-t`/`-tb` fixed to the values the control's startup
log proves production resolves to on that machine (never implicit, never `llama-bench` defaults),
pinned seed, no other new flags. Pass `-ngl` explicitly in every condition, including `0` — never
rely on build defaults, which may differ across llama.cpp versions. Vision/`--mmproj` out of scope
(text-only production path).
**Version-skew confound — RESOLVED 2 August 2026.** The b9585 release **does** ship a Windows Vulkan
build, so the skew can be eliminated rather than merely recorded:

| Asset (llama.cpp release `b9585`) | Size |
| --- | --- |
| **`llama-b9585-bin-win-vulkan-x64.zip`** | **38,405,705 bytes** ← use this |
| `llama-b9585-bin-win-cpu-x64.zip` | 16,722,795 bytes |
| `llama-b9585-bin-win-cuda-12.4-x64.zip` (+ `cudart-…` 391 MB separately) | 260,940,464 bytes |
| `llama-b9585-bin-win-hip-radeon-x64.zip` | 320,918,515 bytes |
| **no SYCL asset exists in this release** | — |

Because the Vulkan binary is the **same tag as the bundled server**, the CPU-vs-Vulkan comparison
isolates the backend instead of confounding it with a newer llama.cpp. `--cache-reuse` is silently
disabled at b9585 (058), and that now holds identically for both arms — one less thing to equalise.
If a future spike is ever forced onto a different tag, the old skew rule applies again.
**Three comparisons, three meanings:** bundled b9585 CPU vs Vulkan `-ngl 0` = build/version/backend
skew only; Vulkan `-ngl 0` vs Vulkan partial/full = the cleanest within-build estimate of the
GPU-offload effect; bundled b9585 CPU vs best Vulkan = the practical product opportunity
(decision-relevant, not mechanism-isolated). Shipping thresholds are evaluated against the bundled
CPU control; any claim about what GPU offload itself achieved must cite the within-build pair.
`-ngl 0` is not assumed to mean zero GPU work: verify from its startup log and GPU-memory evidence
that no offload occurred, and attribute any residual delta versus the bundled CPU binary to
version skew, not to the GPU.
**T7a.0 smoke qualification (must pass before any timed repetition):** the Vulkan device
enumerates; the model loads at `-ngl 0`, ≈half, and `999`; the startup log confirms the actual
backend, device, and offloaded-layer count for each condition; one short production-shaped request
per condition completes without crash, garbage output, truncation, or memory exhaustion; RAM and
commit charge are recorded and stay within the preregistered bound. Any smoke failure stops the
matrix before long runs — record it and rule per the verdict criteria. Only after T7a.0 passes do
the long-fixture balanced repetitions run.
**Fixtures/repetitions:** frozen clock-4 real-audio Sources fed through the existing production
prompt construction so request bytes match production shape; minimum decisive = longest fixture,
n=3 per condition, balanced order, bounded 5-minute stabilisation between condition blocks; extend
to one mid-length fixture only if the longest passes its floor. If partial offload wins the
screen, one bounded refinement pass (≤3 additional `-ngl` values around the winning region,
nothing else varied) may run; no other matrix extension.
**Preregistered thresholds (owner may amend before activation, not after):** verdict `CONTINUE`
requires, on the longest fixture versus the production CPU control: median prefill tok/s ≥1.5×;
median decode tok/s ≥0.95× with no single repetition below 0.90×; median request wall ≥10% faster;
and a composed-clock-(4) projection of ≥60 s saved, computed from the fresh T7a CPU control rows'
own phase shares — never from `LEGACY-INCOMPLETE` data. A decode result inside the measured noise
floor (±5–14% at n=3 on wall clocks; token-rate medians are expected to be tighter but must be
shown, not assumed) is reported as "within noise", not as a pass/fail certainty. If the bars are
missed **without** a generalising mechanism failure, the verdict is `CONTINUE` with an explicit
"Iris-Xe-class excluded as beneficiaries" scope note (Arc stays open on T7b's own evidence).
Verdict `KILL` for the whole track requires a generalising failure — decode collapse consistent
with the shared-bandwidth hypothesis AND prefill gain <1.1×; an output-integrity failure class
inherent to the backend (degenerate/garbage text, systematic truncation); or ≥1/3 of runs hitting
driver crash, failed model load, or shared-memory exhaustion — **and explicit owner ratification**,
because IT436365-class memory configuration is unattested and generalises poorly to the
dual-channel DDR5 fleet machines.
**Quality handling:** outputs hashed and coarsely sanity-checked (finish reason, truncation,
headings present). Output text is not guaranteed byte-identical to CPU output and must be treated
as potentially different; a difference alone is not a spike failure. No blind gate at this stage.
**Reliability kills (spike-scoped):** any write to the repo, the production install, or either
read-only evidence tree; any use of the live clinical DB/storage; a requested-vs-log mismatch
accepted as offload truth.
**Evidence:** preregistration + postflight per §4 to the extent the v1 schema can represent a
standalone-binary run; where it cannot, extend the schema or record the named gap in the manifest —
never silently downgrade. Retain the throwaway binary's own hash, GPU driver version, full startup
log, per-request raw timings, request/response bytes and output hashes under
`backend/benchmark_results/<experiment-id>/`. The throwaway binary itself lives outside the repo.
**RAM note:** offloaded layers are copied into GPU-allocated shared system memory — record
working-set/commit before and during runs. E2B (~2.4 GB) is expected to fit on 16 GB; E4B is out of
spike scope and must be re-checked at T7c.

Before activation, fill per §0.3: exact machine/power/load/thermal attestation, the Vulkan release
tag and binary/DLL hashes, GPU driver version, model/fixture/prompt hashes, the balanced condition
schedule, and the artifact path. T7b re-fills the same fields on the Arc machine before it
activates.

</details>

#### [ ] T7b.0 — whisper.cpp **CPU** split + control (run this before any GPU arm)

**Run once already, jp-start, comparison-only, 2026-08-03 — see §11.8.** Box stays unchecked because
the decision-grade IT436365 repeat is still owed; jp-start's own gate arithmetic leans no (13.8–17.9%
vs the ≥20% bar) but does not decide anything per §11.6 rule 8.

**Corrected 2026-08-03 — see `bugs-fixed/061-03082026.md` §0.1(b), §5.1–5.2.** Two facts reorder this
track:

1. **whisper.cpp v1.9.1 ships no Windows Vulkan and no Windows OpenVINO binary.** Verified against
   the release API; the only Windows x64 assets are CPU (7,982,101 B), CPU+BLAS (20,769,031 B), and
   two CUDA builds. Both GPU arms therefore need a **source build** — the MSYS2/CMake exercise just
   put away for llama.cpp — and OpenVINO additionally needs the OpenVINO toolkit plus a Python
   encoder-IR conversion step. The owner is sceptical of another Vulkan attempt; that scepticism now
   has cost evidence behind it.
2. **OpenVINO offloads the encoder only**, so the encoder's share of transcription is a hard ceiling
   on that arm. That share has never been measured. If the encoder is ~25% of transcription, the
   ceiling is `34.4% × 25% ≈ 8.6%` of the journey — below T7b's own ≥20% gate, and no build is
   justified.

**T7b.0 also supplies the control arm T7b was missing.** Comparing faster-whisper CPU directly against
a whisper.cpp GPU arm changes runtime (CTranslate2 → ggml) *and* device (CPU → iGPU) at once. A
whisper.cpp **CPU** row separates them, and its direction is not assumed — CTranslate2 int8 is well
optimised on x86 and may be the faster CPU runtime, in which case a GPU "win" is only a return to
parity.

**Cost:** `whisper-bin-x64.zip` (8.0 MB) + `ggml-base.bin` (147,951,465 B) or `ggml-base-q5_1.bin`
(59,707,625 B) from `huggingface.co/ggerganov/whisper.cpp`. Temp folder, no build, no repo change.
**Output:** `whisper_print_timings` encode/decode/batchd split, plus a same-machine whisper.cpp CPU
timing row against the fresh faster-whisper control.
**Decision:** if the measured encoder share cannot clear T7b's gate arithmetic, close the GPU arms and
record it. Do not build.

#### [ ] T7b — IT436365 Whisper Intel-iGPU runtime screen — **BLOCKED ON T7b.0**

**Why this was first in the GPU track:** T1 measured transcription at 210.7 seconds, 34.4% of the
611.6-second journey. PRIVATE’s current faster-whisper/CTranslate2 runtime is CPU-only, while the
`whisper.cpp` **source tree** supports OpenVINO encoder offload to Intel GPUs and Vulkan execution.
This is a new runtime mechanism, not the already-killed batched-Whisper algorithm. It is no longer
first: it is gated behind T7b.0, and both arms require source builds.

**Also weigh shipping cost, not only upside.** Integrating OpenVINO means a second inference runtime,
its DLL set, and a converted encoder artifact in the installer — which directly aggravates the known
post-update AV-scan startup delay behind the 1.0.3 licence-screen bug (the 60-second cover fallback in
`CLAUDE.md` exists because of it). T7c and T7d add 57 MiB and zero bytes respectively.

**Host:** IT436365 i5-1135G7/Iris Xe/16 GB, on AC. No 135U gate.
**Conditions:** fresh current faster-whisper CPU/int8 control; standalone whisper.cpp OpenVINO with
logs proving Intel GPU encoder selection; standalone whisper.cpp Vulkan with logs proving Intel GPU
selection. Same frozen audio, closest equivalent base model/quantisation, pinned decode parameters,
minimum n=3 balanced order after smoke. Record the unavoidable runtime/model-format confound.
**Speed gate:** median transcription wall ≥20% lower, no worse p90, and fresh same-machine composed
projection ≥30 seconds saved.
**Quality/reliability kill:** any clinically material missing span; any new ≥5-word missing span;
speaker/negation/medication/number reversal; generalising hallucination/repetition; crash, silent CPU
fallback, or managed-driver failure. Full §3.1 review occurs before a speed winner advances.
**Sources:** official [whisper.cpp OpenVINO documentation](https://github.com/ggml-org/whisper.cpp/blob/master/README.md),
[Intel iGPU Vulkan recognition PR](https://github.com/ggml-org/whisper.cpp/pull/3492), and the exact
i5-1135G7-class directional report in [issue #2542](https://github.com/ggml-org/whisper.cpp/issues/2542)
(motivation only, not a transferable speed claim).

#### [ ] T7c — Gemma 4 E2B MTP: CPU target, tiny CPU/iGPU draft

**Run once already, jp-start, comparison-only, 2026-08-03 — see §11.8.** Box stays unchecked because
the decision-grade IT436365 repeat is still owed; jp-start's numbers are encouraging (CPU-draft ~54.8%
acceptance / +18.0% decode, iGPU-draft ~50.1%/−19.1%) but comparison-only per §11.2. **§11.8 also
records a real telemetry correction:** the acceptance fields this section assumed live in `usage` are
not populated by this build — use `timings.draft_n`/`draft_n_accepted` instead.

**New mechanism:** use Gemma 4’s trained MTP assistant head, not killed n-gram speculation and not
partial layer offload. Upstream support landed in llama.cpp
[#23398](https://github.com/ggml-org/llama.cpp/pull/23398) and
[#24282](https://github.com/ggml-org/llama.cpp/pull/24282); the E2B assistant artifact is about
[59 MB](https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF/blob/main/mtp-gemma-4-E2B-it.gguf).

**Preflight — DONE 2026-08-03, gate PASSED.** Checked against `backend/llama_server/llama-server.exe`
itself (version 9585 / `d73cd0767`): `--spec-type` accepts **`draft-mtp`**, `--spec-draft-model`/`-md`
takes the draft path, and `--spec-draft-device`/`-devd` places the draft independently. All three
required controls exist, so **no llama.cpp upgrade is needed** and the iGPU-draft arm is runnable.
Full evidence: `bugs-fixed/061-03082026.md` §6.1.

**Wiring shipped 2026-08-03 (owner instruction, ahead of measurement).** The draft is downloadable
from Settings (`mtp_filename`/`mtp_url` in `AVAILABLE_MODELS`; E2B 59,235,648 B, E4B 59,678,016 B) and
`ai.py::_find_mtp_draft` is now **active by default whenever the file exists** —
`PRIVATE_AI_ENABLE_MTP` is retired. **`PRIVATE_AI_DISABLE_MTP=1` is the kill switch and is the
"no draft" control arm: never create that arm by moving model files.**

⚠️ **Benchmark contamination guard.** Because MTP is now on by default,
`benchmark_beautify_first_run.py::production_benchmark_environment` pins `PRIVATE_AI_DISABLE_MTP=1`
unless called with `enable_mtp=True`. Any *other* harness that starts llama-server on a machine with
the draft downloaded must do the same, or its rows are not comparable with the MTP-free historical
evidence in §8. Check this before trusting any new timing row produced after 2026-08-03.

Use one exact runtime build for all conditions.
**Conditions:** CPU target/no draft; CPU target+CPU E2B MTP draft; CPU target+Intel-iGPU E2B MTP
draft, with logs proving independent draft placement. Same GGUF, prompt bytes, target settings,
sampling contract, and seed; minimum n=3 balanced after smoke. Record draft proposed/accepted
tokens, acceptance, prefill/decode/request wall, RAM/commit, logs, and response bytes.
**Speed gate:** median Beautify request wall ≥10% lower and composed projection ≥30 seconds saved;
the iGPU-draft arm must beat both controls to justify the backend.
**Output gate:** deterministic spike output byte-identical; if production sampling still differs,
the result is not output-safe until it passes §3.2 blind review. Any critical regression kills the
arm regardless of acceptance or speed.

#### [ ] T7d — Progressive transcript-prefix prefill overlap

**Goal:** create actual useful overlap for one recording. While CPU Whisper emits stable segments, a
**CPU** llama-server evaluates the growing Source prefix. llama-server’s documented `n_predict=0` and
[`cache_prompt`](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) mechanisms
can evaluate a prompt without generation and then only its unseen suffix.
PRIVATE already serialises Source first for prefix reuse (`_data_message()` carries a
"Do not reorder these keys back" warning for exactly this).

**Corrected 2026-08-03 — this needs no GPU, and the old gate was a priority inversion.** The earlier
wording ("an iGPU server evaluates…") and the T7b/T5 prerequisites made this look like the hardest
candidate; it is the cheapest to ship. See `bugs-fixed/061-03082026.md` §7.

**This is not the cache-reuse idea the owner rejected.** Nothing runs twice — Stop once, transcribe
once, Beautify once. Only the *order* changes: the early Source is evaluated while Whisper is still
producing the rest, instead of sitting idle until the full text exists. The prompt cache is plumbing
that stops already-computed work being discarded inside one run, not a bet on a repeat run.

**The idle capacity is already measured:** `bugs-fixed/055-31072026(NewFindings).md` §0.4 —
**Whisper scales 2 → 8 threads by only 1.47–1.65×**, so transcription leaves substantial CPU unused.
What is unmeasured is whether contention erases the gain; that is what the spike answers.

**Why it now ranks above the GPU arms:** largest addressable share (Beautify is 65.6% of T1's i5
journey and prefill is a large fraction of it — *[inferred, unverified: the i5 prefill share itself is
not measured]*); **structurally immune to the transcript-fidelity gate** that killed batched Whisper
and live transcription, because it does not touch transcription; and **zero deployment footprint** —
no new runtime, model, driver, or installer bytes.

**Gate:** none beyond this task's own parity proof. **T5 is folded in and will not run separately**
(its own ceiling was bounded at 12.9–17.1% of prefill once per server lifetime, and prefix reuse is
already live in production). Design/standalone replay only until an explicit owner decision
authorises product code.

**⚠️ Corrected 2026-08-05 — the former byte-identity kill was a false-kill criterion and has been
replaced.** This task previously required the final response to be "byte-identical across three
balanced pairs". That would have killed the candidate on contact for a reason unrelated to its
safety. Chunked prefill resumes from an arbitrary cached position, which shifts ubatch boundaries,
which changes float summation order in the GEMMs, which perturbs KV values in the low bits and can
flip an argmax at a near-tie. **The evidence that this happens already exists**: the naive
warm-start spike recorded `byte_identical_output: false` at only 13.86% of the prompt cached
(`warm-start-spike-01082026-jp-start/RESULT.json`). Byte-identity is therefore not a property this
mechanism can be expected to have, and its absence is not evidence of degradation. This is the same
trap that made the jp-start MTP quality review unattributable (§11.10) — do not re-import it.

**Standalone proof — two-arm identity design, in this order:**

1. **Arm 0, the availability check (run first, it is cheap and it decides the gate).** With
   `PRIVATE_AI_SEED` pinned (`ai.py` already reads it) and temperature 0, run the ordinary
   non-prefetched request **twice, back to back, on the same server and slot**. This establishes
   whether byte-identity is available on this engine at all.
   - *Identical* → byte-identity is a meaningful standard here. Apply it to arm 1 below, and any
     cold-vs-warm difference is a genuine effect of the mechanism.
   - *Different* → byte-identity was never available, is not a valid gate for anything in this plan,
     and arm 1 falls through to the §3.2 blind gate. **Record which of these two outcomes occurred;
     it is a load-bearing fact for T7c and any future A/B, not an incidental detail.**
2. **Arm 1, the mechanism.** Replay growing stable transcript prefixes into one fixed slot; prove
   final prompt bytes exactly equal ordinary production prompt bytes; compare ordinary versus
   progressively prefetched final responses on the same backend; minimum three balanced pairs.
   Judge output by the standard arm 0 established, never by assumption.
3. Measure observed overlapped wall clock and CPU/GPU utilisation, not summed isolated phase
   arithmetic.

**Staging (added 2026-08-05).** Stage A is mechanism-only with no Whisper running: pre-evaluate
0 / 25 / 50 / 80% of one long fixture Source via `n_predict: 0` + `cache_prompt: true`, then issue
the real request, and confirm `prompt_tokens_cached` rises roughly proportionally. The naive
warm-start spike gives the expected slope — 13.86% cached bought 12,962 ms of a 100,137 ms prefill,
i.e. ≈12.9% of prefill, so the relationship is near-linear and an ~80% hit projects to roughly 80 s
off that fixture. Stage B is the contention test and is the real question: transcription alone
versus transcription with concurrent progressive prefill, measuring **both** the transcription wall
(did Whisper slow down?) and the prefill remaining at Beautify time. Net saving = prefill saved −
transcription slowdown. Do not run Stage B until Stage A passes.

**Simpler fallback if Stage B shows contention eats the gain:** prefill during the post-Stop idle
window while the counsellor reads and edits the Source, rather than concurrently with Whisper. Zero
contention risk, cannot make anything slower, wins nothing if the counsellor clicks Beautify
immediately, and does not help the All-at-Once chain (which has no idle window). Cheaper to build
than the concurrent design and worth costing before abandoning the task.

**Stage B completed 2026-08-05 on JP-START.** The handoff-prescribed `counselling-45-min.mp3`
(`7d863bf1ed116a0e40049dda75a227d9a00e3db10162368a5cfb5aa139d454e8`) ran through two
counterbalanced ordinary/concurrent pairs. Prefix prefill worked and saved **86.8 s** of final
prompt work on average, but it slowed Whisper by **93.9 s** (+57.7%); net prompt-vs-Whisper
arithmetic was **−7.1 s**. The four live Sources were not byte-identical, including the two ordinary
controls, so concurrent Source integrity is not attributable and the product gate does not clear.
Do not claim a concurrent T7d product speedup. Full evidence is in
`benchmark-reports/JP-START-i7-T7d-StageB-45min-20260805.md`; the 49- and 51-minute recordings
remain optional and are not required for this minimum finding.
**Kill:** final **prompt** bytes not exactly equal to the ordinary production prompt bytes, cache
reset, transcript revision invalidating the prefix, Whisper content/timing regression, or composed
saving <30 seconds. **Output** difference is judged by the standard arm 0 establishes, never treated
as an automatic kill — see the corrected standalone proof above.

**Known constraints to design around, not discover mid-run:** (a) the counsellor can edit the Source
before pressing Beautify, and an edit at position *k* invalidates the cache from *k* onward —
`--cache-reuse` is silently disabled in the bundled b9585 (`061`, i5-runner finding), so only exact
prefix reuse is available and there is no gap-tolerant recovery; (b) the server runs `-np 1`, so the
prefetch and the real request share one slot — this is *required* for the cache hit, but a prefetch
in flight when the counsellor clicks Beautify makes the real request queue behind it, so bound the
chunk size; (c) `_data_message()` (`services/ai.py`) already serialises `{"source", "data", "task"}`
with Source first and carries a "Do not reorder these keys back" warning — that ordering is the
precondition for this entire mechanism and must not be changed.

#### [ ] T7e — Product integration and validated fallback

**Gate:** at least one of T7b/T7c/T7d passes speed, output, reliability, and composed-journey gates;
explicit owner sign-off; then a separate implementation preregistration. Timing alone never opens it.

The shipped policy is workload-specific and allowlisted, not “any GPU found”: verified runtime/device
classes get only the role they passed; unknown/failed devices stay on current CPU. Record the chosen
runtime/backend per phase, retain force-CPU support control, and retry an entire failed phase rather
than switching computation midway. Integration must address binaries/models, installer footprint,
licensing, driver/runtime compatibility, startup and mid-run fallback, memory pressure, signing,
activity logging, and the full transcript/generated-note gates. `backend/database.py` remains out of
scope unless a later explicit design proves otherwise.

---

## 7. Closed-work ledger — do not repeat

| Candidate/mechanism | Decision | Reopening requirement |
| --- | --- | --- |
| Forced Flash Attention `on`, bundled b9585 CPU | `KILL` / keep `auto` | Different runtime/backend with effective kernel attested |
| Physical `-ub 2048` | `KILL` | Materially different implementation with a new output hypothesis |
| Reasoning budget `1024` | `KILL` | Different model/runtime where the budget demonstrably binds |
| `-t 9/-tb 16` | `KILL` | None; T3 is a distinct downward hybrid-topology experiment |
| N-gram speculation | `KILL` | Do not retune; real MTP is a different gated candidate |
| Batched Whisper as final Source | `KILL` | New algorithm that restores omitted speech, not batch/chunk tuning |
| Deterministic prepared+labelled Source as speed work | `KILL` | Quality initiative only; Phase 0 token test is not rerun |
| Live 60 s/~1 s timestamp-midpoint stitch | `KILL` | T4’s larger-overlap/boundary-agreement mechanism |
| T4 — live-transcription boundary reconciliation (Phase 0A config) | **`KILL` — owner ruling 2026-08-06** | New mechanism only (§4.2/§4.3 overlap-sweep/bridge-window), tested from scratch against §5's full gate set; not a rerun of Phase 0A |
| Naive unrelated full-request warm-up | `KILL` as output-neutral | T5’s system-prefix-only mechanism |
| IT436365 `-t {-1,4,6}` | complete/no lever | Hybrid 135U T3 only |
| Beam 1 | owner-declined, unmeasured | Explicit product decision for a labelled nonfinal tier |
| Reasoning-off | **CLOSED by owner ruling after testing/reconsideration** | Do not suggest or schedule; only a new explicit owner instruction can reopen it |
| T7a — Vulkan partial Gemma layer offload / PR #22789 | **STOPPED 2026-08-03; prepared patch remains unbuilt** | `-ngl` is layer placement, not concurrent useful-work scheduling; reopen only for an official fix plus independent comparable-iGPU end-to-end speed evidence — see §11.3d and `061` |
| T7d **concurrent** prefill during Whisper | **KILL 2026-08-05 on two machines** (net −7.7 s i5, −7.1 s i7) | None for the concurrent shape. The post-Stop **idle** variant is a separate product-gated question, not a rerun — see §11.11.6 |
| T5 fixed-prefix warm-start | **effectively answered, not formally run** — T7d Stage A's 0% row measured the identical prefix at **12.86 s** on jp-start, below T5's own ≥15 s gate | Only on IT436365, and only if §11.11.3 step 1 returns deterministic — its kill criterion is byte-identity, which jp-start no longer offers |

Also prohibited: treating `/props` as thread/speculation truth, using implicit `llama-bench`
threads, transferring percentages between machines, quoting the 711-second composite, or calling a
sum of separately measured cold spans an observed end-to-end journey.

---

## 8. Generated evidence registry

| ID | Task | Machine | Artifact | Contract verdict | Decision | State |
| --- | --- | --- | --- | --- | --- | --- |
| HIST-056-IT-WHISPER | IT436365 Whisper 5-fixture timing | IT436365, i5-1135G7/16 GB | read-only sibling `whisper_threads_it436365-dell-class_20260801T*.{json,csv}` | 5/5 `LEGACY-INCOMPLETE`; 0 errors | measured baseline only | historical |
| HIST-056-IT-BEAUTIFY | IT436365 12-row Beautify baseline | IT436365, i5-1135G7/16 GB | read-only sibling `it436365-baseline-01082026/beautify_first_run_20260801_165333/` | `LEGACY-INCOMPLETE`; 0 errors | measured baseline only | historical |
| HIST-056-IT-THREADS | IT436365 thread screen | IT436365, i5-1135G7/16 GB | read-only sibling `it436365-thread-sweep-01082026/` | 3/3 `LEGACY-INCOMPLETE`; 0 errors | no useful lever | historical |
| HIST-056-LIVE-1S | live slice replay, ~1 s overlap | JP-START | read-only sibling `live-slice-replay-01082026-jp-start/` | legacy | `KILL` | closed |
| HIST-056-WARM-NAIVE | unrelated full-request warm-up | JP-START | read-only sibling `warm-start-spike-01082026-jp-start/` | legacy | `KILL` as output-neutral | closed |
| T0-20260801 | evidence contract + legacy audit | JP-START | `backend/benchmark_results/evidence-contract-01082026-jp-start/tooling-v1-final/` | `VALID`; 9/9 legacy subjects separately `LEGACY-INCOMPLETE` | tooling `SHIP`; initiative `CONTINUE` | COMPLETE |
| T1P-20260802 | borrowed-i5 journey runner + contract extensions | JP-START, no evidence run | commits `6982cdc`, `03e0121`; 136 tests | N/A — tooling | tooling `SHIP`; T1 unblocked | COMPLETE |
| T2-20260802 | durable-job force-kill/relaunch verification | JP-START | `backend/benchmark_results/t2-durable-job-02082026-jp-start/` (`control/`, `kill/`, `kill-fixed/`, `kill-fixed2/`, `kill-cleanup/`) | 8/8 assertions PASS on the shipped `kill-cleanup` run; queue settles 2,030 ms, no unattended note in a 300 s watch | 2 defects found by real kill; auto-resume then removed by owner ruling; `SHIP` | COMPLETE |
| LOG-20260802-FLEET | support-log machine attribution + first real i5 Beautify figures | JP-START `577c4552e305`, IT436365 `2053ad7321d1` | `support-logs/private-diagnostic-log-2026-07-{25,25-new,26,27,28,29}.json` (read-only analysis) | descriptive production evidence; **not** contract-valid (no attestation, no pinned hashes) | machine identity resolved; numbers corroborate the 1.7–2.3× gap (`059` §10) | COMPLETE |

Every completed phase appends a row; historical rows are never overwritten.

---

## 9. Next activation rule

> **See §11 for the current handover.** This section is the formal activation rule; §11 and `061`
> state the current order and full zero-production-code protocols.

**Updated 3 August 2026 after the CPU+iGPU objective correction.** T0, T1P, T1, T2 and T2-i5 have
run; T1 still needs practitioner review/`apply-review` to become VALID. There is no 135U available,
so no active task may wait for it. Follow this order on the hardware actually available:

1. Complete T1 practitioner review/`apply-review` when the reviewer is available; it does not
   consume an acceleration benchmark window.
2. ~~Run T5’s narrow fixed-prefix-only cache test.~~ **Folded into T7d 2026-08-03; will not run
   separately** — see §11.7 and `bugs-fixed/061-03082026.md` §0.1/§4.
3. Run **T7b.0** on IT436365 first: standalone whisper.cpp **CPU** for the encoder/decoder split and a
   same-runtime control. 8 MB, no build. The GPU arms (OpenVINO, Vulkan) have **no Windows prebuilt**
   and stay blocked until that split justifies a source build. Apply §3.1 before interpreting any
   speed win.
4. Run T7c’s Gemma E2B MTP matrix — runtime `--help` **already proved** independent draft-device
   support on the bundled b9585: `PRIVATE_AI_DISABLE_MTP=1` (no draft), CPU draft, iGPU draft.
5. Run T7d progressive prefill on **CPU** — no GPU or T5 prerequisite. Standalone/design-only;
   production integration requires separate owner approval.
6. T7a partial layer offload is closed. Do not compile PR #22789, run `-ngl 18`, sweep adjacent
   layer counts, or use `-ngl 999` on IT436365 as a production candidate.
7. T4 and §10.4 remain independent product/reliability work. They do not replace the acceleration
   order above.

`reasoning-off` is closed by owner ruling and excluded from this activation list.

The overall initiative remains active after T0, T1, or any single later success.

---

## 10. Immediate handover — exact work required before any borrowed-i5 test

> **SUPERSEDED 2 August 2026 by §11.** Most of this section is done: T1P built the runner
> (§10.2/§10.3), and `bugs-fixed/058` §5 records what was deliberately not done. **§10.4 (the
> renderer-instrumented journey) is the one item still genuinely open** and is carried forward in
> §11.7. Read §11 for the current position; this section is retained for its preregistration record
> and because §10.4/§10.5 still describe real outstanding work.

**Recorded:** 1 August 2026.  
**Scope of this note:** handover only. It does not authorise a JP-START model run, an i5 run, a
production-default change, a merge, or a push.

### 10.1 Stop-state: the new i5 test path is not ready

Do **not** copy the current dirty working tree to the i5 and do **not** begin T1 yet. The application
performance path has not been changed, and there is no new speed candidate to measure. T1P is an
unfinished measurement-package task.

Exact repository state at handover:

- branch `prompt-improve`, two local commits ahead of `origin/prompt-improve`;
- `c4452e70e32684e17db0464b694863e67c60f648` is the completed T0 evidence-contract commit;
- `6317928` activates T1P in this plan;
- uncommitted work exists only in `backend/tests-benchmarks/benchmark_evidence.py` and
  `backend/tests-benchmarks/benchmark_evidence_bundle.py`: 575 insertions/2 deletions at handover;
- there is no completed `benchmark_i5_journey.py`, no i5 execution command, no handoff package and
  no untracked runner/test file;
- the 154-test T0 suite passed at the T0 checkpoint. A 67-test evidence subset passed during the
  partial T1P edit, but more validator code was added afterward. The present dirty tree has **not**
  received a post-edit test run and must be treated as unverified;
- no Whisper, Gemma/llama-server, audio, Transcribe & Beautify or product-speed run was performed on
  JP-START for T1P. Product speed effect remains 0 seconds/0% and no product output was generated.

The next implementer must preserve these partial edits until they have reviewed the diff. Do not
silently discard, commit, or describe them as complete.

### 10.2 P0 — finish or deliberately replace the partial evidence changes

These two dirty files are the first code-review boundary:

1. `backend/tests-benchmarks/benchmark_evidence.py`
   - The partial work adds journey row bindings for prompt/template/runtime hashes, opaque quality
     case IDs, transcript-diff identities, job-event identities, strict scorecards, blind-scorecard
     linkage, derived journey clocks, orphan-artifact rejection and a read-only preregistration
     validator.
   - It is incomplete until a valid one-row journey fixture and negative tests exist. Review for
     schema consistency, duplicate file reads, issue-code stability, malformed/unhashable JSON,
     Windows path handling and compatibility with the completed T0 tooling bundle.
   - Correct the preflight model: the newly generated Source hash cannot be known before
     transcription. Preregister the frozen **reference transcript** separately; capture the newly
     generated Source as post-run evidence. The T1P wording at §6 lines describing an unfilled
     pre-run Source hash is superseded by this correction.
   - Add a `transcript_reference` input/binding, or document and test an equally explicit reference
     mechanism. `transcript_diff` must bind the reference hash, audio hash, generated transcript
     hash, run ID and case ID.
2. `backend/tests-benchmarks/benchmark_evidence_bundle.py`
   - The partial work makes `write_preregistration()` call the read-only preflight before it creates
     a bundle. Finish tests proving invalid specs create no directory, valid specs remain
     create-only, input mutation fails closed and an invalid final bundle is retained for diagnosis.
3. Tests that must be added or extended before accepting either file:
   - `backend/tests/test_benchmark_evidence.py`: first complete `ValidJourneyBundleFixture`; prompt,
     template, reference, runtime, diff, event, scorecard, blind-key, clock, artifact-role and blank
     Source mutation cases;
   - `backend/tests/test_benchmark_evidence_bundle.py`: preregistration preflight/create-only cases;
   - rerun the complete T0 suite plus the new journey suite with `python -u`.

Keep this hardening journey-specific where possible. Do not expand unrelated contract machinery
unless a failing one-row T1 requirement demonstrates the need.

### 10.3 P0 — implement the missing one-row i5 runner

Create and test:

- `backend/tests-benchmarks/benchmark_i5_journey.py`;
- `backend/tests/test_benchmark_i5_journey.py`.

The CLI must have a narrow, irreversible-by-accident workflow:

1. `template` writes one new configuration template and never overwrites;
2. `prepare` performs a **no-model** preflight, attests the actual i5, hashes every input, creates an
   immutable one-row/cold/production-control spec and prints both its SHA-256 and the literal marker
   `READY — NO MODEL STARTED`;
3. `execute` accepts only that exact spec hash and an explicit
   `--confirm-one-cold-production-row`; it exposes no `--mode all`, repetition count, thread sweep or
   extended matrix;
4. `finalize` copies raw outputs create-only, rehashes all inputs, constructs the row/artifact table,
   validates the bundle, and writes a separate create-only validation report outside the bundle;
5. a model-free `self-test` creates one inert synthetic journey bundle and independently obtains
   `VALID` without importing or spawning Whisper, llama-server, the app or live storage.

`prepare` must fail before model import/start on placeholders, the wrong branch/commit, a dirty
checkout, ineligible machine identity/topology, battery/power-plan/load mismatch, missing RAM/disk,
missing or changed hashes, reused output paths, live clinical DB/storage, or any path under the
read-only sibling evidence tree. Force AI debug off for this workflow. Do not copy `backend/env`
between machines; the i5 uses its own rebuilt project venv.

### 10.4 P0 — measure the real renderer-orchestrated journey, not two summed scripts

T1 requires the actual user journey in `src/pages/SessionsPage.tsx`:

- `runTranscribeAndStructure()` at the pending-recording path;
- `transcribeBlob()` and its confirmed `updateSession()` Source commit;
- `runStructureAfterTranscribe()`;
- `beautify()` and its confirmed durable draft save.

Do not wrap `benchmark_whisper_threads.py` plus `benchmark_beautify_first_run.py` and call their sum
an observed Stop→draft journey. Those scripts may still provide component timings, but they do not
observe renderer visibility, navigation freedom or the final durable save.

Before T1, implement one default-off benchmark observation mechanism for the real path. The
recommended minimal file boundary is:

- `src/pages/SessionsPage.tsx`: emit benchmark-only events for action/Stop origin, Source committed,
  first draft text visibly rendered, durable draft save confirmed and user/navigation released;
- `electron/preload.js` and `electron/main.js`, or an external UI driver: capture those events in a
  create-only local artifact without exposing a production-default writer;
- `src/utils/api.ts`, `backend/routers/transcribe.py` and `backend/routers/sessions.py` only if exact
  backend stage/token evidence is not already available to the runner. Any added field/hook must be
  disabled by default and covered by tests.

Define `time_to_free` before implementation as the first timestamp at which the user can perform
the named navigation/action without cancelling or corrupting the running job. A backend response or
first streamed token is not “first visible text,” and a backend-only wrapper cannot claim UI
`time_to_free`.

The bound `job_events.json` must contain exactly one event for the origin, Source commit, first
visible text, durable draft and user-free point. Derive all five row clocks from those events; bind
the Source hash to the Source event and final-note/DOCX hashes to the durable-save event.

### 10.5 P0 — capture truthful complete runtime evidence

The existing runtime evidence is not yet sufficient for T1:

- `backend/services/ai.py` keeps only a 200-line `_ENGINE._tail`; do not call that a complete startup
  log. Add a default-off benchmark capture or launch wrapper that preserves the complete server log
  without changing the production default;
- `backend/tests-benchmarks/benchmark_common.py::parse_server_startup_log()` currently proves threads, batch threads,
  CPU/device memory and speculation only. Extend and test it for the T1-required effective context,
  batch/ubatch, KV, Flash, reasoning, model/tokenizer/server binary, backend/model allocation and
  server version fields that are actually present in the retained raw log;
- the adapter may append exactly one
  `PRIVATE_EVIDENCE_RESOLVED_RUNTIME_JSON:` sentinel only after parsing the retained real log. It may
  not copy requested values into “resolved” fields when the log did not prove them.

Whisper production truth must come from the actual call sites, not stale prose: base model,
CPU/int8, 8 threads, beam 2, VAD on and no word timestamps as of this handover. Reattest this on the
i5; do not hard-code it as eternal truth.

### 10.6 P0 — freeze the exact borrowed-i5 inputs and isolated environment

Minimum one-row fixture pins already known:

- recorded-synthetic audio `counselling-45-min.mp3`: 62,641,987 bytes, SHA-256
  `7d863bf1ed116a0e40049dda75a227d9a00e3db10162368a5cfb5aa139d454e8`;
- frozen JP-START reference transcript
  `clock4-baseline-31072026-jp-start/sources_8t/counselling-45-min.source.txt`: 41,104 bytes,
  SHA-256 `36ac11ccbdb2829da1c9a9940629ceafea24a5f6c46b5263570df1dc56d2fe12`.

The reference currently resides in the read-only sibling evidence tree. Copy it create-only into
the handoff materials and verify the copy hash; never alter or move the original. Fill on the i5:
exact audio/reference/template/prompt/model/tokenizer/Whisper model/runtime/llama-server/DLL and
dependency paths, sizes and hashes; exact machine/power/load/thermal fields; fresh quality case ID
and blind-key custody; new isolated benchmark DB/storage paths. Do not point debug, DB, storage or
new result output at `C:\Users\wooin\Documents\private-test-debugs\benchmark_results`.

### 10.7 P0 — finish transfer, commands and documentation

Because pushing is prohibited, create the handoff only after a clean, tested implementation commit:

- create an offline Git bundle containing the exact `prompt-improve` package commit;
- record its SHA-256/bytes and clone it into a fresh directory on the i5; never overwrite an unknown
  or dirty checkout;
- provide an exact `python -u` prepare/execute/finalize/validate command block;
- copy results back rather than moving them, with a tree manifest of relative path/bytes/SHA-256;
- preserve the source-machine external validation report. Do not claim destination revalidation if
  absolute input paths no longer resolve identically.

Update these files additively before handoff:

- `.claude/commands/BenchmarkCommands.md`: replace the current “package pending” gate with the exact
  one-row commands; explicitly forbid its generic sibling-debug/move/push instructions for T1;
- `.claude/commands/LocalAIStack.md`: correct the stale beam-5/word-timestamps production claim;
- `thoughts/AfterSolMaxAndFable.md`: add a supersession note for the old “partial validator” and
  “056 commands ready” claims;
- `bugs-fixed/056-01082026(NewFindings).md`: add a supersession note that its old command block is
  legacy-only and its fixtures are recorded-synthetic;
- `CLAUDE.md`: point to the exact clean package commit and one-row gate;
- `bugs-fixed/058-01082026(NewFindings).md`: create only after T1P has measured offline package
  results, raw hashes, tests and a decision.

### 10.8 Gate that changes T1 from `[ ]` to `[-]`

Do not activate or run T1 until every item below is true:

- the working tree is clean on a named local package commit and no push occurred;
- the two partial evidence files are completed and their new journey tests pass;
- the narrow runner exists, self-test independently returns `VALID`, and prepare proves no model
  started;
- the real renderer journey emits bound Source/visibility/durable-save/user-free events;
- complete runtime logs and requested-vs-resolved attestation pass;
- exact i5 input/machine/power/load/thermal/isolation fields and fresh quality case/custody are
  preregistered;
- handoff bundle/hash/clone verification succeeds on the i5;
- only one cold recorded-synthetic 45-minute-class production-control row is scheduled.

If any gate fails, retain the artifact and stop. Do not fall back to the old `056` commands, do not
sum two component benchmarks into a journey, and do not open a thread sweep or extended matrix.

---

## 11. Handover — start here next session

**Written 2 August 2026; corrected 3 August after the owner’s CPU+iGPU objective was re-read.** This
section is the entry point. It is written to be read cold. Where it conflicts with §10 or the
historical T7a procedures in §11.3b/c, **this corrected section and `061` win**.

### 11.1 Where things actually stand

| | |
| --- | --- |
| Branch | `prompt-improve` only. Never merge to `main`. Never push without explicit instruction. |
| Production defaults | **Unchanged.** No prompt, model, engine flag, thread value, schema or frontend file has been altered by this initiative. |
| Complete | **T0** (evidence contract), **T1P** (i5 journey runner), **T1** (composed journey on IT436365 — PENDING-REVIEW), **T2** (durable-job force-kill/relaunch, JP-START), **T2-i5** (T2 confirmation on IT436365 — 8/8 PASS), **T7b.0** (whisper.cpp CPU split, jp-start — **comparison-only**, gate does not clear at 13.8–17.9%), **T7c** (MTP draft acceptance, jp-start — **comparison-only**, CPU-draft ~54.8% acceptance/+18.0% decode, iGPU-draft ~50.1%/−19.1%). See §11.8. |
| **Stopped** | **T7a partial Gemma layer offload and the prepared PR #22789 build are stopped.** The toolchain/source preparation is provenance only; compilation/testing must not be resumed from the old instructions (§11.3d, `061`). `reasoning-off` is also closed by owner ruling. |
| Next on available hardware | **⚠️ UPDATED 2026-08-05 — go to §11.11, which is now the live order.** T7b.0 + T7c are **complete on IT436365** (§11.9) and the whisper.cpp GPU arms are **closed** (gate not cleared). The next action is the **free determinism check on the IT436365 seeded bundle** (§11.11.3 step 1), then the rescoped practitioner review, then the two real-application rows, then T7d. §11.7's numbered list is superseded. |
| Not available / not blocking | No 135U is available. T3/future 135U product qualification stays open but must not block IT436365 discovery. T4, T7d/e and §10.4 retain their own gates. |

**T2's outcome, in one line:** killing a real backend mid-structuring proved the `056` crash-recovery
path had *never* produced a note (two defects, §6 T2); both were fixed, and then the owner ruled that
**automatic resume should not exist** — reopening the app must never start an unattended
multi-minute generation. Startup now retires the leftover recording and runs no model
(2,030 ms, versus 145,077 ms of unattended model work). The Source is durable, so the counsellor
simply opens the draft and presses Beautify. Record: `bugs-fixed/059-02082026(SYLC).md`.

**T1's outcome, in one line:** the real composed Stop→durable-draft journey on IT436365 measured
**611.6 s (≈10.2 min)** cold on a real 43.5-minute recording — transcription 210.7 s (34.4%),
Beautify 401.0 s (65.6%) — the first time this laptop's transcription phase has ever been captured
in a completed row. Getting there required fixing two real bugs in the T1 runner itself (a
`WindowsPath` JSON-serialization crash that hit *after* the expensive work completed, and a
structural artifact-closure gap that would have failed every future T1 run on any machine), plus
redoing one row honestly after the operator skipped the real thermal-idle wait the first time.
Bundle verdict is **PENDING-REVIEW** — VALID needs a practitioner transcript/note review via
`apply-review`, not yet performed. Record: `bugs-fixed/060-02082026.md`.

**T2-i5's outcome, in one line:** T2 confirmation (`059` §9) run immediately after T1, same
session — `control` then `kill` on `counselling-31-min.mp3`, **all eight assertions true, exit
code 0**. Confirms the owner-ruled retire-on-reopen behaviour (§4 above) holds on the real
weak-tier laptop, not just JP-START; correctness only, no new timing claim. Record: `060` §6.

**T7a's outcome, in one line:** the T7a.0 smoke qualification ran on IT436365 immediately after
T2-i5 and **failed** — `-ngl` ≈half (`18`) crashed with a hard ggml scheduler assertion
(`GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)`) during graph reservation, before the server
ever reached "listening"; `-ngl 0` and `-ngl 999` both loaded and served correctly, but `-ngl 999`'s
one smoke request was markedly slower than `-ngl 0` on both prefill and decode (single-request
signal, not the balanced n=3 standard). Per §11.3b/§6 T7a, any smoke failure stops the matrix before
timed repetitions — **the balanced comparison never ran.** The failure meets the KILL rule's "≥1/3
of runs hitting … failed model load" bar on its face, but that rule requires **explicit owner
ratification** before a formal KILL verdict is declared. §11.3d later recorded the owner's practical
stop decision without re-litigating that narrower formal scope. Record: `060` §8.

**T7a patched follow-up correction, 3 August:** exact b9585 source plus PR #22789 and a temp-only
UCRT64/Vulkan stack were prepared, source-matched, and never built. **Do not resume it.** Repairing
the scheduler assertion would not turn `-ngl` layer placement into concurrent CPU+iGPU work, while
the working full-iGPU endpoint was already slower in both measured phases. `061` is now the stop and
reprioritisation record, not a build-resume manual.

**§11.3c's JP-START reproduction check ran 2026-08-02, same day, and confirmed the crash
generalises.** The identical `GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)` assertion, at the
identical `-ngl 18` split point, reproduced byte-for-byte on JP-START's Intel iGPU — a different
Intel generation and a materially newer driver (`32.0.101.7076`) than IT436365's Iris Xe
(`32.0.101.6556`). `-ngl 0` and `-ngl 999` were both clean there too. This is evidence *against* an
Iris-Xe- or single-driver-specific explanation and *for* a ggml-scheduler/model-architecture
mechanism. It was not a decision on its own and not a T7a speed run; it supports §11.3d’s closure.
Record: `060` §8.7.

### 11.2 Machine roster — three machines, never merge their numbers

| Machine | Spec | Role | `device_fp_hash` |
| --- | --- | --- | --- |
| **JP-START** | Core 7 240H, 6P+4E (10c/16t), 2×16 GB DDR5-5600, RTX 4050 + Intel iGPU | **Comparison only.** A win here never demonstrates the product target. | `577c4552e305` |
| **IT436365** | i5-1135G7 (4c/8t, no P/E split), **16 GB**, Iris Xe, UoA-managed | **Conservative weak-tier floor.** The owner's second laptop; available. | `2053ad7321d1` |
| **Core Ultra 5 135U / 16 GB** | 2P+8E+2LPE, Arc iGPU | **Future fleet qualification only; currently unavailable. Do not wait for it.** | — |

The 135U remains necessary before changing a fleet-wide hybrid-thread default. It is not available
and is not a blocker for T5/T7b/T7c mechanism discovery on IT436365. A passing IT436365 run does not
qualify the 135U class; it only determines whether a mechanism is worth later qualification.

**First real IT436365 production numbers** (from Support Diagnostic Logs, `059` §10 — descriptive
evidence, *not* contract-valid): Beautify on the same ~41.5k-char Source costs **9.59 min cold**
there versus **4.15 min** on JP-START — **2.31×**, consistent with the documented 1.7–2.3× gap. On
the i5 a warm server ran the identical 12,327-token prompt in **3.95 min vs 7.81 min cold** (n=1
warm — a hypothesis worth designing a test around, not a result).

**T1's contract-shaped number (2 August 2026, `060`):** the first real composed Stop→durable-draft
journey on IT436365 — cold, real 43.5-min recording, attested machine/git/power state — measured
**611.6 s (≈10.2 min)**: transcription 210.7 s (34.4%), Beautify 401.0 s (65.6%). This corroborates
(does not replace) the descriptive Beautify-only figure above. Bundle verdict is **PENDING-REVIEW**,
not yet VALID — cite it as "measured, review outstanding."

### 11.2b Why T1 is still required, given the support-log numbers

A fair challenge was raised: the logs already show what Beautify costs on the i5, so why run T1?

**What the logs genuinely settled:** the magnitude of *one phase* on the weak tier
(Beautify ≈9.6 min cold on a 45-minute-class Source). That is real and it does reduce uncertainty.

**What they cannot supply, and T1 does:**

| Missing | Why it matters |
| --- | --- |
| The composed **Stop→durably-saved-draft** journey (clock 4) | The governing product metric. Beautify is only part of it, and **the i5's transcription time is entirely unmeasured** — both its transcription rows are `cancelled` |
| The **phase split** on the i5 | See below — this is the one that blocks the GPU decision |
| Runtime attestation | No proof of what threads/context/reasoning actually resolved for those rows |
| Fixture pinning | We know `input_chars`, not which audio, at what hashes |
| Any quality evidence | No transcript or note review at all. Speed without quality decides nothing |

**The sharpest reason, and it is the one that matters right now: T1 is the denominator for the
Vulkan decision.** GPU offload can only attack Beautify *prefill*. Without the i5's own phase split,
a T7a result cannot be converted into "this saves the counsellor N minutes" — §6 T7's Amdahl guard
forbids stating a saving against Beautify alone. So T1 is not ceremony ahead of the interesting
work; it is what makes the interesting work interpretable.

**Cost:** roughly 15–20 minutes of run time for the single cold row (estimate: i5 transcription of a
45-minute file ≈2× JP-START, plus ≈10 min cold Beautify), plus setup.

**If the owner prefers to reorder** and run the Vulkan spike first because it is more interesting,
that is a legitimate call — the stated cost is that a good T7a number stays uninterpretable as a
product claim until T1 exists.

### 11.3 The next action, exactly

**T1 and T2-i5 are complete (2 August 2026) — see `bugs-fixed/060-02082026.md`.** The procedure below
is retained only as the record of what ran. The actual next order is:

1. practitioner review of T1’s transcript/note bundle plus `apply-review` when the reviewer is
   available;
2. T5 fixed-prefix-only cache identity test on IT436365;
3. T7b standalone faster-whisper CPU vs whisper.cpp OpenVINO vs Vulkan on IT436365;
4. T7c Gemma E2B MTP no-draft/CPU-draft/iGPU-draft, if preflight proves the controls exist.

Do **not** compile PR #22789 and do not run `-ngl 18`; §11.3b/c are historical evidence only.

#### Preconditions on IT436365 — check these BEFORE anything else

Verified 2 August 2026 by inspecting what `prepare` actually requires. Two of these are things git
cannot carry, so they are the realistic failure points:

1. **The venv.** `backend/env` is per-machine and must never be copied between laptops. Rebuild it
   on the i5 (`BUILD.md` §Development):
   `py -3.12 -m venv backend\env` then
   `backend\env\Scripts\pip install -r backend/requirements.txt`.
2. **The audio fixture.** `private_storage/` is **gitignored**, so `counselling-45-min.mp3` does not
   travel with the repo. IT436365 has its own copy of the same recordings — **verify the hash, do
   not assume**: expect **62,641,987 bytes**, SHA-256
   `7d863bf1ed116a0e40049dda75a227d9a00e3db10162368a5cfb5aa139d454e8`. A mismatch means a different
   recording; stop, or re-preregister against the file actually present and say so.
3. **The reference transcript** — now solved. `prepare` requires `reference_transcript_path` and
   resolves it `strict=True`, and it previously lived only in the read-only sibling evidence tree,
   which is **not** on the i5. A create-only verified copy is now committed at
   **`benchmark-handoff/counselling-45-min.source.txt`** (41,104 bytes, SHA-256
   `36ac11ccbdb2829da1c9a9940629ceafea24a5f6c46b5263570df1dc56d2fe12`). Point the config at that
   path. See `benchmark-handoff/README.md`.
4. **The model and Whisper weights** must be present with **unchanged filenames**. IT436365 ran
   Beautify in late July, so it has them.
5. **Clean tree** on `prompt-improve` at the pulled commit. `prepare` refuses a dirty checkout by
   design — do not work around it.
6. AC power, battery ≥95%, Windows Balanced plan, office-idle, ~5 minutes idle before `execute`.

**T1 — the minimum decisive production journey on IT436365.** Procedure:
`bugs-fixed/058-02082026(NewFindings).md` §2, verbatim. Summary:

1. On the i5, clean tree on `prompt-improve`, its **own** rebuilt venv (never copy `backend/env`).
2. `benchmark_i5_journey.py self-test` must print
   `{"unreviewed": "PENDING-REVIEW", "reviewed": "VALID"}`. Anything else: **stop**.
3. `template` → fill every `FILL_ME` → `prepare` (prints `READY - NO MODEL STARTED`) → `execute`
   → `finalize`.
4. **`PENDING-REVIEW` with exit code 3 is the expected success.** It is not a failure. `VALID`
   arrives later via `apply-review`, off the laptop, after a practitioner reads the transcript and
   note.
5. Copy (never move) the whole bundle off with a path/bytes/SHA-256 manifest.

Run **only** the one preregistered cold 45-minute-class row. Do not open warm rows, thread sweeps or
extended matrices until it passes its evidence, transcript, note and reliability gates.

Historical order at the time was T2 confirmation then T7a. Both ran; do not treat this sentence as a
current instruction. The corrected order is above and in §11.7.

### 11.3b HISTORICAL ONLY — T7a Vulkan spike procedure that already failed

> **DO NOT EXECUTE.** Retained to explain the 2 August evidence. T7a is closed by §11.3d/`061`.

The historical procedure changed **zero** production files:
the app keeps launching `backend/llama_server/llama-server.exe`; this runs a separate binary, by
hand, on a different port.

**Get the binary.** From the llama.cpp `b9585` release — the *same tag we bundle*, which is what
removes the version-skew confound:

```
llama-b9585-bin-win-vulkan-x64.zip     38,405,705 bytes
```

Extract to a scratch folder **outside the repo**, e.g. `C:\vulkan-spike\`. No installer, no pip, no
venv, nothing system-wide. `backend/llama_server/` is what `dist:clinical` bundles, so a foreign
unsigned binary must never be placed there. Record the zip's SHA-256 and the GPU driver version.

**Pin the parity settings from the CPU control first.** Start the app normally once, capture the
real `llama-server` startup log, and read off what production actually resolves on that machine:
effective `-t` / `-tb`, context, and model path. The spike uses those exact values explicitly —
never implicit, never `llama-bench` defaults.

**T7a.0 smoke qualification — must pass before any timed repetition.** For each of
`-ngl 0`, `-ngl ≈half`, `-ngl 999`:

1. the Vulkan device enumerates, and it is **the device under test** — Vulkan enumerates *every*
   capable device, so confirm the selected one from the startup log rather than assuming;
2. the model loads;
3. the startup log states the actual backend, device, and offloaded-layer count;
4. one short production-shaped request completes: no crash, no garbage, no truncation, no OOM;
5. record RAM and commit charge before and during. On IT436365 the Iris Xe shares system RAM against
   a 16 GB total, so `-ngl 999` may exhaust shared memory — that is a legitimate smoke failure, not
   a surprise.

Any smoke failure stops the matrix. Record it and rule per §6 T7a's verdict criteria.

**Only then** run the balanced timed conditions in §6 T7a: bundled-CPU control, Vulkan `-ngl 0`,
`-ngl ≈half`, `-ngl 999`; longest fixture, n=3, balanced order, 5-minute stabilisation between
condition blocks.

**Reading the result — three comparisons, three different meanings** (§6 T7a):
bundled CPU vs Vulkan `-ngl 0` = build/backend skew only; Vulkan `-ngl 0` vs partial/full = the
cleanest within-build estimate of the offload effect; bundled CPU vs best Vulkan = the practical
product opportunity. `-ngl 0` is **not** assumed to mean zero GPU work — verify it from the log.

**Do not** claim a product saving from Beautify alone. Convert it against T1's composed clock-4
phase shares from the same machine, which is exactly why T1 runs first.

### 11.3c HISTORICAL ONLY — JP-START reproduction that already ran

> **DO NOT REPEAT.** The crash was already reproduced and the question is settled for planning.

**Written 2 August 2026, same session as the IT436365 smoke failure.** This is a narrow
mechanism-diagnostic check, not a T7a run. It does **not** replace or advance the preregistered
T7a matrix (which stays gated to Iris-Xe-class per §6 T7a's own scope), and it does **not** by
itself decide the KILL-ratification question in §11.7 item 1 — it only answers one question:
**does the same crash reproduce on a different iGPU, or is it specific to IT436365's Iris Xe /
driver?**

**What happened on IT436365, in one line:** `llama-b9585-bin-win-vulkan-x64.zip` (official
llama.cpp release, same tag as the bundled server) loaded and served the production Gemma E2B GGUF
fine at `-ngl 0` (CPU-only) and `-ngl 999` (full GPU offload, though *slower* than CPU-only on both
prefill and decode there), but crashed at `-ngl 18` (half of the model's 36 layers split across
CPU+Vulkan) with:

```
D:/a/llama.cpp/llama.cpp/ggml/src/ggml-backend.cpp:1367: GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS) failed
```

before the server ever reached "listening" — not an OOM, not a driver rejection. Full detail:
`bugs-fixed/060-02082026.md` §8.

**Why JP-START is genuinely informative here, and why it isn't a performance test:** JP-START has
a *different* Intel iGPU generation than IT436365's Iris Xe, **and** an RTX 4050 dGPU. If the same
partial-offload crash reproduces on JP-START's iGPU, that points to a ggml-scheduler/model-
architecture bug (Gemma's fused Gated Delta Net + SWA layers spanning two backends) that is
independent of the specific GPU — a stronger, more generalisable finding than IT436365 alone. If it
does **not** reproduce there, that narrows the failure to something Iris-Xe- or driver-specific,
which is also informative. Either outcome is worth recording. **This is not a speed test** —
JP-START's numbers never transfer to the weak-tier product question (§11.6 rule 8), and its RTX
4050 is a fundamentally different case (dedicated VRAM, not shared system memory) that the plan
deliberately keeps out of scope (§11.4, CUDA descoped) — testing the 4050 would be a genuinely new,
unplanned experiment, not part of this reproduction check.

**Everything needed to run this cold, on JP-START, in one sitting:**

1. **Get the binary.** Download `llama-b9585-bin-win-vulkan-x64.zip` fresh on JP-START from
   `https://github.com/ggml-org/llama.cpp/releases/download/b9585/llama-b9585-bin-win-vulkan-x64.zip`
   (38,405,705 bytes; verify `sha256:af6b1b94377b9f78dbb2285b878fb696d36766391499d65e055ecd622b69018a`
   — same public asset, hash must match regardless of machine). Extract to a scratch folder
   **outside the repo** (e.g. `C:\vulkan-spike\`) — never into `backend/llama_server/`.
2. **Enumerate devices before doing anything else.** Run
   `llama-server.exe --list-devices` and read the output. JP-START has **two** Vulkan-capable
   devices (the RTX 4050 and an Intel iGPU) — do not assume which enumerates as `Vulkan0` vs
   `Vulkan1`. Identify the Intel one by name in the listing.
3. **Pin real parity settings from JP-START's own production startup log** — do not copy
   IT436365's `-t 8 -tb 8`; JP-START is 6P+4E (10c/16t) and will resolve differently. Start the app
   normally once, do one real Beautify, and read the effective `-t`/`-tb`/context/model path from
   the real `llama-server` startup log (same method used for IT436365, `060` §8.1).
4. **Target the iGPU explicitly** with `-dev VulkanN` (the flag is `-dev`/`--device`, comma-separated
   device names as printed by `--list-devices`) — pointing at the Intel device identified in step 2,
   never the RTX 4050, since this check is about the iGPU-crash question specifically.
5. **Run the three conditions** (`-ngl 0`, `-ngl 18` — half of the same model's 36 layers, `-ngl
   999`), same GGUF (`gemma-4-E2B-it-qat-UD-Q4_K_XL.gguf`, hash-verify against the pinned model hash
   in `060` §8.1), same flags otherwise. Watch specifically for the
   `GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)` line at `-ngl 18`.
6. **Record whichever happens** — crash-reproduces or clean load are both a real, useful result.
   No timed comparison, no evidence bundle, no balanced schedule needed for this check; a short
   note (append to `060` or a new short record) with the raw log excerpt is enough.
7. Zero production files touched either way — same reliability scope as the IT436365 spike
   (§11.3b, `060` §8.6).

**To pick this up cold in a fresh session:** point it at this section (§11.3c) plus
`bugs-fixed/060-02082026.md` §8 for the original crash and mechanism hypothesis. Nothing else needs
explaining first — the binary URL/hash, model hash, layer count (36), exact assertion text, and
device-selection flag are all here.

### 11.3d Why T7a / Vulkan partial GPU offload is stopped for now — full closure record

> **Corrected 3 August 2026:** the former research exception is cancelled as the next action.
> Preparation exists but remains unbuilt. Do not compile PR #22789 or resume the `-ngl 18` matrix.
> `bugs-fixed/061-03082026.md` is now the definitive goal-correction and next-work record.

**Written 2026-08-02, same day as the JP-START reproduction check.** This is the complete chain of
evidence behind the owner's practical decision to stop pursuing this lever. It supersedes the "needs
owner ratification" framing in §11.1/§11.7 as of this date — read this section, not just the older
open-item language, for the current position.

**The chain, in order:**

1. T7a.0 smoke qualification on IT436365 found `-ngl 18` (half the model's 36 layers split CPU+GPU)
   crashes before the server reaches "listening" — `GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)`
   in `ggml-backend.cpp`. Not memory-related, not a driver rejection. `060` §8.
2. §11.3c's JP-START reproduction ran the same three conditions on a second machine — different
   Intel iGPU generation, different driver family (~1 year newer). **Identical crash, identical
   split point, identical assertion, byte-for-byte.** `060` §8.7. This ruled out "one bad laptop /
   one bad driver" as the explanation.
3. Investigating the assertion found it is **already a known, actively-tracked upstream bug**:
   [llama.cpp#24132](https://github.com/ggml-org/llama.cpp/issues/24132) (open since ~June 2026, 11+
   comments), specific to Gemma 4 E2B/E4B under partial offload, already reproduced by other users on
   CUDA and ROCm — i.e. the same bug across three independent GPU backends, which confirms it is a
   defect in llama.cpp's shared cross-backend scheduler code, not anything specific to our hardware,
   our driver, or Vulkan.
4. A fix exists — [llama.cpp#22789](https://github.com/ggml-org/llama.cpp/pull/22789), "use dynamic
   allocation for split graph inputs" — but as of 2026-08-02 it is **open, unreviewed by a maintainer,
   not merged, and not in any official release.** There is nothing to bundle even if we wanted to.
5. **Separately from the crash entirely:** even the one condition that *does* work today — `-ngl 999`,
   full GPU offload, no crash — showed **no speed benefit** on the one data point measured. On
   IT436365 it was slower than CPU-only on both prefill (16.5 vs 44.1 tok/s) and decode (8.1 vs
   11.6 tok/s). This matches the plan's own realistic prior going in (§11.4: "wash, possibly worse" —
   an iGPU shares the CPU's memory controller, and decode is bandwidth-bound, not compute-bound). So
   even a hypothetical llama.cpp release with the crash fixed would not, on present evidence, make
   this worth shipping.

**Net result:** partial offload is broken in pinned b9585 and full offload has no demonstrated local
benefit. More importantly, even a patched midpoint answers the wrong product question: `-ngl` places
dependent layer ranges on different backends; it does not schedule independent concurrent CPU+iGPU
work. There is no current version of this lever worth prioritising.

**What this does and does not mean.** This closes **one lever** (Vulkan/GPU offload for Beautify),
not the whole initiative. It is not "no options left" in the broader sense — see §11.7 for what
remains genuinely open on IT436365: T1 practitioner review, T5’s byte-identical fixed-prefix test,
T7b Whisper OpenVINO/Vulkan, T7c E2B MTP, and—only after their gates—T7d progressive prefill. A 135U
is unavailable and must not block this work. §10.4 remains independent engineering work.

**Original production reopening requirement (per §7's ledger convention):** a new official llama.cpp release that both (a)
contains a merged fix for #24132/the `GGML_SCHED_MAX_SPLIT_INPUTS` overflow, and (b) is re-measured
showing a real speed benefit for partial or full offload on iGPU-class hardware — not just "the crash
is gone." Tracking the upstream issue (comment posted, §11.3c/§11.3d evidence attached) is sufficient;
no periodic re-checking is scheduled. A new explicit owner instruction would still be required even
after that bar is met, because the current work order attacks different mechanisms first.

**Formal note on the ratification rule (§8.5):** the plan's KILL rule technically still asks for an
explicit owner ratification of scope (whole-track vs. Iris-Xe-class-only). This section records the
owner's practical decision to stop working on T7a given the compound evidence above; it is not a
formal re-litigation of that narrower scope question, because the compound evidence (upstream bug +
no unmerged fix + no demonstrated benefit even when working) makes the scope distinction moot for any
near-term work either way.

#### 11.3d.1 Exact-PR checkpoint — PREPARED / UNBUILT / CANCELLED AS NEXT ACTION

The historical question was whether PR #22789 removes the `-ngl 18` scheduler assertion. That is a
valid upstream diagnostic question, but it is no longer an authorised next product-speed experiment.

**Prepared outside the repository:** a portable MSYS2 UCRT64 build environment under
`%TEMP%\private-llama-b9585-pr22789-20260803`, exact b9585 source at
`d73cd076740db9c111d0e58ddd4486904469e75e`, fetched PR head
`cd572e919ad445a6b9d50b4c5db96f279d0819aa`, and the PR's exact one-file
`ggml/src/ggml-backend.cpp` delta (44 additions/6 deletions). The source file matches the fetched PR
version exactly. GCC 16.1.0, CMake 4.4.2, Ninja 1.13.2, shaderc 2026.3, and Vulkan 1.4.357
development components are installed only inside that Temp tree.

**Final stop boundary:** no CMake configure, compilation, binary, model load, server process,
request, or timing run exists. PRIVATE application code and `backend/llama_server/` are untouched.
Do not cross this boundary from the former instructions.

**Cold-start source of truth:** `bugs-fixed/061-03082026.md` — **read its §0.1 first.** It says not to
resume or reconstruct this build merely because the Temp checkpoint exists. Its first version ordered
T5 → T7b → T7c → gated T7d; the same-day second correction replaces that with
**T7b.0 → T7c → T7d**, with the T7b GPU arms blocked behind T7b.0 and T5 folded into T7d.

**Decision:** provenance retained; no build, no result, no speed claim, no reconstruction, and no
production candidate. Future reopening uses §7’s explicit requirement and a new owner instruction.

### 11.4 Backend choice is workload-specific, not Vulkan-only

The old “Vulkan, not SYCL” ruling was too broad. It described only the pinned b9585 llama.cpp asset
table and only full/partial Gemma target placement. The corrected track chooses an implementation
for each useful role:

| Role | First comparison | Current ruling |
| --- | --- | --- |
| Whisper transcription | whisper.cpp **CPU** (T7b.0) | **No Windows Vulkan/OpenVINO prebuilt exists** — both GPU arms need source builds. Measure the encoder share first; it is OpenVINO's hard ceiling |
| Gemma E2B draft | **Bundled b9585 — gate passed** | `--spec-type draft-mtp`, `-md`, `-devd` all present; no upgrade needed. Keep the bandwidth-heavy target on CPU; compare no-draft / CPU draft / iGPU draft |
| Growing prompt prefill | **CPU** | Needs no GPU. Vulkan/SYCL are **not** prerequisites — treating them as such was the priority inversion corrected on 2026-08-03 |
| Full Gemma target | Current CPU runtime | IT436365 `-ngl 999` was slower directionally; partial `-ngl` is stopped |

**A backend choice is also an installer choice.** OpenVINO means a second inference runtime, its DLL
set, and a converted encoder artifact shipped to customers — which aggravates the post-update AV-scan
startup delay behind the 1.0.3 licence-screen bug. MTP costs one optional 57 MiB GGUF; progressive
prefill costs nothing. Rank by upside *and* shipping cost, not upside alone.

The statement “b9585 has no Windows SYCL asset” remains a historical fact about one tag, not a
permanent ecosystem rule. Later llama.cpp releases have shipped Windows SYCL assets and maintain
official [SYCL backend documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/backend/SYCL.md).
SYCL can be a bounded comparator when it implements the specific MTP/prefill mechanism needed; it
does not reopen a full-target layer sweep.

CUDA remains descoped for the present fleet because no fleet-representative machine has an NVIDIA
GPU. JP-START’s RTX 4050 can answer mechanism questions only and cannot qualify Intel fleet devices.

Every saving is computed against the composed journey. On IT436365 transcription is measured at
210.7 seconds (34.4%) and Beautify at 401.0 seconds (65.6%); moving either phase may matter. The old
claim that “CTranslate2 has no Intel GPU path, therefore transcription is untouched” confused the
current runtime with the workload. T7b tests a different Whisper runtime without changing production
code first.

### 11.5 How a heterogeneous runtime would integrate — only after standalone proof

Presence of an iGPU is not enough. A production design assigns **validated roles**, not one global
“GPU mode”:

1. Allowlist runtime/device/driver classes only after the exact phase passes its speed, quality,
   reliability, memory, and deployment gates. Unknown or failed classes keep the current CPU path.
2. Record the runtime/backend used separately for transcription and Beautify. Support must be able
   to identify which path produced a Source or note.
3. Preserve explicit force-CPU control. On absence/startup failure, use CPU. On mid-phase failure,
   restart that entire phase on CPU; never splice two partial transcripts or notes.
4. Do not generalise one role’s success. OpenVINO Whisper success does not approve Gemma GPU, and
   MTP-draft success does not approve full-target offload.
5. Keep production prompts, target model, sampling contract, Source fidelity rules, and note quality
   gates unchanged unless a separately authorised product change says otherwise.
6. Integration must close binary/model provenance, licences, installer size, signing/scanning,
   runtime and driver compatibility, memory pressure, health checks, fallback, and activity logging.

One-time device calibration may eventually select among already quality-approved roles. It cannot
substitute for the blind gates, and per-request experimentation on clinical work is prohibited.

No source implementation is authorised by the current documentation update. T7e opens only after a
standalone arm passes and the owner explicitly approves an implementation preregistration.

### 11.6 Rules that do not bend

1. `prompt-improve` only. No merge to `main`. No push without explicit instruction.
2. No production default changes without a completed speed **and** quality **and** reliability
   decision.
3. `examples/`, `examples-raw/`, and `C:\Users\wooin\Documents\private-test-debugs\benchmark_results`
   are **read-only**. New evidence is create-only under `backend/benchmark_results/<experiment-id>/`.
4. Every benchmark invocation uses the project venv and `python -u`. A quiet redirected file is not
   evidence a process died.
5. Never infer effective runtime from requested flags. Parse the real startup log. `/props` is not
   truth for threads or speculation.
6. Never label an unexplained termination as EDR without portal evidence — record
   `UNKNOWN EXTERNAL TERMINATION`.
7. Do not reopen anything in the §7 closed-work ledger without a materially new mechanism.
8. Percentages, deadlines and phase shares **never transfer between machines**.
9. T7b/T7b.0 standalone discovery changes zero production files, and any foreign runtime/model stays
   outside `backend/llama_server/` and the bundle. T7d remains standalone/design-only until explicit
   owner approval; T7e is the only integration gate. **One recorded exception (2026-08-03, owner
   instruction):** T7c's MTP download path and on-by-default gate were shipped ahead of measurement —
   four files plus a benchmark pin, reversible by deleting the GGUF, setting `PRIVATE_AI_DISABLE_MTP=1`,
   or reverting the diff. Shipping it did **not** discharge T7c's speed or quality evidence, and no
   speed figure may appear in UI copy, release notes, or customer material until that evidence exists.
10. The initiative is not complete after any single phase.

### 11.7 Known-open, in priority order

**The prepared PR #22789 experiment is closed as the next action.** It remains unbuilt provenance,
not an open task. There is no 135U available; do not wait for one.

**Reordered 2026-08-03 (second correction, same day) — see `bugs-fixed/061-03082026.md` §0.1.**
Three changes: whisper.cpp has **no Windows Vulkan/OpenVINO prebuilt**, so those arms need source
builds and now sit behind a cheap CPU measurement; the **MTP runtime gate passed** and the draft head
is wired and on by default; and **progressive prefill needs no GPU**, so its old gate was an
inversion. **T5 is folded into T7d and will not run separately.**

> **⚠️ SUPERSEDED 2026-08-05 — the numbered list below is kept for provenance but is no longer the
> current order.** Items 2 and 3 (T7b.0, T7c) are **complete on IT436365** — see §11.9. Item 5
> (T7b GPU arms) is **closed**: IT436365's own same-machine gate arithmetic returned 16.88% and
> 13.93%, both under the ≥20% bar, so the whisper.cpp GPU source builds are not authorised. **The
> live order is in §11.11.** Read that section, not this list.

Historical order as of 2026-08-03:

1. **Practitioner review + `apply-review` on T1’s bundle** (`060` §1–§5), when the reviewer is
   available. This changes T1 from PENDING-REVIEW to VALID and can proceed independently of machine
   benchmark time.
2. **T7b.0 whisper.cpp CPU split + control — run once already on jp-start (comparison-only, 2026-08-03,
   §11.8), still owed on IT436365.** 8 MB download, no compilation. Produces the encoder/decoder share
   and the same-runtime control the old T7b protocol lacked. **This one number decides whether any
   whisper.cpp GPU arm is worth a source build** — OpenVINO offloads the encoder only, so the encoder
   share is that arm's hard ceiling. jp-start's own gate arithmetic (13.8–17.9%, using the IT436365
   34.4% cross-machine reference) does **not** clear the ≥20% bar — leans no, but per §11.6 rule 8 this
   does not decide anything; IT436365's own native number is what counts, and there it will be a clean
   same-machine calculation instead of a cross-machine estimate.
3. **T7c Gemma E2B MTP — run once already on jp-start (comparison-only, 2026-08-03, §11.8), still owed
   on IT436365.** Preflight is **done and passed**; the draft downloads from Settings and is active by
   default. Compare `PRIVATE_AI_DISABLE_MTP=1` (no draft), CPU draft, and Intel-iGPU draft with one
   runtime build. Require output gates, ≥10% Beautify wall improvement, and ≥30 seconds composed
   saving. Record draft acceptance — n-gram died at 10.2%, and a trained MTP head that lands near that
   number dies the same way. jp-start's real acceptance rate came in well clear of that graveyard
   number (~54.8% CPU-draft / ~50.1% iGPU-draft mean) — **not a kill signal**, though IT436365's own
   number is what decides shipping. Expect the **iGPU-draft arm to be the weak one**: a 57 MiB draft is
   nearly free on CPU, and iGPU placement pays a cross-backend sync per draft step — jp-start confirmed
   this direction (CPU-draft +18.0% decode vs iGPU-draft −19.1%), but confirm again on IT436365 rather
   than assuming the same margin transfers. **Also note the corrected telemetry mechanism (§11.8):**
   `usage.completion_tokens_details.accepted_prediction_tokens`/`rejected_prediction_tokens` is not
   populated by this build — read `timings.draft_n`/`draft_n_accepted` instead.
4. **T7d progressive prefix prefill on IT436365 — CPU, no GPU prerequisite.** Standalone replay only;
   production implementation still requires explicit approval. Largest addressable share of the
   remaining candidates, immune to the transcript-fidelity gate, zero deployment footprint.
5. **T7b GPU arms** — only if step 2's measured encoder share clears the gate arithmetic. Weigh the
   installer/AV-scan cost of a second inference runtime, not just the speed number.
6. **T4 and §10.4** remain independent fidelity/reliability work and retain their existing gates.
7. **Future 135U qualification** remains required before a fleet-wide hybrid-thread or iGPU policy,
   but unavailable hardware is not on the active critical path.

⚠️ **Before trusting any timing row produced after 2026-08-03:** MTP is on by default when its GGUF is
present. `benchmark_beautify_first_run.py` pins `PRIVATE_AI_DISABLE_MTP=1` unless `enable_mtp=True`;
any other harness that starts llama-server must do the same or its rows are not comparable with §8's
MTP-free evidence.

Keep every foreign runtime/model outside `backend/llama_server/` and the production bundle. A ZIP or
standalone executable is not installed into the app merely because it wins a spike. `061` contains
the full protocols, stop rules, output-preservation requirements, and provenance boundary.

### 11.8 T7b.0 + T7c ran on jp-start, comparison-only (2026-08-03) — results, corrections, and the
### IT436365 repeat handover

**Read this section if picking the initiative up cold.** It records what actually ran on jp-start
(machine roster role: comparison-only, §11.2 — a win or a loss here never demonstrates the product
target) and is the standing handover for repeating both on IT436365, the machine whose number
actually decides anything.

#### 11.8.1 T7b.0 result — gate leans no, does not clear

`whisper.cpp` v1.9.1 official CPU build (`whisper-bin-x64.zip`, 7,982,101 bytes) + `ggml-base.bin`
(147,951,465 bytes) run against `counselling-31-min.mp3` and `counselling-45-min.mp3`, plus a fresh
same-machine `faster-whisper` CPU/int8 control using the real production call shape. Encoder share of
whisper.cpp's own reported total was **52.06% (31-min) and 40.04% (45-min)** — far higher than the
plan's ~25% prior, and itself not fixture-invariant (it moved 12 points as the 45-min fixture's
decode-side work grew disproportionately to its near-flat encoder cost — encoder cost tracks audio
*duration*, decode-side tracks *speech density*, the same pattern `CLAUDE.md` already documents for
whole-transcription cost, now shown to extend to the within-transcription phase split).

**Gate arithmetic** (encoder_share × 34.4%, the IT436365 clock-4 transcription-share reference from
`bugs-fixed/060-02082026.md` — multiplying a jp-start ratio by an IT436365 ratio, which §11.6 rule 8
flags as not formally transferable): **17.91% (31-min) and 13.77% (45-min)**, both under the plan's
own ≥20% bar. **Verdict: does not clear, on this comparison-only evidence** — roughly double the
plan's prior ~8.6% guess but still short. Not a clean kill (the ratio moved 12 points between two
fixtures) — a "leans no, worth the already-required IT436365 repeat before treating as final" result.
Control-runtime comparison (whisper.cpp CPU vs faster-whisper CPU) flipped sign between fixtures
(whisper.cpp 47.9% slower on the 31-min, 11.7% faster on the 45-min) — no clean runtime winner either
way, at n=1 per fixture. Informal word-level spot-check against the hash-verified 45-min reference
transcript: 87.6% coverage (VAD was off — no VAD model was in the handover's fixed asset list — a real
deviation from production's `vad_filter=True`, plausibly a partial confound for the gap). Full
bundle: `backend/benchmark_results/t7b0-whisper-cpp-cpu-03082026-jp-start/RESULT.md`.

#### 11.8.2 T7c result — real, working mechanism; iGPU confirmed the weak arm

Standalone harness (`backend/tests-benchmarks/benchmark_t7c_mtp_standalone.py`, new create-only script) drove the
Vulkan-capable b9585 `llama-server.exe` (identical tag to the bundled server, extracted from the
T7a-spike zip at `C:\vulkan-spike\extracted\` on jp-start — used as the **single runtime build for all
three conditions** so a build/backend change is never mistaken for an MTP effect) through
`no_draft` / `cpu_draft` / `igpu_draft`, target forced `-ngl 0` in every condition so only draft
placement varied, n=3 each, balanced order, byte-identical real Beautify-shaped messages (PRIVATE
default template, `short-private` fixture) across all nine runs.

**Acceptance rate — the number to report first, per the standing instruction:**
CPU-draft **56.6% / 54.9% / 50.9% (mean ~54.8%)**; iGPU-draft **48.7% / 50.7% / 50.9% (mean ~50.1%)**.
Both are well clear of n-gram's dead 10.2% graveyard number — this is a real, working speculative
mechanism, not a repeat of that closed experiment.

**Decode throughput** (the fairer comparison than raw wall-clock, since output length varies run to
run under temperature 0.1 sampling): no-draft baseline ~24.5 tok/s; **CPU-draft ~28.9 tok/s (+18.0%)**;
**iGPU-draft ~19.8 tok/s (−19.1%)**. Confirms the plan's own prior with real numbers instead of
assumption: the iGPU-draft arm is the weak one, a cross-backend sync per draft step costing more than
the mostly-free CPU draft saves. A harmless `[spec] failed to measure draft model memory: failed to
create llama_context from model` warning appears at startup in both draft conditions — confirmed
non-fatal via `/slots` (`"speculative":true`) and the verbose accept/reject trace; it does not block
real operation. Full bundle: `backend/benchmark_results/t7c-mtp-acceptance-03082026-jp-start/RESULT.md`.

#### 11.8.3 Two corrections worth carrying forward

1. **Telemetry field correction (updates `CLAUDE.md`'s Local AI Stack section and this plan's own T7c
   description above).** The handover assumption that `usage.completion_tokens_details.
   accepted_prediction_tokens`/`rejected_prediction_tokens` is populated by the bundled b9585 build is
   **wrong** — confirmed absent in both streaming and non-streaming mode via a targeted diagnostic
   (`backend/tests-benchmarks/benchmark_t7c_diagnostic.py`: raw SSE dump, non-streaming request, `/slots`, `/metrics`).
   The real field is **`timings.draft_n` / `timings.draft_n_accepted`**, present on the response's
   `timings` object (the final SSE chunk when streaming). `ai.py`'s existing `nested_allowed` parsing
   for the Support Diagnostic Log currently names the field that this build never sends — any future
   code that wants real MTP acceptance numbers (diagnostics, UI, further benchmarking) must read
   `timings.draft_n_accepted`/`draft_n`, not `usage.completion_tokens_details`.
2. **The first T7c run (now kept only as
   `backend/benchmark_results/t7c-mtp-acceptance-03082026-jp-start/t7c_raw_results_v1_incomplete_acceptance_field.json.bak`,
   provenance only, not data) had a real harness bug**, not a build limitation as first hypothesized:
   the script captured `timings` from the SSE stream but never serialized it into the output row. Once
   fixed, the full 9-run matrix was re-run clean and produced the numbers in §11.8.2.

#### 11.8.4 Evidence-routing miss — not yet corrected, owner is relocating manually

Per `.claude/commands/BenchmarkCommands.md`'s standing override, all new benchmark evidence must land
under `%USERPROFILE%\Documents\private-test-debugs\benchmark_results`, never this repo's
`backend/benchmark_results/`. **Both new scripts violated this** — they hardcode
`backend/benchmark_results/<experiment-id>/` with no `--out` support, the same class of gap the
override note already calls out for `benchmark_live_slice_replay.py`/`benchmark_warm_start_spike.py`.
As of this writing the two evidence bundles (§11.8.1/§11.8.2) and three new scripts
(`benchmark_t7b0_faster_whisper_control.py`, `benchmark_t7c_mtp_standalone.py`,
`benchmark_t7c_diagnostic.py`) are **untracked, uncommitted**, sitting in this repo's
`backend/benchmark_results/` and `backend/`. Nothing has been committed — the owner is relocating the
evidence bundles to `private-test-debugs` manually. **Before reusing these scripts on IT436365 or any
other machine, fix the output path** (either add `--out` support following the pattern in
`benchmark_beautify_first_run.py`, or at minimum move the run folder immediately after, per
`BenchmarkCommands.md`'s documented fallback) — do not repeat the same miss a second time.

#### 11.8.5 Handover — repeating T7b.0 + T7c on IT436365

This is the actual next action. jp-start's results above are a comparison-only early read, not a
decision — IT436365 is the machine whose number closes the T7b GPU-arm question and the T7c shipping
question for real, and its gate arithmetic (§11.8.1's calculation) becomes a **clean same-machine
calculation instead of a cross-machine estimate** once run there, because IT436365 is both the source
of the 34.4% transcription-share reference *and* the machine being gated.

**Preconditions — same as §11.3's original IT436365 checklist, still apply:** clean tree on
`prompt-improve` at the pulled commit; IT436365's own rebuilt `backend/env` (never copy from another
machine); audio fixtures already present (verify hash, do not assume — `counselling-45-min.mp3`
expected 62,641,987 bytes, SHA-256 `7d863bf1ed116a0e40049dda75a227d9a00e3db10162368a5cfb5aa139d454e8`);
AC power, battery ≥95%, Windows Balanced plan, office-idle, ~5 minutes idle before running.

**New preconditions specific to this repeat:**

1. **Get the three new scripts onto IT436365.** They are currently untracked on jp-start's
   `prompt-improve` checkout (§11.8.4) — git alone will not carry them across machines until they are
   committed and pushed (or pulled from wherever jp-start's branch is shared). Decide how to get them
   across (commit+push, or manual copy) before starting; this plan does not commit anything on its
   own authority.
2. **Fix the output-path miss (§11.8.4)** before the IT436365 run, not after.
3. **The MTP draft GGUF is very likely NOT yet on IT436365.** It only started downloading/shipping
   2026-08-03; IT436365's model directory was last known-current from late-July Beautify runs (§11.3
   precondition 4), before MTP existed. Get it via Settings' in-app download, or directly:
   `https://huggingface.co/unsloth/gemma-4-E2B-it-qat-GGUF/resolve/main/mtp-gemma-4-E2B-it.gguf`
   (expect 59,235,648 bytes) into `private_storage/models/`.
4. **IT436365 needs its own Vulkan-capable b9585 `llama-server.exe`** — jp-start's copy at
   `C:\vulkan-spike\extracted\` is local to that machine. Fetch fresh (same public asset, hash must
   match regardless of machine):
   `https://github.com/ggml-org/llama.cpp/releases/download/b9585/llama-b9585-bin-win-vulkan-x64.zip`
   (38,405,705 bytes, SHA-256 `af6b1b94377b9f78dbb2285b878fb696d36766391499d65e055ecd622b69018a`).
   Extract outside the repo (e.g. `C:\vulkan-spike\`, matching jp-start's layout so the scripts'
   `VULKAN_SERVER_EXE` constant needs no edit — or edit the constant if using a different path). Run
   `--list-devices` first and confirm which Vulkan device is IT436365's Iris Xe before targeting it for
   the iGPU-draft condition — do not assume device ordering transfers from jp-start.
5. **T7b.0's whisper.cpp assets are the same public downloads, no machine-specific step:**
   `https://github.com/ggml-org/whisper.cpp/releases/download/v1.9.1/whisper-bin-x64.zip`
   (7,982,101 bytes) and `https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin`
   (147,951,465 bytes).

**Run T7b.0 first** (cheap, no server lifecycle, decides whether any whisper.cpp GPU arm is worth
building), **then T7c** (avoid running both concurrently — CPU contention would contaminate both).
Reuse the jp-start scripts as the starting point; the extraction logic for T7c is already correct
(`timings.draft_n`/`draft_n_accepted`, §11.8.3) — do not reintroduce the `usage.
completion_tokens_details` assumption.

**What changes in interpretation on IT436365 versus jp-start:**

- T7b.0's gate arithmetic stops being a cross-machine estimate and becomes IT436365's own real number
  — this is the one that actually decides whether to open a whisper.cpp GPU-arm source build (§11.7
  item 5).
- T7c's acceptance rate and decode-throughput deltas become the real evidence against the plan's
  shipping gate (≥10% Beautify wall improvement, ≥30s composed saving) for the MTP-on-by-default
  decision already shipped ahead of measurement (`bugs-fixed/061-03082026.md` §9) — this repeat is
  what discharges that owed measurement debt, not the jp-start run.
- Do not average or otherwise merge jp-start's numbers with IT436365's. Record both, cite each by
  machine, per §11.6 rule 8.

**After running:** write both `RESULT.md` files following the format in §11.8.1/§11.8.2's bundles,
move the evidence into `private-test-debugs` correctly this time (§11.8.4), and update this section
(or add §11.9) with the IT436365 numbers rather than editing over the jp-start record above — both are
worth keeping, machine-labelled, per the established convention elsewhere in this plan (§11.2).

#### 11.9 IT436365 repeat — T7b.0 + T7c complete (2026-08-04)

The decision-grade repeat ran on IT436365 after verifying both audio fixture hashes. T7b.0 ran
first, sequentially, using whisper.cpp v1.9.1 CPU plus the fresh faster-whisper CPU/int8 control.
The whisper.cpp encoder share was **49.07%** on the 31-minute fixture and **40.48%** on the
45-minute fixture. Applying the IT436365 34.4% transcription-share reference gives **16.88%** and
**13.93%** journey ceilings, both below the ≥20% T7b gate. **Do not build the whisper.cpp GPU arms
from this result.** The faster-whisper control remained the faster runtime on the 31-minute fixture
and whisper.cpp was 7.98% faster on the 45-minute fixture; the sign still does not form a clean
runtime win, with the stated no-VAD confound on whisper.cpp.

T7c then ran all nine rows with zero smoke failures, one identical b9585 Vulkan runtime, target
forced to CPU, and `Vulkan0` confirmed as IT436365's Intel Iris Xe. Mean no-draft wall was
237,739.67 ms; CPU draft was **180,917.00 ms (−24.0%)** with **51.85%** acceptance; Iris Xe
draft was **189,926.67 ms (−20.1%)** with **52.13%** acceptance. Every acceptance value came from
`timings.draft_n_accepted/draft_n`. CPU draft is the preferred placement in this matrix. The
standalone ≥10% / ≥30-second gate clears, but a composed production journey was not rerun, so that
part remains unconfirmed. Do not average these numbers with jp-start's comparison-only results.

Evidence is create-only under the separate debug repository:

- `C:\Users\wpar027\Documents\private-test-debugs\benchmark_results\t7b0-whisper-cpu-04082026-it436365\RESULT.md`
- `C:\Users\wpar027\Documents\private-test-debugs\benchmark_results\t7b0-faster-whisper-control-04082026-it436365-v2\results\t7b0_faster_whisper_control.json`
- `C:\Users\wpar027\Documents\private-test-debugs\benchmark_results\t7c-mtp-acceptance-04082026-it436365\RESULT.md`

#### 11.10 JP-START CPU-MTP audio qualification and handover (2026-08-04)

This is the end-of-day summary for the JP-START session. It is a separate,
sealed qualification bundle and must not be confused with the decision-grade
IT436365 standalone T7c result in §11.9.

**What ran and what passed**

- R2 of the b10248 Intel target-placement smoke ran as preregistered on the
  longest Source. It **failed** the predeclared gates: `-ngl 18` did not reach
  the 1.5× prefill gate, was slower than the same-build `-ngl 0` control on
  median wall, and did not beat the fresh current CPU control. R3 was therefore
  correctly not authorised. Gemma Intel target placement is closed.
- The broader CPU-MTP audio qualification then ran on six frozen, hash-verified
  fixtures with production code, prompts, schemas, model defaults, and
  Appearance behaviour unchanged.
- Deterministic temperature-0 pass: 3 representative fixtures; CPU-MTP wall
  improved by 8.8% on median, with valid headings and clean stops.
- Counterbalanced production-temperature 0.1 pass: 6 fixtures / 12 rows;
  CPU-MTP was faster on 5/6, with a paired median wall delta of **−15.4%**.
  The organisation-template fixture was **14.7% slower** with CPU-MTP on raw
  wall. **Corrected 2026-08-05 — that row is an output-length artifact, not a
  slowdown.** It generated **29.1% more tokens** (2,080 vs 1,611). Normalised
  for output length, CPU-MTP decoded **faster in 6/6** fixtures: +27.1%, +9.3%
  (this fixture), +31.4%, +30.6%, +16.3%, +60.1%, at 47.6–61.3% draft
  acceptance. There is no fixture in this matrix where MTP decodes slower. Do
  not cite the 14.7% figure as evidence of an MTP regression.
- Repeatability pass: 3 thermal sessions × 3 fixtures × 2 conditions = 18
  rows. Median paired wall delta was **−11.8%** (mean **−11.5%**); all rows
  completed cleanly. Median savings were 17.3 s on the short fixture, 23.1 s
  on the longest fixture, and 40.4 s on the difficult fixture.
- Across the 36 qualification rows there were no harness failures, truncations,
  or invalid heading orders. These are isolated Beautify request timings, not
  composed real-application savings.

**Quality and release interpretation**

> ⚠️ **THIS QUALITY REVIEW IS UNATTRIBUTABLE. Corrected 2026-08-05 — read this
> before citing anything below it.** The jp-start harness
> (`tmp/cpu_mtp_qualification.py`) **set no sampling seed**, so llama-server drew
> a fresh seed per request at temperature 0.1. **§4.1 requires the seed to be
> recorded and §4 forbids required fields silently becoming `null`; this run
> violated that contract.** The consequence is visible in the run's own data:
> in the repeatability pass the **no-MTP control produced 3 unique outputs in 3
> runs on every fixture**, with completion-token spreads of 6.5% / 16.0% / 17.1%
> — while the between-condition token deltas were −10.2%, +29.1%, −10.1%,
> +5.6%, +5.5%, −1.5%, i.e. **inside the control's own variance band and in no
> consistent direction**. The differences the reviewer found therefore cannot be
> attributed to MTP. Do not cite this review as evidence that MTP degrades
> output, nor as evidence that it does not. **The seeded IT436365 bundle is the
> one that can answer this — see §11.11.**

- The blinded textual review found **no clear systematic CPU-MTP regression**.
  MTP was more complete or more explicit about safety in some pairs, while
  another hard pair traded away some historical suicidal-ideation detail while
  explicitly flagging risk. Several outputs in both conditions had incomplete
  Risk Level/template sections. **Note the accidental direction: where the arms
  differed, MTP was the arm that filled Risk/Assessment in fixtures 02, 03 and
  05. There is no mechanism by which speculative decoding improves clinical
  completeness — that bidirectional, mechanism-free pattern is the signature of
  sampling noise, not a treatment effect.**
- Output hashes differed between conditions. The current evidence therefore
  does not establish content equivalence from timing alone. **But note that the
  control did not reproduce its own hashes either, so hash difference alone
  carries no information here.**
- There is no independent practitioner sign-off and no clinical safety pass.
  CPU-MTP is promising, not yet a default-ship decision.
- **Separately, and more important than the MTP verdict: 4 of 6 fixtures left
  Risk Level or template sections as "Please complete" in at least one arm, and
  fixture-04 failed in *both* arms.** Per §3.2 step 6 that is a finding about
  the product, not about the lever. It corroborates the standing record that
  risk handling has failed prompt-only three times and that the deterministic
  risk guard was never built. Route it to the defect record, not to this
  experiment's verdict.

**End-to-end gate**

- The real Electron/renderer journey was **not measured**. No renderer-observed
  time-to-free, Stop-to-durable Source, Source-to-first structured text,
  Source-to-durable draft, Stop-to-durable draft, composed saving, or tail
  latency claim is made.
- The local in-app browser surface was unavailable in this session and the
  app was not running on its normal 8000/5173 listeners. The renderer build
  itself passed. Backend/direct timings must not be substituted for the missing
  renderer clock.
- The sealed result bundle is create-only at
  `tmp/cpu-mtp-qualification-result-20260804-jp-start/`.
  Read `RESULT.md`, `RESULT.json`, `repeat-analysis.json`,
  `quality-review.json`, and `SEAL.txt` there. Do not edit the bundle; create a
  new experiment directory for any rerun.

**Handover / next action**

1. Have an independent practitioner review the existing blinded A/B packet
   against Source, with special attention to Risk Level, suicidal ideation,
   missing template sections, negation, numbers, and unsupported facts.
2. If that review finds no unacceptable CPU-MTP regression, run one bounded
   real-application MTP-off versus CPU-MTP journey with the renderer available.
   Two counterbalanced rows should take roughly 30–90 minutes including model
   warm-up and cleanup; record the required composed clocks, durable state,
   output hashes, RAM/commit, failures, and tail behaviour.
3. If practitioner review identifies an unacceptable omission or distortion,
   do not spend the end-to-end run on a ship decision; retain the kill switch
   and investigate quality first.
4. Do not reopen Intel target placement or authorise R3 from this bundle. Do
   not average JP-START numbers with IT436365 numbers.

**Session hygiene note:** the benchmark report was sealed at
`2026-08-04T10:12:25Z` before the assistant response returned. Five
`llama-server` processes from the benchmark remained alive afterward; verify
which process is the user's active server before terminating anything. The
worktree has no tracked production changes; only `tmp/` is untracked.

#### 11.11 Position and handover as of 2026-08-05 — ARCHIVED, not the instruction

> **📁 Archive.** This was the live handover on 2026-08-05 and is superseded by the **Current Status**
> block at the top of this file. Read for the reasoning and the measured detail; do not take its
> "live order" as current — item 4 (T7d) and item 5 (T4) have both since closed.

**This section supersedes §11.7's numbered list as the live order.** §11.8–§11.10 remain accurate as
machine-labelled records of what ran; this section states where things stand now and what to do next.

##### 11.11.1 What is settled

- **T7b.0 is closed on both machines. The whisper.cpp GPU arms are NOT authorised.** IT436365's own
  same-machine gate arithmetic (§11.9) returned **16.88%** (31-min) and **13.93%** (45-min) journey
  ceilings against a ≥20% bar. jp-start's cross-machine estimate agreed (17.91% / 13.77%). Two
  machines, same direction, one of them computed cleanly on its own numbers. Do not open the source
  builds.
- **Intel target placement (Gemma `-ngl`) is closed.** b10248 R2 on the longest Source failed its
  preregistered gates: no 1.5× prefill gain, slower than the same-build `-ngl 0` control, slower than
  the fresh CPU control. R3 was correctly not authorised. Do not reopen; the mechanism is
  architectural — Iris Xe shares system DRAM with the CPU, so offloading buys no memory bandwidth,
  and prefill is bandwidth-bound.
- **MTP works and is the leading candidate.** Real speculative mechanism, 47.6–61.3% draft
  acceptance, nowhere near n-gram's dead 10.2%. Standalone gates clear on both machines.
- **The engine-flag search space is genuinely exhausted.** Reasoning budget, ubatch, Flash attention,
  threads, n-gram, batched Whisper, live transcription, transcript preparation, Vulkan target
  offload, whisper.cpp GPU arms — all closed with measurements. That is a finding, not a failure.
  What remains is architectural (T7d) or already declined by the owner (reasoning-off).

##### 11.11.2 New finding — MTP's benefit scales *inversely* with machine strength

⚠️ **This is a directional cross-machine inference about the *shape* of the effect, not a merged
number. §11.6 rule 8 stands: the timings below are never averaged, and each is cited by machine.**

| Machine | no-MTP decode | CPU-MTP decode | relative gain | wall reduction |
| --- | --- | --- | --- | --- |
| jp-start (Core 7 240H, 6P+4E, dual-channel DDR5) | 13.8–20.3 tok/s | 16.0–32.5 tok/s | +9% … +60% | −11.8% median |
| IT436365 (i5-1135G7, 4c/8t, single-DIMM DDR4) | 5.0–10.4 tok/s | 7.9–22.4 tok/s | +54% … +116% | −23.8% … −45.0% |

**Mechanism:** on a bandwidth-starved CPU, verifying 2–3 drafted tokens in one forward pass costs
barely more than verifying one, so speculative decoding amortises better the weaker the machine.

**Two consequences that matter for shipping.** First, **MTP helps most where the product is slowest**
— and the real fleet (15 W U-series, ~2 P-cores, §0D of `055`) is *weaker* than IT436365, so it
should benefit at least as much. This is a materially better ship case than the jp-start number alone
suggested. Second, **MTP's wall benefit is diluted exactly where prefill dominates** — long Sources on
faster machines. **That is precisely the case T7d attacks.** MTP owns decode, T7d owns prefill; they
are complementary and each covers the other's weak case. Do not treat them as competing candidates.

##### 11.11.3 The live order

1. **Determinism check on the IT436365 bundle — FREE, DO THIS FIRST, IT DECIDES STEP 2.**
   The IT436365 run pinned **seed `20260804`** (unlike jp-start, §11.10) and ran **n=3 per condition
   per fixture**. So the §3.2 step-2 control arm may already exist in that bundle. Compare the three
   `no_mtp` `output_sha256` values *within* each fixture, in:

   ```
   ...\private-test-debugs\benchmark_results\cpu-mtp-audio-qualification-04082026-it436365-v9-repeatability
   ...\private-test-debugs\benchmark_results\cpu-mtp-audio-qualification-04082026-it436365-v9-continuation-05082026
   ```

   (Note: those paths are `C:\Users\wpar027\...` — the IT436365 user profile. They are not reachable
   from jp-start. This check runs **on IT436365**.) Exclude v9 row 12, the interrupted 31-minute
   no-MTP arm, from everything.
   - **All three identical** → the engine is deterministic at fixed seed. MTP-vs-no-MTP differences
     are real MTP effects. Proceed to step 2 with a tightly scoped review.
   - **They differ despite the pinned seed** → the product does not reproduce itself even seeded.
     Byte-identity is off the table for MTP *and* T7d (record this — T7d's arm 0 then has its answer
     in advance). Blind 1-v-1 pairs are uninterpretable; MTP passes on mechanism grounds and you go
     straight to step 3.
   - Either way, **write the outcome into this plan.** It is load-bearing for every future A/B.

   ⚠️ **jp-start has already run this check and FAILED it (2026-08-05).** T7d Stage A's arm 0 issued
   two back-to-back ordinary requests on one fresh server and slot, same prompt, seed `20260805`,
   temperature **0.0**, and returned **different output hashes**
   (`d2df2163…` vs `bfe3d24a…`). So on jp-start the answer is already the second branch: byte-identity
   is unavailable and blind 1-v-1 pairs are uninterpretable there. The IT436365 check is still worth
   running — it uses a different seed, a different CPU, and its Stage B produced a **byte-identical
   Source across both arms** (`ff0f5c4d…`) where jp-start's four arms all differed, so the two
   machines may genuinely differ on determinism. That divergence is itself a finding; record it.
2. **Practitioner review — rescoped.** Do **not** ask "is MTP worse?" — that question is only
   answerable if step 1 came back deterministic, and it is the wrong use of scarce clinical time
   either way. Ask **"are these notes clinically acceptable?"** Hand over a blinded mixed set drawn
   from both arms, without disclosing that it is an A/B, scored against Source on the §3.2 step-4
   dimensions. If both arms show the same defect rate, MTP is cleared **and** you have measured your
   actual note quality for the first time. Give the incomplete Risk Level / template sections
   (§11.10, 4 of 6 fixtures, one failing in both arms) at least equal weight to the MTP comparison.
3. **The two counterbalanced real-application rows.** Scope is agreed and unchanged: the ~45-minute
   counselling recording, MTP-off vs CPU-MTP, order balanced; a second difficult recording adds
   confidence but is not required. Do **not** re-transcribe the frozen Sources — reuse them, or the
   Source changes and the comparison is confounded. Required clocks: Stop→durable Source,
   Source→first structured text, Source→durable draft, Stop→durable draft, composed saving, tail
   latency. **Blocker note:** §11.10 records that this stalled because the renderer surface was
   unavailable, *not* because the design was wrong. Before rebuilding a measurement rig, check
   whether `activity_log` suffices — it already timestamps `beautify-single` start/complete and may
   yield Source→durable-draft without renderer instrumentation.
4. ~~**T7d progressive prefix prefill — Stage A, then Stage B.**~~ **RAN AND CLOSED 2026-08-05 on both
   machines. Do not re-run the concurrent shape.** Stage A passed its mechanism gate on both; Stage B
   failed its composed-saving gate on both, in the same direction, within 0.6 s of the same net.
   Full record and the surviving variant: **§11.11.6**.
5. **T4 — live-transcription boundary reconciliation. CLOSED — REJECTED 2026-08-06 (owner ruling).**
   Phase 0A's `counselling-51-min` IT436365 result failed on four independent grounds (negation
   reversal, relocated self-harm content, a 19 s missed-speech gap, and a 16× repetition loop) — full
   ruling and reasoning in §11.12. T4 as designed (1 s overlap, timestamp-trim stitch) is closed; no
   further work proceeds under this candidate. Execution plan (history only, not an active queue):
   [`TranscribeBeautifyAudioWorkletNode.md`](TranscribeBeautifyAudioWorkletNode.md).
   ⚠️ Phase 0B (the noise-floor control) is no longer T4 work — see §11.12/§11.13 for its narrower
   remaining purpose: checking whether the same defects already exist in currently shipped serial
   transcription, an independent, potentially higher-priority question.
6. **§10.4** retains its existing independent gates. **Future 135U qualification** remains
   required before any fleet-wide hybrid-thread or iGPU policy, and is additionally the machine that
   sets T4's ≥120 s economic bar; no such machine is available and it does not block anything above.

##### 11.11.4 Process rules added 2026-08-05 — these are not optional

- **Pin `PRIVATE_AI_SEED` in every harness.** It already exists in `services/ai.py` (the chat payload
  builder reads it from the environment). §4.1 has always required the seed to be recorded; the
  jp-start run's omission cost a 36-row bundle that cannot answer its own question. An unseeded
  harness is a **contract violation**.
- **Every A/B carries a within-condition control arm** (§3.2 step 2, added same day). Repeat the
  control against itself before comparing across conditions. Without it, a between-condition
  difference is uninterpretable.
- **Ad-hoc harnesses in `tmp/` keep bypassing the evidence contract.** This is now the second
  instance of the same class: §11.8.4 records the `--out` routing miss, and §11.10 records the
  missing seed. Both harnesses were hand-rolled in `tmp/` rather than following the
  `backend/benchmark_*.py` pattern that enforces preregistration, seed capture, and output routing.
  **Before writing another benchmark script, extend an existing contract-validated one.**
- **Normalise wall-clock deltas by output length before calling anything a regression.** The
  "organisation-template fixture was 14.7% slower" line (§11.10) was an output-length artifact; that
  fixture decoded *faster*. Under temperature-0.1 sampling, output length varies run to run, so raw
  wall is a confounded metric and decode rate (`timings.predicted_per_second`) is the fair comparison.
- **MTP acceptance telemetry is `timings.draft_n` / `timings.draft_n_accepted`.** The bundled b9585
  does **not** populate `usage.completion_tokens_details.accepted_prediction_tokens`. Already recorded
  in §11.8.3; repeated here because `ai.py`'s `nested_allowed` parsing still names the wrong field.

##### 11.11.5 Standing corrections a cold-start session will otherwise get wrong

- **T7d is not "the second run of the day is faster."** That is the *naive warm-start*, which is
  already dead: it shared only the system message and envelope preamble between two different
  Sources, hit **1,526 of 11,007 tokens (13.86%)**, and is structurally capped near 13–17% of prefill
  because Source is 79.5–84.2% of the prompt. **T7d shares the prefix with itself** — the text being
  pre-evaluated *is* the transcript Whisper is producing right now — so it works on the **first**
  Beautify of the day, cold server, first recording. Different mechanism, ~80% ceiling not ~13%.
- **Reasoning-off remains closed by owner ruling and was re-declined on 2026-08-05**, on the owner's
  observation that the side effects ran roughly 50:50 good and bad. Do not schedule it, do not
  reintroduce it, and do not cite speed pressure as a reopening mechanism.
- **jp-start is comparison-only.** A win there never demonstrates the product target is met. Never
  average its numbers with IT436365's.

##### 11.11.6 T7d CLOSED — concurrent prefill killed on two machines (2026-08-05)

Reports (tracked, non-PHI): `benchmark-reports/IT436365-i5-prefill.md` (Stage A + Stage B),
`benchmark-reports/JP-START-i7-T7d-StageA-20260805.md`,
`benchmark-reports/JP-START-i7-T7d-StageB-45min-20260805.md`. Runners:
`backend/tests-benchmarks/benchmark_t7d_prefill.py`, `backend/tests-benchmarks/benchmark_t7d_stage_b.py`. Raw bundles stay in each
machine's own ignored `private-test-debugs\benchmark_results` tree. **Per §11.6 rule 8 the two
machines' timings are never merged; they are cited side by side below because they *agree in
direction*, which is the finding.**

**Stage A — mechanism PASS on both, to the token.**

| | IT436365 (i5-1135G7) | jp-start (Core 7 240H) |
| --- | ---: | ---: |
| Cached tokens at the 80% Source prefix | 8,934 | 8,934 |
| Prompt tokens still evaluated | 2,072 / 11,006 | 2,073 / 11,007 |
| Final production prompt byte-identical across arms | yes | yes |

Exact-prefix KV reuse is real, survives the production message builder untouched, and reaches ~81%
of the final prompt. That part of T7d is settled and needs no repeat.

**Stage B — composed-saving gate FAIL on both.**

| | IT436365 | jp-start |
| --- | ---: | ---: |
| Whisper slowdown | +128.827 s (+53.2%) | +93.883 s (+57.7%) |
| Beautify prompt saving | −121.092 s (−76.7%) | −86.774 s (−76.8%) |
| **Net** | **−7.735 s** | **−7.1 s** |
| Composed wall | 21.187 s slower | serial clock 5.7 s lower, correctly refused as a claim |

Two different topologies (4c/8t vs 10c/16t), two different power classes, both landing within 0.6 s
of the same negative net, with prompt reduction agreeing to a tenth of a percent. **Prefill finished
before transcription in both cases**, so "the overlap window was too small" is not an available
escape — the window was sufficient and the CPU was not.

**The generalisable lesson, which is worth more than the candidate:** on a CPU-only stack there is
**no free concurrency**. Prefill during Whisper does not spend idle time, it takes Whisper's time and
returns slightly less than it took. Any future candidate whose value proposition is "do X while Y
runs" is presumed dead unless X consumes a genuinely idle resource. That retires a whole class of
ideas for the cost of one experiment pair.

**Source-integrity divergence — a real cross-machine finding, not noise.** IT436365 produced a
**byte-identical Source in both arms** (`ff0f5c4d…`). jp-start produced **four different Sources
across four arms, including its two ordinary controls**. So jp-start's non-determinism is that
machine's own property, not something concurrency caused, and the i5 shows byte-identity *is*
achievable on this stack. Neither fact rescues T7d — the timing arithmetic fails independently — but
it does mean: **never gate anything on jp-start byte-identity again**, and run determinism-sensitive
arms on IT436365.

**The only surviving T7d variant is post-Stop idle prefill**, and it is now a *product* question, not
an engine one. The prize is real — the final prompt phase was 157.868 s of 334.563 s Beautify on the
i5 and 112.968 s of ~235 s on jp-start, so roughly **110–160 s off the Beautify click** if a genuine
idle window exists. Three unmeasured risks before anyone builds it:

1. **All-at-Once has no idle interval by construction**, so this cannot help the chain — only the
   governing workflow where the counsellor reads the Source before clicking Beautify.
2. **Any Source edit above the prefill point invalidates reuse from that point**, and editing is
   expected in that exact window. The realistic yield may be far below the ceiling above.
3. **Burning CPU while "idle" pre-heats the machine.** On a 15 W ~2-P-core U-series fleet part that
   may simply move the cost into thermal limiting on the Beautify that follows. Unmeasured.

**Consequence for the MTP/T7d pairing in §11.11.2.** That section reasoned that MTP owns decode and
T7d owns prefill, each covering the other's weak case. **Decode is now covered and prefill is not.**
Prefill is 21.2–33.2% of clock (4) and has no surviving concurrent lever.

**Priority statement — replaces this section's earlier closing line (owner ruling 2026-08-05, itself
superseded 2026-08-06).** The MTP quality gate remains the immediate critical path. **T4
live-transcription boundary reconciliation is CLOSED — REJECTED 2026-08-06** (owner ruling on Phase
0A's `counselling-51-min` result; full reasoning in §11.12). With T4 closed and T7d already closed,
**there is currently no surviving independent minutes-scale speed candidate on the transcription side
of clock (4).** Execution plan (history only):
[`TranscribeBeautifyAudioWorkletNode.md`](TranscribeBeautifyAudioWorkletNode.md).

> ⚠️ The line this replaced — *"there is no second speed candidate waiting behind it"* — was read by
> two consecutive sessions as meaning live transcription was closed when it was only killed **as
> designed on 2026-08-01** with an explicit reopening condition. T4 then executed that reopening and
> was itself rejected on 2026-08-06. Do not read *this* closure as reopenable by the same kind of
> phrasing drift — reopening now requires a genuinely new mechanism tested against §5's gates, not a
> rerun of anything in this file.

### 11.12 T4 Phase 0A — both machines report; owner ruling: REJECTED (2026-08-06)

> ⚠️ **Read before anything else in this section: T4 is CLOSED — REJECTED, owner ruling 2026-08-06.**
> IT436365's `counselling-51-min` result failed on four independent grounds: a negation reversal, the
> relocated self-harm/cutting span, a 19 s missed-speech gap, and a 16× repetition loop. Full reasoning
> is in the "Owner ruling" block below. The actual span text is not reproduced here or anywhere in a
> tracked file, per §6's no-PHI rule.

**Instrumentation repaired and committed.** `backend/tests-benchmarks/benchmark_live_slice_replay.py`
got the four fixes T4's own §4.0A specifies (fresh-reference flag, the audio-input/speech/largest-
missed-gap coverage triplet, an n-gram repetition detector with per-slice attribution, ±25-word
missing-span context), plus two things not in the original spec but needed before handing this to a
second machine: a required `--machine` label (output folders must never default to a stale/wrong
machine name again) and `--out` support so a run can be routed straight into `private-test-debugs`
via `--out $BenchOut`, matching the convention every other `benchmark_*.py` already uses
(`.claude/commands/BenchmarkCommands.md` updated to match). A synthetic `--self-test` mode (no audio,
no model) validates the new math in seconds. Commits: `3e488bf`, `5cd6910`.

> ⚠️ **Process note, unresolved:** these commits landed on `ui-improvement-bulk-run`, not
> `prompt-improve`. §11.6 rule 1 says this initiative's branch is `prompt-improve` only. This wasn't
> caught until writing this section. The push itself was explicitly requested by the owner in-session
> (satisfying the "no push without explicit instruction" half of the rule), but the branch choice was
> not — flag this to the owner; either move the commits or explicitly amend the rule for
> benchmark-tooling-only changes. Do not silently repeat this on the next benchmark-script edit.

**jp-start ran the repaired harness today** (`--no-frozen-reference --machine jp-start`, all 5
fixtures) — comparison-only, per §11.2. This is **not** Phase 0B (the 3× noise-floor control); it's a
single-pass reproduction of the 2026-08-01 comparison with trustworthy instrumentation this time.
Output (after correcting an initial `it436365` mislabel caused by a copy-paste of the wrong
`--machine` value — same class of error as §11.8.4/§3.3, caught before it reached git):
`private-test-debugs\benchmark_results\live-slice-replay-06082026-jp-start\`.

**Result — leans toward reproducing the 2026-08-01 kill, on every fixture:**

| Fixture | Missing spans ≥5w (gate: 0) | Speech coverage (gate: ≥99%) | Repetition incidents: serial → stitched |
| --- | ---: | ---: | ---: |
| 31-min | 3 (5,7,9w) | **98.39%** ❌ | 0 → 18 |
| 45-min | 3 (6,5,13w) | 99.4% | 6 → 15 |
| 49-min | 1 (7w) | 99.6% | 4 → 16 |
| 51-min | 4 (5,9,5,5w) | 99.18% | 13 → 20 |
| 38-min | 2 (**26w**,8w) | 99.04% | 2 → 11 |

13 missing spans total across the 5-fixture set against a gate of zero; every fixture's repetition
count rose over its own serial baseline (25 → 80 summed); word delta is positive on all 5 (+4.84% to
+8.18%), consistent with insertion/repetition, not content thinning. **The single item needing owner
classification, not a model's:** `counselling-38-min` has a 26-word missing span whose context
mentions hospitalization — exactly the history/intervention content class §5's gate names by name.
Per T4's own rule, only the owner rules a span clinically material, and the ruling must be recorded
with its reasoning so it isn't re-litigated.

**What this does and does not establish, per the rules already in this file:** jp-start is
comparison-only (§11.2) — this result does not close T4 by itself; IT436365's run is what governs.
It is also not yet Phase 0B's noise floor, so how much of the 13 missing spans reflects genuine
live-stitching damage versus ordinary serial-decode variability is not yet separable — though the
same two defects (missing content + elevated repetition) appearing on **every single fixture** is a
harder pattern to explain as pure noise than a one-off would be.

**IT436365's run landed the same day**, after a one-time fix (that laptop had never run this workflow
before — `PRIVATE_AI_DEBUG_DIR` was unset; clone `private-test-debugs` if absent, set the env var,
**restart the shell before re-checking**, a same-session re-check falsely shows it still unset). This
is the machine that actually decides T4's fidelity gate (§11.2) — jp-start above is comparison-only.

| Fixture | Missing spans ≥5w (gate: 0) | Speech coverage (gate: ≥99%) | Repetition: serial → stitched |
| --- | ---: | ---: | ---: |
| 31-min | 1 (49w — reads as a serial-side Whisper repetition/hallucination artifact on its own content, not obviously lost real speech, but still trips the numeric gate; needs the same owner look as everything else here) | **98.54%** ❌ | 7 → 8 |
| 45-min | 1 (7w, casual conversational filler) | 99.53% | 6 → 5 |
| 49-min | 1 (45w — coherent content about prognosis / "not getting better," a content class worth owner review) | **97.91%** ❌ | 5 → 11 |
| 51-min | **6** (includes the self-harm/cutting span flagged above, plus a debriefing-related span) | 99.2% | 9 → 15 |
| 38-min | 1 (5w, substance-use / hospital-visit content) | 99.75% | 2 → 6 |

10 missing spans total (gate: 0); **2 of 5 fixtures fail the speech-coverage gate outright**
(31-min, 49-min); repetition rose on 4 of 5 fixtures (45-min is the one exception, 6→5). This is a
harder failure than jp-start's — more total spans concentrated on fewer fixtures (6 on `51-min`
alone), and it includes the one span that fails the gate on content class rather than needing any
statistical argument at all.

**What this changes.** IT436365 is the machine whose number governs (§11.2, §11.9's own convention
for T7b.0/T7c). Combined with jp-start's independent same-direction result (§11.12 above), two
machines now agree: content is lost and repetition rises under this stitching design, on every
fixture tested on either machine. This is **not yet Phase 0B's noise floor** (3× serial repeat, still
unbuilt — §4.0B), so the exact attribution split between "live-stitching mechanism" and "ordinary
Whisper variability" is still formally open for the numeric-count spans. **The self-harm span is not
subject to that caveat** — §5's absolute clinical gate is explicitly noise-floor-independent, and nothing
about running Phase 0B would change whether that span disqualifies the current design.

#### Owner ruling — RULED 2026-08-06, `counselling-51-min`, IT436365 (§4.0B's classification requirement)

**T4 is `[x] — REJECTED`.** Owner review of the IT436365 `counselling-51-min` fixture found four
independent transcript-gate failures, any one of which is disqualifying on its own per §5:

1. **Negation reversal.** "It did help" is rendered as "It didn't really help" in the stitched
   transcript, and other positive answers are similarly flipped to negative. This is the clearest
   possible instance of §5's named `negation` content class — disqualifying on its own, with no
   dependence on content severity or the self-harm finding below.
2. **Relocated self-harm/cutting content.** The span already flagged above in this section, describing
   self-harm/cutting behaviour, is not merely present but has moved out of its original position during
   stitching. Fails §5 "at any percentage, at any noise floor."
3. **Completeness.** A missed speech gap of up to 19 seconds, on top of 335 additional words versus the
   serial baseline for this fixture — consistent with insertion/duplication rather than faithful
   transcription.
4. **Repetition-loop containment (§4.4's independent gate).** One chunk repeats "I'm not" approximately
   16 times — the same generalising repetition-loop failure mode §4.4 already expected from the
   2026-08-01 run (5/5 fixtures failed there).

**Why this does not wait for Phase 0B.** §4.0B's exit table is explicit that an absolute-clinical-gate
failure stops the process regardless of the noise floor — negation reversal and relocated risk-content
are not statistical questions a 3×-serial noise-floor run could excuse. Phase 0B remains valuable for a
narrower, separate reason: checking whether the *same* defects already exist in currently shipped serial
transcription (§4.0B's fourth outcome row) — an independent product-reliability question, not a T4
question, and not a precondition for this ruling.

**What closes and what doesn't.** T4 as designed — 1 s overlap, timestamp-trim stitch (§4.0A/Phase-0A
configuration only) — is closed. The overlap-sweep and bridge-window mechanisms (§4.2/§4.3) were
designed to test whether more context around cut points fixes exactly this class of error; they remain
theoretically available as a **new** candidate, but must be tested from scratch against §5's full gate
set — this ruling is neither evidence for nor against a wider-overlap variant, and reopening is not a
rerun of Phase 0A's configuration.

---

### 11.13 Plain-language status as of 2026-08-06 — ARCHIVED, not the instruction

> **📁 Archive.** Superseded by the **Current Status** block at the top of this file, which carries
> the same content plus the Sol Max review corrections. Kept because its plain-language framing is
> useful for explaining the initiative to a non-specialist. Do not update it — update the top block.

**Read this first if you are picking this up cold.** Plain language, no jargon assumed. Tri-state:
`[x]` done · `[~]` in progress / partial · `[ ]` not started.

#### What's actually settled

- `[x]` **Tuning the AI engine's own knobs** (how much it "thinks" before answering, batch sizes,
  a GPU-acceleration feature called Flash Attention, thread counts, a lightweight prediction trick
  called n-gram speculation) — all tried, none gave a real, keepable speed win. Closed.
- `[x]` **Using the graphics chip (iGPU) to help write the note (Beautify)** — crashes on this
  hardware/software combo, and even in the one mode that doesn't crash, it's not faster. Closed.
- `[x]` **Using the graphics chip to help transcribe speech** — tested properly on both laptops,
  doesn't clear the bar that would justify building it. Closed.
- `[x]` **Getting a head start on note-writing while transcription is still running** — tried on
  both laptops, and on a CPU-only machine there's no such thing as free multitasking: it just steals
  time from transcription and gives back slightly less than it took. Closed on both machines. (One
  narrow variant — starting that head start only *after* the counsellor presses Stop and before they
  click Beautify — is still an open, unmeasured idea, not the same thing as what was just closed.)
- `[x]` **"Draft-ahead" prediction for note-writing (MTP)** — this one works. Real, measured
  18–24% faster note-writing, and it helps *more* on weaker/cheaper laptops, which is good news since
  that's most of the real customer fleet. It's already shipped and on by default.
- `[x]` **Live transcription during the session** (writing text as the counsellor talks, instead of
  waiting until they press Stop) — **REJECTED by owner ruling, 2026-08-06.** Real review of the
  IT436365 `counselling-51-min` result found four separate disqualifying problems in one fixture: a
  positive answer flipped to a negative one ("it did help" became "it didn't help"), a piece of
  self-harm-related content that moved to the wrong place in the transcript, roughly 19 seconds of
  missed speech, and one place where the transcript got stuck repeating "I'm not" about 16 times. Any
  one of these alone would be disqualifying for clinical use. Closed — full reasoning in §11.12.

#### What's still open

- `[~]` **Confirming MTP's draft-ahead prediction doesn't quietly change note quality or clinical
  accuracy.** The speed win is proven; whether it's safe to leave on by default for real clinical
  notes has not been independently confirmed by a practitioner yet. This is the single most important
  open item — it blocks a shipping decision on something already live.
- `[x]` **Actually building live transcription into the app** (the part that would touch real code,
  called AudioWorkletNode) — **does not happen.** It was locked behind live transcription passing its
  fidelity review; that review failed (see above), so Phase 6 of the execution plan stays locked
  permanently for this candidate. Reopening requires a genuinely new stitching mechanism tested from
  scratch, not a continuation of this one.
- `[ ]` **Testing on a laptop that matches the real customer fleet** (a specific mid-range Intel
  chip, 16 GB RAM) — nobody has one available right now. Not blocking anything else, just an
  eventually-needed confirmation.

#### Next tests to execute — in order, written so a different model/session can run these cold

1. `[x]` **DONE 2026-08-06 — owner review of `counselling-51-min` on IT436365.** Ruled REJECTED on four
   independent grounds (negation reversal, relocated self-harm content, a 19 s missed-speech gap, a 16×
   repetition loop). Full reasoning recorded in §11.12's "Owner ruling" block. T4 as designed is closed.

2. `[ ]` **Still open, but no longer gating anything.** The other three coherent-content spans in
   §11.12 (jp-start `counselling-38-min` hospitalization-adjacent span, IT436365 `counselling-49-min`
   prognosis span, IT436365 `counselling-38-min` substance-use span) have not been individually ruled.
   T4 is already closed on step 1's finding alone (§5: one critical loss is `KILL` regardless of what
   else is measured), so classifying these no longer changes T4's outcome. They remain worth a one-line
   disposition each — mainly for the production-defect angle in item 6 below, not for T4.

3. **IT436365 MTP determinism check — free, no new run, ~5 minutes of reading.** Separate track from
   T4; does not need to wait for #1–2. On the IT436365 laptop, open the two existing result folders:
   `private-test-debugs\benchmark_results\cpu-mtp-audio-qualification-04082026-it436365-v9-repeatability`
   and `...-v9-continuation-05082026`. For each fixture, find the three `no_mtp` condition rows and
   compare their `output_sha256` values (exclude v9 row 12, an interrupted run). All three identical
   per fixture → the engine is deterministic at a fixed seed there, and MTP-vs-no-MTP comparisons can
   be trusted byte-for-byte. Any difference → record it, and treat every MTP quality comparison as
   mechanism-only, not byte-identity. **Write the outcome into §11.11.3 item 1 of this file.**

4. **MTP blind practitioner review** (§11.11.3 item 2) — rescoped question is *"are these notes
   clinically acceptable?"*, not *"is MTP worse?"*, scored against Source. Give the pre-existing
   incomplete-Risk-Level finding (§11.10, 4 of 6 fixtures) at least equal weight to the MTP question
   itself. Needs the owner's or a practitioner's clinical-review time — cannot be executed by a model.
   Independent of T4; does not need to wait for #1–2 either, though it draws on the same scarce
   clinical-review time, so sequence with the owner rather than assuming both fit in one sitting.

5. **Two counterbalanced real-application MTP rows** (§11.11.3 item 3) — only after step 4 clears.
   Reuse the frozen ~45-minute recording's existing Source; never re-transcribe it. Check whether
   `activity_log`'s existing `beautify-single` timestamps already give Source→durable-draft before
   building new renderer instrumentation (§11.10's blocker was an unavailable renderer surface, not a
   design flaw).

6. **T4 Phase 0B (noise floor)** — **no longer T4 work.** T4 is closed on step 1's ruling regardless of
   what Phase 0B would show. Its only remaining value is the production-reliability question: whether
   the same defect classes (negation reversal, content relocation, missed spans, repetition loops)
   already exist in currently *shipped* serial transcription (§4.0B's fourth outcome row) — a separate,
   potentially higher-priority defect against production, unrelated to whether T4 itself ships. Not yet
   built; `.claude/plan/TranscribeBeautifyAudioWorkletNode.md` §4.0B has the exact method (3× serial
   decode per fixture on IT436365, diffed pairwise). Re-prioritise independently of T4.

7. **Write the summary reports.** `benchmark-reports\JP-START-i7-T4-Phase0A-LiveSliceReplay-06082026.md`
   and `benchmark-reports\IT436365-i5-T4-Phase0A-LiveSliceReplay-06082026.md` — data for both is now in
   hand (§11.12), same format as the existing files in that folder (git-tracked, narrative only, no
   raw transcript content, content-class descriptions only for the flagged spans). Record the REJECTED
   ruling and its four grounds, not just the missing-span counts.

**Step 1 is done.** Steps 3–5 are independent MTP-track work and proceed on their own schedule; step 2
and step 6 are now optional production-reliability follow-ups, not T4 work; step 7 (the summary
reports) is the only remaining T4-specific action.

