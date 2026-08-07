# Benchmark Commands

Read this file when: running any `backend/tests-benchmarks/benchmark_*.py` script (moved out of flat
`backend/` on 2026-08-05, alongside `test_*.py` moving to `backend/tests/`). Output must land in the
separate `private-test-debugs` repo, **never** in this repo's `backend/benchmark_results/`.

> **Override closed (2026-08-02).** The 2026-08-01 override below that named
> `backend/benchmark_results/<experiment-id>/` as the writable root for the active
> Transcribe & Beautify breakthrough initiative is **rescinded.** A real counselling-audio file and
> encrypted-DB test artifacts (`local_private.db` + `db_keys.json`) were swept into that directory
> and committed/pushed on 2026-08-02 (`a4c1526`, `b92cb29`) — see
> `bugs-fixed/060-02082026.md` for context and `WhatWasDone/10-MustBeDone.md` for the git-history
> purge this triggered. **The owner has named the writable evidence root: it is
> `%USERPROFILE%\Documents\private-test-debugs\benchmark_results`, effective immediately, on every
> laptop.** Every `benchmark_*.py` invocation from now on must pass `--out $BenchOut` (computed
> below) or, for the two scripts with no `--out` flag, move its output there immediately after the
> run, before anything gets committed. `backend/benchmark_results/` is gitignored again — if a run
> lands there anyway (a script without `--out` support, or `--out` omitted), **move it, do not
> commit it,** before touching git.
>
> Every benchmark Python invocation must include `-u`; a quiet redirected file is not evidence that
> the process died. The rolling plan and evidence contract are in
> `.claude/plan/TranscribeBeautifyBreakthrough.md` — its evidence-root references are being updated
> to match; where they still say `backend/benchmark_results/`, treat that as a historical pointer to
> content that has since moved to `private-test-debugs` (or been purged from this repo's history),
> not as a currently-writable path in this repo.

---

## Prerequisite

`PRIVATE_AI_DEBUG_DIR` (User env var) must already point at the `debug` subfolder of your local `private-test-debugs` clone, e.g.:

```powershell
[System.Environment]::GetEnvironmentVariable('PRIVATE_AI_DEBUG_DIR', 'User')
# -> C:\Users\<you>\Documents\private-test-debugs\debug
```

This only redirects `backend/services/ai.py`'s `debug/` artifact writer. It does **not** touch benchmark output — every `benchmark_*.py` script hardcodes `backend/benchmark_results/` as its default and only writes elsewhere if you pass `--out` on that run.

All commands below run from `backend/` using the project's own venv (never a system Python). Scripts
live in `tests-benchmarks/`, so every invocation below is prefixed `tests-benchmarks\` — CWD stays
`backend/` throughout, so `--out`/`--repo-root`/`benchmark_results\...` paths are unaffected:

```powershell
cd backend
```

Compute the sibling `benchmark_results` folder once per shell session (derives from `PRIVATE_AI_DEBUG_DIR` so this works unchanged on either laptop):

```powershell
$BenchOut = Join-Path (Split-Path $env:PRIVATE_AI_DEBUG_DIR -Parent) "benchmark_results"
```

---

## Scripts that support `--out` (redirect works)

```powershell
env\Scripts\python.exe -u tests-benchmarks\benchmark_beautify_first_run.py --mode all --out $BenchOut

env\Scripts\python.exe -u tests-benchmarks\benchmark_beautify_reasoning.py --mode all --out $BenchOut

env\Scripts\python.exe -u tests-benchmarks\benchmark_prompt_baseline.py --label pre-hardening --out $BenchOut

env\Scripts\python.exe -u tests-benchmarks\benchmark_whisper_threads.py <path-to-audio-clip> --label <machine-label> --out $BenchOut

env\Scripts\python.exe -u tests-benchmarks\benchmark_whisper_batched.py --label <machine-label> --out $BenchOut

env\Scripts\python.exe -u tests-benchmarks\benchmark_live_slice_replay.py --machine <machine-label> --out $BenchOut
```

Each script nests its own timestamped/labelled run folder under whatever `--out` you give it, so `$BenchOut` only needs to be the top-level `benchmark_results` folder, not a per-run path. `benchmark_live_slice_replay.py` additionally **requires** `--machine` on every real run (not needed with `--self-test`) — it refuses to run without one, so an output folder can never default to a stale or wrong machine label. It also has a `--self-test` mode (no audio, no model) that validates the harness's own coverage/repetition math in seconds — run this before any real run, especially on a machine that hasn't run it before.

Run `<script>.py --help` for the full flag list (fixtures, mode, reps, model, seed, etc.) — this doc only covers output routing, not every benchmark's own options.

## Scripts with NO `--out` flag (hardcoded output — cannot redirect)

```powershell
env\Scripts\python.exe -u tests-benchmarks\benchmark_warm_start_spike.py
```

This always writes under `backend\benchmark_results\<run-name>\` regardless of `PRIVATE_AI_DEBUG_DIR` or anything else. To get the result into `private-test-debugs`, move it manually afterward, e.g.:

```powershell
Move-Item backend\benchmark_results\warm-start-spike-* $BenchOut\ -Force
```

(If this becomes a recurring annoyance, this script's `OUT_DIR` constant near the top of the file could be changed to read an env var fallback — not done as of 2026-08-01. `benchmark_live_slice_replay.py` got exactly this treatment on 2026-08-06, per T4 Phase 0A — see `.claude/plan/TranscribeBeautifyAudioWorkletNode.md` §4.0A.)

## Evidence-contract validation (active initiative)

New runs use a bundle containing an immutable `spec.json`, `manifest.json`, content-addressed
rows/artifacts, exact input identities, a stored balanced schedule, and requested/resolved runtime
attestation. The create-only producer helpers are in `backend/tests-benchmarks/benchmark_evidence_bundle.py`; they
refuse existing bundle/artifact paths and validate the finalized bundle. Existing legacy output
must never be relabelled or retrofitted as v1.

Validate a completed bundle before reading timing:

```powershell
env\Scripts\python.exe -u tests-benchmarks\benchmark_evidence.py validate `
  benchmark_results\<experiment-id> `
  --report <new-path-outside-the-bundle-and-all-input-directories>
```

Exit code `0` and verdict `VALID` are both required. `INVALID` timing is not interpreted. The
validator is read-only for the inspected bundle and rechecks every inspected file's byte/hash/mtime
identity at completion. `--report` uses create-only semantics: it refuses an existing file, the
bundle, any declared input directory, or a legacy evidence directory. Omitting `--report` prints
the same machine-readable result to stdout.

The validator enforces fixed minimum schemas for `tooling`, `transcript`, `note`, and `journey`;
the caller cannot weaken them with empty `required_*` lists. Executed rows must match the
preregistered schedule one-for-one, including order and per-row runtime profile. Note/journey
startup logs must retain both the real server banner and exactly one
`PRIVATE_EVIDENCE_RESOLVED_RUNTIME_JSON:` line emitted by the benchmark adapter after parsing the
effective configuration.

Offline tests:

```powershell
env\Scripts\python.exe -u -m unittest `
  tests.test_benchmark_evidence `
  tests.test_benchmark_evidence_bundle `
  tests.test_benchmark_evidence_t0 `
  tests.test_benchmark_common `
  tests.test_beautify_first_run_benchmark `
  tests.test_whisper_batched_benchmark
```

T0 completed on 1 August 2026. Its create-only final bundle is:

```text
backend/benchmark_results/evidence-contract-01082026-jp-start/tooling-v1-final/
```

Independent validation returned `VALID` with no issues; the suite passed 154/154. The four
IT436365 Beautify subjects and five Whisper subjects audited inside it are all
`LEGACY-INCOMPLETE` with zero errors. Preserve the earlier exploratory `legacy-audit.json` and the
final bundle; never overwrite either. Full hashes and ruling:
`bugs-fixed/057-01082026(NewFindings).md`.

### Borrowed weaker-i5 handoff — current gate

The owner’s next priority is a minimum decisive run on the borrowed IT436365-class
i5-1135G7/16 GB laptop. Do **not** rerun the old `056` command block yet: the existing Beautify and
Whisper scripts still emit legacy output unless the active T1 package supplies the v1 adapter.
Running them alone would reproduce the evidence gaps T0 just measured.

The package must be offline-validated on JP-START before transfer. On the borrowed machine it must:

1. remain on `prompt-improve` at the exact package commit;
2. attest machine, power/load, runtime/model/binary and dirty state before the row;
3. create a new local bundle and immutable preregistration before inference;
4. start with one cold production-journey row only;
5. capture stage clocks, transcript/note hashes and quality evidence;
6. postflight-rehash every fixture/input and validate the bundle before timing is interpreted.

The i5 can establish a conservative weak-tier floor. It cannot close the separate 135U hybrid
topology question. `056` supplies parameter inventory only; this plan’s balanced ordering and
evidence contract supersede its forward/reverse ordering.

Legacy evidence can be audited without rewriting it:

```powershell
env\Scripts\python.exe -u tests-benchmarks\benchmark_evidence.py audit-legacy `
  --beautify-dir <legacy-run-directory> `
  --whisper-json <legacy-whisper-result.json> `
  --repo-root .. `
  --report benchmark_results\<audit-id>\legacy-audit.json
```

`LEGACY-INCOMPLETE` means the retained artifact may still be internally consistent historical
evidence but does not meet the stronger contract for a new shipping decision. `INVALID` means an
internal contradiction/hash/configuration failure was found.

---

## After running

Commit into the `private-test-debugs` repo (separate from this one):

```powershell
cd C:\Users\<you>\Documents\private-test-debugs
git add benchmark_results debug
git commit -m "<describe the run>"
git push
```
