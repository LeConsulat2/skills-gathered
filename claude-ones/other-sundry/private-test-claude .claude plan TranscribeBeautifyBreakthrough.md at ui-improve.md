# private-test-claude/.claude/plan/TranscribeBeautifyBreakthrough.md at ui-improvement-bulk-run · LeCo

[github.com](https://github.com/LeConsulat2/private-test-claude/blob/ui-improvement-bulk-run/.claude/plan/TranscribeBeautifyBreakthrough.md)

> What is the current status of the **PRIVATE Transcribe & Beautify** initiative? The **live transcription** feature is officially rejected due to clinical safety failures, while **MTP draft-ahead decoding** is confirmed as a stable, shipping speed improvement.

## 1. Document Control and Current Status Baseline 

### 1.1 Maintenance Rules and Document Hierarchy 

> 💡 **Strict Document Maintenance Protocol**
>
> This section is strictly **overwritten** and never appended to. It acts as the single entry point so its location remains static. Olddated handovers or additional "start here" banners are prohibited.

- **Document Structure Rules:**
  - Sections §1 through §11.13 serve as the **evidence archive** documenting past execution runs. 
  - The evidence archive is an unalterable historical record that should be cited rather than handed over as active instructions. 

![](https://resource.lilys.ai/images/genimg_8079711eadb33058.png)

### 1.2 One-Line Status Summary 

- **Search Space Exhaustion:** Both engine-flag and GPU search spaces are fully measured and exhausted. 
- **Shipped Acceleration:** CPU-MTP (Multi-Token Prediction) is the sole mechanism that proved effective and is shipped. 
- **Critical Path:** The remaining bottleneck is human clinical validation to confirm that note outputs meet clinical standards. 

### 1.3 Settlement Matrix 

The following table summarizes levers that are closed and must not be reopened without a genuinely new mechanism: 

| Closed Lever | Reason for Closure | Location in Archive |
| :--- | :--- | :--- |
| Reasoning budget, ubatch, Flash Attention, upward threads, n-gram speculation | All measured with no net performance win | §11.11.1, `053`/`054` |
| Batched Whisper | Omits clinically material speech | `055` §0C |
| Transcript Preparation Phase 0 | Prepared Source output is 4.5%–11.1% larger | `TranscriptPreparation.md` |
| Gemma iGPU / Vulkan / `-ngl` Target Placement | Iris Xe shares system DRAM; offload buys no memory bandwidth while prefill remains bandwidth-bound | §11.11.1 |
| whisper.cpp GPU arms (T7b.0) | Reached a 13.93%–16.88% journey ceiling vs. a ≥20% threshold gate | §11.9 |
| T7d Concurrent Prefill during Whisper | No free concurrency on a CPU-only stack; failed on both machines within 0.6 s net difference | §11.11.6 |
| **T4 Live Transcription (1 s overlap, timestamp-trim stitch)** | **REJECTED 2026-08-06**: Negation reversals, relocated self-harm spans, 19 s missing speech gap, and 16× repetition loops | §11.12, `TranscribeBeautifyAudioWorkletNode.md` §11 |
| Reasoning-off | **Owner decision** (not an engineering closure); timing was clean but lever declined | `055` §0B |

- **Shipped CPU-MTP Details:** 
  - Implements draft-ahead decoding on CPU. 
  - Automatically enabled when the draft GGUF file is present. 
  - Delivers **18%–24% faster note generation**, with benefits scaling inversely with machine strength. 
  - Kill switch environment variable: `PRIVATE_AI_DISABLE_MTP=1`. 

---

## 2. Priority Queue and Active Investigations 

### 2.1 Ranked Task Queue 

1. **`[~]` MTP Blind Practitioner Review (Critical Path):** 
   - **Core Question:** Rescoped to *"Are these notes clinically acceptable?"* rather than *"Is MTP worse?"* 
   - **Execution:** Scored against Source on a blinded mixed set from both arms. 
   - **Weighting:** Gives equal weight to the pre-existing incomplete Risk Level finding (affecting 4 of 6 fixtures). 
   - **Constraint:** Blocks shipping decisions on live features; requires human clinical evaluation. 

2. **`[ ]` IT436365 MTP Determinism Check:** 
   - Compare three `no_mtp` `output_sha256` values per fixture across both `cpu-mtp-audio-qualification-04082026-it436365-v9-*` folders. 
   - **Status Warning:** `jp-start` **FAILED** this check (differing hashes at temperature 0.0 with a pinned seed). 
   - If IT436365 also fails, byte-identity testing is ruled out for future A/B evaluations. 

3. **`[ ]` Fix `word_diff_report` Replace Blindness:** 
   - Correct `benchmark_live_slice_replay.py:433-469`, which only counts `delete` and `insert` opcodes. 
   - It is structurally blind to negation flips (the defect that invalidated T4). 
   - Add a unit test verifying that every segment belongs to exactly one official interval. 

4. **`[ ]` Two Counterbalanced Real-Application MTP Rows:** 
   - Requires Item 1 to pass first. 
   - Reuse frozen ~45-minute Source audio without re-transcribing. 
   - Verify if `activity_log` timestamps (`beautify-single`) yield Source→durable-draft metrics before writing renderer instrumentation. 

5. **`[ ]` Write T4 Phase 0A Summary Reports:** 
   - Save narrative-only summary reports into `benchmark-reports/`. 
   - Exclude raw transcript content; include content-class descriptions only. 

6. **`[ ]` CTranslate2 4.8.x Packed GEMM Experiment:** 
   - Environment is pinned to `ctranslate2 4.7.2` / `faster_whisper 1.2.1`. 
   - Upstream 4.8.0 enables Intel MKL packed GEMM (~23% speedup on `int8_float32` microbenchmarks). 
   - Transcription accounts for 38.7%–44.1% of runtime, yielding an estimated ≈9%–10% total clock reduction (~30 s on a 45-min session). 
   - Execute in an isolated environment using one frozen fixture without in-place upgrades. 

7. **`[ ]` Production-Reliability Baseline Audit (Repurposed from T4 Phase 0B):** 
   - Audit whether defect classes (negation reversals, relocations, missed spans, repetition loops) exist in currently shipped serial transcription. 
   - Methodology: Run 3× serial decode per fixture on IT436365 and perform pairwise diffs. 

8. **`[ ]` 135U / 16 GB Fleet Qualification:** 
   - Deferred until hardware is physically available; does not block preceding queue items. 

---

## 3. Review Corrections and Operational Rules 

### 3.1 Sol Max 5.6 Review Findings 

> 💡 **T4 Harness Stitching Defect Analysis**
>
> An audit revealed that adjacent audio slices shared 2 seconds of overlap instead of 1 second, and the ownership rule (`mid < official_start`) lacked a matching upper boundary (`mid >= official_end`). This caused right-hand overlaps to be kept twice and sorted globally, leading to 2,217 decoded segments with zero trims executed.

- **Impact Analysis:** 
  - Explains word inflation, repetition loops, and relocated text spans. 
  - Does **not** explain the ~19–20 s missed speech gap or sub-99% speech coverage on 2 of 5 fixtures. 
  - Rejection stands: the specific configuration is unsafe, though audio slicing itself remains unproven as fundamentally flawed. 

- **Subsystem Status Corrections:** 
  - **AudioWorklet:** Status is UNTESTED rather than rejected. Recorders currently invoke bare `mediaRecorder.start()` without timeslices. 
  - **pydub:** Declared a NO-GO because it operates at the wrong abstraction layer and cannot preserve Whisper token histories, prompts, or VAD states. 
  - **Live ASR Path Forward:** Any future reopening requires a checkpointable `faster-whisper` loop preserving decoder state, gated on exact offline identity. 

### 3.2 Standing Rules and Constraints 

- **Machine Baseline Rule:** `jp-start` is for comparative analysis only. `IT436365` provides decision-grade evidence. Never average or merge metrics across machines. 
- **Harness Pinning:** Always pin `PRIVATE_AI_SEED` across all benchmark runs. 
- **Control Arm Requirement:** Run a within-condition control arm before evaluating cross-condition changes. 
- **Harness Integrity:** Extend validated contract harnesses; do not execute custom scripts in `tmp/`. 
- **PHI Containment:** Prohibit PHI in tracked files; retain flagged text in gitignored `private-test-debugs` paths. 
- **Branch Strategy:** Work exclusively on `prompt-improve`. (Note: Phase 0A commits `3e488bf` and `5cd6910` landed on `ui-improvement-bulk-run` and require owner reconciliation). 

### 3.3 Companion Document Reference Matrix 

| Document | Operational Role |
| :--- | :--- |
| `TranscribeBeautifyAudioWorkletNode.md` | **Closed Sub-Plan:** Contains T4 execution history and rejection rulings.  |
| `thoughts/SolMaxReview.md` | **Review Document:** Actionable findings are promoted into the main plan.  |
| `benchmark-reports/temp-handover-for-i5.md` | Machine-specific operational extract for IT436365.  |

- **Project Metadata:** Created 1 August 2026; overall initiative status is **ACTIVE**. Primary sources of truth are `CLAUDE.md`, `thoughts/AfterSolMaxAndFable.md`, and `bugs-fixed/056-01082026(NewFindings).md`. 

---

## 4. Operating Contract and Core Protocol 

### 4.1 Task State Notation 

- `[ ]` **NOT STARTED** 
- `[-]` **ACTIVE** (Maximum of 3 concurrent active tasks permitted) 
- `[x]` **COMPLETE** (Requires finished evidence, tests, result documents, registry updates, and focused commits) 

### 4.2 Non-Negotiable Execution Protocol 

1. Maintain production defaults until all named gates pass. 
2. Treat `examples/`, `examples-raw/`, and `C:\Users\wooin\Documents\private-test-debugs\benchmark_results` as strict read-only resources. 
3. Write new raw execution logs under `backend/benchmark_results/<experiment-id>/`. 
4. Invoke Python benchmarks using unbuffered output via the project venv: `backend\env\Scripts\python.exe -u ...`. 
5. Verify process states explicitly; silent output redirection does not indicate process termination. 
6. Do not attribute external process terminations to security tools (EDR) without explicit system logs. 
7. Rerun closed candidates only when presenting a novel reopening mechanism. 
8. Execute minimum decisive tests before running matrix expansions; terminate early upon gate failure. 

### 4.3 Mandatory Task Execution Workflow 

> 💡 **Pre-Execution Protocols**
>
> - Document exact hypothesis and isolated variable lever. 
> - Define speed threshold or declare an explicit reliability ruling. 
> - Document transcript and note quality kill conditions. 
> - Record hardware, power plan, thermal baseline, and model hashes.

> 💡 **Post-Execution Protocols**
>
> - Validate manifest attestation before processing timing logs. 
> - Perform output diff analysis under §3 rules. 
> - Assign task outcome (`CONTINUE`, `SHIP`, `KILL`, or `BLOCKED`). 
> - Update registry log and execute a single phase commit.

---

## 5. Objective Metrics and Fleet Clocks 

### 5.1 Governing Product Objective 

> Minimise predictable time from Stop to a **durably saved reviewable draft**, and minimise the time the practitioner is attention-locked, on the weakest representative supported hardware, subject to zero regression in Source fidelity, clinical attribution, inspectability, and crash recovery. 

### 5.2 Mandatory Timed Clocks 

1. **Clock 1:** Stop → Exact editable Source durably committed. 
2. **Clock 2:** Source committed → First visible draft text. 
3. **Clock 3:** Source committed → Reviewable draft durably saved. 
4. **Clock 4 (Governing Metric):** Stop → Reviewable draft durably saved. 
5. **Clock 5:** Start/Stop → User safely free to navigate or perform non-AI tasks. 

---

## 6. Shared Quality Protocol and Evidence Contracts 

### 6.1 Quality Verification Gates 

```
[ ASR / Output Candidate ]
           │
           ▼
 ┌───────────────────┐
 │  Transcript Gate  │ ──► Coverage ≥ 99%, 0 missing ≥5-word spans, 0 clinical omissions
 └─────────┬─────────┘
           │ Pass
           ▼
 ┌───────────────────┐
 │  Generated-Note   │ ──► Step 2: Establish within-condition control reproducibility (n≥2)
 │       Gate        │ ──► Step 4: Risk-directed Source<->output diff check
 └─────────┬─────────┘
           │ Pass
           ▼
 ┌───────────────────┐
 │ Reliability Gate  │ ──► Zero audio loss, idempotent recovery, clean cancellation
 └───────────────────┘
```

- **Transcript Quality Requirements:** 
  - Minimum timeline coverage of 99%. 
  - Zero contiguous missing speech spans of 5+ words. 
  - Zero omissions of risk factors, medications, dates, or clinical qualifications. 
  - Zero whole duplicated exchanges or repetition loops. 

- **Generated-Note Verification Funnel:** 
  - **Mandatory Step 2 Control Arm:** Evaluate control vs. control using identical inputs and pinned seeds ($n \ge 2$). If control outputs are non-identical, between-condition text diffs cannot be attributed to the lever. 
  - Check finish reasons, truncation, heading orders, and export structure. 
  - Perform risk-directed Source↔output diff checks covering clinical facts, safety, and dates. 
  - Use opaque case IDs and blinded key custody. 

- **Reliability Specifications:** 
  - Audio and Source data must never be lost. 
  - Source must commit to storage prior to draft generation. 
  - System recovery must be idempotent, resolving to exactly one session state. 

### 6.2 Evidence Contract Standards 

Every run requires a pre-execution specification hash and a post-execution manifest attestation: 

- **Preregistration Spec Requirements:** Experiment ID, single lever under test, target hardware parameters, full scheduled row matrix, bounded thermal stabilization duration, and exact SHA-256 hashes for all input binaries, models, prompts, and audio. 
- **Postflight Attestation Requirements:** System topology, power plan, load state, git commit hash, clean/dirty state, full startup flags, parsed effective runtime parameters, and output file hashes. 
- **Validation Rule:** Timing metrics are ignored if the validator returns anything other than `VALID`. 

---

## 7. Execution Ledger and Primary Handoff Queue 

### 7.1 Execution Ledger 

- **[x] T0 — Evidence Contract Validator and Audit:** 
  - Delivered schema/validator tooling. Legacy runs ruled `LEGACY-INCOMPLETE` due to missing environment attestations. Speed effect: 0 s. Result: `SHIP`. 

- **[x] T1P — Borrowed-i5 Integration & Handoff Validation:** 
  - Integrated `PENDING-REVIEW` state for runs awaiting human review. Speed effect: 0 s. Result: `SHIP`. 

- **[x] T1 — Weak-Tier Minimum Decisive Journey (IT436365):** 
  - Measured cold Stop→draft time of 611.6 s (~10.2 min) on a 43.5-min recording (transcription: 34.4%, Beautify: 65.6%). Result: `PENDING-REVIEW`. 

- **[x] T2 — Durable-Job Force-Kill & Relaunch Verification:** 
  - Demonstrated that background auto-resume after app relaunch was unviable. Implemented `cleanup_interrupted_structuring()`, which cleans orphaned queue items in 2,030 ms without auto-triggering background model work. Result: `SHIP`. 

- **[x] T4 — Live Transcription Boundary Reconciliation:** 
  - **REJECTED 2026-08-06.** Failed on negation reversal ("It did help" → "It didn't really help"), relocated self-harm spans, 19 s missing speech gap, and 16× repetition loop. 

- **[x] T6 — Reasoning-Off Reconsideration:** 
  - Re-declined by owner due to output quality regressions. Closed. 

### 7.2 Heterogeneous CPU+iGPU Acceleration Track (T7) 

- **T7 Track Rules:** Backend selection is workload-specific. Gemma target offloading is closed. Dual-run comparisons must establish same-machine controls. 

- **[x] T7a — Partial Layer Offload (`-ngl`):** 
  - **STOPPED.** `-ngl 18` triggered assertion crashes (`GGML_ASSERT(n_inputs < GGML_SCHED_MAX_SPLIT_INPUTS)`), while `-ngl 999` slowed execution on Iris Xe hardware. Closed. 

- **[ ] T7b.0 / T7b — whisper.cpp CPU & iGPU Screen:** 
  - **T7b.0 CPU:** Measured encoder share at 40.5%–52.1%, establishing a maximum journey speedup ceiling of 13.9%–16.9% on IT436365 (below the 20% gate). 
  - **T7b GPU Arms (OpenVINO / Vulkan):** Closed because the theoretical maximum gain fails to meet the 20% threshold gate. 

- **[ ] T7c — Gemma 4 E2B Multi-Token Prediction (MTP):** 
  - Evaluated CPU Target + CPU Draft vs. CPU Target + iGPU Draft. 
  - **IT436365 Execution Results:** CPU draft reduced Beautify wall-clock time by **24.0%** (237.7 s → 180.9 s) with 51.85% acceptance. 
  - iGPU draft achieved 189.9 s (-20.1%) due to cross-device synchronization overhead. CPU draft is the primary configuration. 

- **[ ] T7d — Progressive Transcript-Prefix Prefill Overlap:** 
  - **Stage A (Mechanism):** Successfully pre-cached up to ~81% of prompt tokens. 
  - **Stage B (Concurrent Execution):** **FAILED on both machines.** Concurrent prefill slowed Whisper by +53% to +58%, resulting in net journey time losses (−7.7 s on i5, −7.1 s on i7). Concurrent execution is closed. 

---

## 8. Summary Master Evidence Registry 

| ID | Task Description | Target Machine | Contract Verdict | Final Decision | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HIST-056-IT-WHISPER | Whisper 5-fixture baseline | IT436365 (i5-1135G7) | `LEGACY-INCOMPLETE` | Descriptive baseline | Historical |
| HIST-056-IT-BEAUTIFY | Beautify 12-row baseline | IT436365 (i5-1135G7) | `LEGACY-INCOMPLETE` | Descriptive baseline | Historical |
| HIST-056-IT-THREADS | Thread count sweep | IT436365 (i5-1135G7) | `LEGACY-INCOMPLETE` | No lever found | Historical |
| HIST-056-LIVE-1S | Live slice replay (~1s) | JP-START (Core 7 240H) | Legacy | `KILL` | Closed |
| T0-20260801 | Evidence contract & audit | JP-START (Core 7 240H) | `VALID` | Tooling `SHIP` | Complete |
| T1P-20260802 | i5 Journey Runner Tooling | JP-START (Core 7 240H) | N/A (Tooling) | Tooling `SHIP` | Complete |
| T1-20260802 | Weak-tier journey baseline | IT436365 (i5-1135G7) | `PENDING-REVIEW` | Measured floor (611.6 s) | Complete |
| T2-20260802 | Force-kill recovery audit | JP-START / IT436365 | 8/8 Assertions PASS | `SHIP` (Cleanup strategy) | Complete |
| T7b0-20260804 | whisper.cpp CPU split | IT436365 (i5-1135G7) | Valid | Ceilings < 20% gate; GPU closed | Complete |
| T7c-20260804 | Gemma CPU-MTP qualification | IT436365 (i5-1135G7) | Valid | **24.0% Beautify wall win** | Complete |
| T7d-20260805 | Concurrent prefill Stage B | JP-START & IT436365 | Valid | `KILL` (Net negative time) | Closed |

---

## 9. Next Action Instructions for Cold Sessions 

1. **Perform IT436365 MTP Determinism Audit:** Verify internal output hash identity across the 3 `no_mtp` repetitions in the v9 result folders to determine if temperature 0.0 outputs are byte-identical. 
2. **Execute MTP Blind Practitioner Review:** Conduct a blinded clinical review of CPU-MTP draft outputs focusing on factual accuracy, risk flags, and missing section rates. 
3. **Run Real-Application Counterbalanced MTP Validation:** Execute 2 real-application journey runs using frozen transcript sources to capture end-to-end Stop→draft clocks. 
4. **Publish Final T4 Narrative Reports:** Complete narrative summary reports for T4 Phase 0A in `benchmark-reports/` without committing raw transcript PHI.
