# This is one-off plan trying to make while doing the executions from CODEX-SONNET5-CHECKLIST.md

=================================FABLE 5 MAX THOGUTHS BELOW========================================

# Full-Project Speed Review — Fable 5, 2026-07-03

**What this is:** a whole-project, code-verified speed review written after reading the actual engine
code (`whisper_service.py`, `ai.py`, `transcribe.py`, `audio_queue.py`, `sessions.py`, `system.py`,
`config.py`, `electron/main.js`, `api.ts`, the relevant parts of `SessionsPage.tsx` /
`MeetingDashboard.tsx`), the bundled `llama-server.exe --help` output (run for real during this
review), `requirements.txt`, the speed checklist (`CODEX-SONNET5-CHECKLIST.md`), your own measured
baselines from the diagnostic logs, and `bugs-fixed/MyFindings.md`.

Every claim below is labelled: **(VERIFIED)** = I read it in the code or ran it; **(MEASURED)** =
from your own diagnostic-log baselines; **(ESTIMATE)** = a projection that must be tested before
trusting; **(NEEDS TEST)** = a proposed change whose benefit must be benchmarked before adoption.

One thing before the technical content, because it matters for how you read the rest: **you have not
hit a wall — you have hit the end of the obvious levers.** The instrumentation you built is exactly
what a good engineering team would have built first, and it means this review can be grounded in
your real numbers instead of guesses. The remaining levers are less obvious but they are real, and
several are large. This is not a dead project. Read section 10 last, but read it.

---

## 2026-07-30 operational addendum — Flash Attention experiment closed

The authoritative closeout is
[`bugs-fixed/054-30072026(SOL).md`](../../bugs-fixed/054-30072026(SOL).md);
the completed run handover is
[`thoughts/HANDOVER-Flash-Attention-30072026.md`](../../thoughts/HANDOVER-Flash-Attention-30072026.md).
The owner-facing day-by-day Korean record is
[`thoughts/핵심-30072026.md`](../../thoughts/핵심-30072026.md).
[`thoughts/한국.md`](../../thoughts/한국.md) remains the historical
2026-07-29 long-form strategy note and was not rewritten for this closeout.

This exact 24-call result was measured on the user's Dell Latitude 5420:
11th Gen Intel Core `i5-1135G7` (4 cores / 8 logical processors), 16 GB RAM,
Windows 11 Education 24H2, using the bundled CPU llama.cpp backend. Do not
merge it with older Core Ultra or estimated 8 GB weak-tier evidence.

The controlled `-fa auto` versus forced `-fa on` experiment completed all 24
cold/full-prompt calls: four frozen fixtures, two conditions, and three
fresh-server repetitions. The candidate failed the speed gate:

| fixture | `auto` median total | forced `on` median total | candidate delta |
| --- | ---: | ---: | ---: |
| short PRIVATE | 257.359s | 282.406s | +25.047s (+9.73%) |
| long PRIVATE | 436.453s | 456.266s | +19.813s (+4.54%) |
| slow-tail Psychiatric | 495.656s | 518.218s | +22.562s (+4.55%) |
| template-heavy NDIS | 515.641s | 510.797s | -4.844s (-0.94%) |

The paired-repetition aggregate deltas were `+28.845s`, `+39.545s`, and
`-103.516s`; that unstable isolated win does not establish a repeatable
improvement. Realistic long-note medians were slower, and the requested
two-to-three-minute improvement was not approached.

The blind review was saved before the key was opened. Each anonymous pair was
byte-identical across conditions, so forced `on` caused neither a condition-
specific quality regression nor a quality improvement. It did expose serious
shared baseline defects: clinical framing of explicit role-play/interview
material, unsupported encounter details and negative histories, lost
qualifiers/evidence, invented “To be booked” follow-up text, and incomplete
NDIS headings. Those defects make quality/provenance repair—not another
uncontrolled speed change—the next product priority.

**Ruling: reject forced Flash Attention `on`; keep production `-fa auto`,
implicit `-ub 512`, F16 KV, 32k context, current threads, and `auto/3072`.
No production default changed. MTP has not started.** Commit `efce97f` adds an
explicit, default-off, fake/de-identified-only, post-timing run-local reasoning
capture for subsequent bounded tests; the completed 24 calls were not rerun
solely to obtain reasoning text.

---

## 2026-07-29 operational addendum — current Beautify speed evidence

The detailed current execution record is
[`bugs-fixed/053-29072026-3(SOL).md`](../../bugs-fixed/053-29072026-3(SOL).md).
The evidence and work order that preceded it remain in
[`bugs-fixed/052-29072026-2(SOL).md`](../../bugs-fixed/052-29072026-2(SOL).md).
The template-architecture measurement gate that owns the next A/B is
[`BracketsAndHeaders.md` §0.0A and §8.5.1](BracketsAndHeaders.md).
The owner-facing Korean explanation, low-RAM strategy, and ranked later
model/runtime research candidates are in
[`thoughts/한국.md`](../../thoughts/한국.md). It is a companion only:
`bugs-fixed/053` and this plan's Current Status still own execution order.

New evidence from all 48 retained Beautify debug artifacts changes the framing,
but not this plan's benchmark discipline:

- Beautify makes **one combined model request**, not four sequential heavy model
  calls. Inside it the model reads the Source, reconciles evidence/guardrails,
  maps template fields, and drafts/self-reviews. Final optional checks are local
  Python work after the stream.
- The same distinctive 25,894-character Chris Park Korean political source
  fixture already took 336.3s, 300.7s, and 313.2s under
  `live-2026-07-25.1`. Its current TEPOU model phase took 290.6s under
  `live-2026-07-28.3`. The July 29 report is not evidence that the new template
  guardrails created a five-minute workload.
- Prompt-cache reuse is working: the supplied current sequence reduced newly
  evaluated prompt tokens `9,665 -> 1,124 -> 517` and prompt evaluation
  `130.5s -> 15.4s -> 7.9s`. Hidden reasoning and completion length then
  dominated.
- The first-text UI's old `1–3 min` range discarded the observed 254.8s slow
  tail and compared runs by source characters, which is especially weak for a
  token-dense Korean source. That estimate is now widened; a future estimator
  should be prompt-token/template/cache aware.

#### Four-item bulk evidence added 2026-07-29

The later Chris/Tash/Jane/Rogene test was a four-note Bulk Beautify. It is the
important complement to the earlier single-note evidence:

| note / template | prompt evaluated / total | prefill | generation | model total |
| --- | ---: | ---: | ---: | ---: |
| Chris / PRIVATE | 2,456 / 10,127 | 26.9s | 199.8s | 3m46.8s |
| Tash / Psychiatric | 10,964 / 10,964 | 126.2s | 165.0s | 4m51.3s |
| Jane / TE POU | 7,765 / 9,202 | 89.7s | 192.2s | 4m42.0s |
| Rogene / Supervision | 9,196 / 10,633 | 109.0s | 115.7s | 3m44.7s |

The queue took approximately `17m06.4s` wall time; model time summed to
`17m04.9s`. Bulk orchestration added only about `1.5s`. This does **not**
contradict "one request per Beautify": each note is one request, while four
selected notes are four full requests run sequentially.

The run reveals two performance classes:

- with a warm prefix, Chris spent 88.1% of total time in hidden
  reasoning/visible generation, so reasoning control is the likely raw-speed
  lever;
- with a cold or mostly cold prefix, the other notes spent 89.7-126.2s on
  prefill alone, so reasoning changes cannot solve the whole first-text wait.

The exact same `31,820`-character Rogene source was also run on 2026-07-26. The
new prompt used 10.2% more prompt tokens and eight headings instead of four,
yet total model time fell from `242.6s` to `224.7s` (-7.4%) because completion
was shorter. This pair is not controlled for cache, but it is further evidence
that the July 28 guardrails did not automatically make the note slower.

#### Execution result added later 2026-07-29

The observability blocker is closed. Commit `768c944` adds one privacy-safe
`beautify-batch-item` measurement per actual model request while retaining the
aggregate `beautify-bulk` row. It captures prompt/cache/timing, hidden-reasoning
onset, exact visible TTFT, reasoning/completion/decode work, finish/truncation,
review slugs, and cancellation/failure state without Source, names, output, or
reasoning text.

Bundled b9585 does **not** honour the top-level request
`reasoning_budget`. Identical request fields `0 -> 256 -> 0` produced identical
reasoning and output. It does honour `--reasoning-budget` at server start:
fresh processes produced reasoning amounts `0 -> 910 -> 0`. Commit `a326582`
adds the local controlled harness and prevents the ignored field from being
offered through the Beautify service/router.

The staged `auto/3072` versus `1024` A/B is complete:

| fixture/state | 3072 visible / total | 1024 visible / total | 1024 total delta |
| --- | ---: | ---: | ---: |
| Short PRIVATE, cold | 92.656s / 125.625s | 91.344s / 124.063s | -1.24% |
| Short PRIVATE, warm | 67.063s / 105.110s | 56.407s / 87.047s | -17.18% |
| Long TE POU, cold | 146.421s / 179.281s | 138.547s / 186.187s | +3.85% |
| Long TE POU, warm | 43.797s / 88.875s | 63.687s / 127.141s | +43.06% |
| **aggregate** | **349.937s / 498.891s** | **349.985s / 524.438s** | **+5.121%** |

Blind review found no 1024-specific quality regression, but speed was neither
materially better nor stable. **Reject 1024; keep production at
`auto/3072`.** Per the staged gate, do not test `512`/`off` after this failure.

Exact prompt-cache reuse was independently proven: immediate identical warm
requests evaluated five of 4,334/8,387 tokens (`99.88–99.94%` reuse), reducing
prompt evaluation from `29.5–76.4s` to `0.11–0.166s`.

**Product-workflow ruling:** counsellors normally transcribe once, Beautify
once, edit small details, and move to the next session. Repeat-cache speed is
therefore a diagnostic, not the primary intervention. The success target is a
routine **2–3-minute first Beautify**, including the current four-to-five-
minute tail; saving a few seconds is not material. Keep reasoning at
`auto/3072`.

**First-run continuation result:** the requested production baseline and
prompt-contribution audit are complete. Four representative roles each
received three fresh-server/full-prompt runs at `auto/3072`. Median totals were
`129.453s` short PRIVATE, `218.297s` long PRIVATE, `174.968s` template-heavy
TE POU, and `227.375s` slow-tail Psychiatric. Source was `79.5–84.2%` of the
three long/template-heavy prompts; fixed evidence/safety rules were
`12.9–17.1%`; labels and all template guidance were too small to be a credible
one-to-two-minute lever.

The first engine-only A/B changed physical prompt microbatch alone:
`-ub 512` versus `2048`, four fixtures × two conditions × three cold
repetitions. Candidate median aggregate prefill improved only `4.309s`
(`1.442%`), while first-visible time worsened `25.062s` and total time
worsened `6.251s`. Its only tail win was `7.938s`, leaving that run at
`3m41.109s`. Blind review also found an unsupported TE POU field placement and
a critical Psychiatric loss of role-play attribution plus risk evidence.
**Reject `-ub 2048`; production remains implicit `512` and `auto/3072`.**

That exact next experiment—current `-fa auto` versus forced `-fa on`, one
variable only, in the same 24-call cold matrix—was executed on 2026-07-30 and
forced `on` was rejected. See the addendum above and
`bugs-fixed/054-30072026(SOL).md`. Source-prefix pre-warm remains secondary
research only if real use shows meaningful idle time before the first
Beautify click.

The four logical Beautify duties remain inside one combined request: read
Source/metadata; reconcile evidence/attribution/risk/template rules; map
supported evidence to fields; draft exact headings/content and self-check.
Audio is not one of them. Whisper transcription is upstream; workflow-level
`Transcribe & Beautify` may chain Whisper and Gemma, but merging speech
recognition and note generation would remove the inspectable Source boundary.

Do not combine reasoning, prompt architecture, cache pre-warm, guidance
compaction, or engine flags in one benchmark. The one-lever/quality-gate rules
below remain controlling.

Do not combine different clients into one prompt as a bulk shortcut. The
per-note input is already combined and Source-first; cross-note batching would
introduce clinical data separation, attribution, context-window, cancellation,
and partial-failure risks without evidence of a net speed win.

---

## 1. The honest picture first

### 1.1 Where the time actually goes today (MEASURED — your own logs, Vivobook / Core Ultra 7 / 32GB)

| Operation | Total | Breakdown |
|---|---|---|
| Transcribe 42-min audio (base, beam 2, 4 threads) | ~4:35 warm / ~4:42 cold | RTF 0.073–0.108 |
| Transcribe 13-min audio | 86.6s | RTF 0.099, model load 6.2s |
| Beautify 47-min session (14,062-token prompt) | 6:04 | **62% prefill** (~62 tok/s) · 20% invisible reasoning · 18% visible writing (12.5 tok/s) |
| Beautify 13-min session (3,720-token prompt) | 2:13 | **44% prefill** (~64 tok/s) · 26% reasoning · 31% visible (18.9 tok/s) |
| llama-server cold start | ~4.4s | trivial |
| 8 whisper threads vs 6 | ~27% faster decode | n=1, promising, not decision-grade yet |

The two headline facts:

1. **Prefill (the model *reading* the transcript) is the single biggest cost of Beautify at every
   session length** — not the reasoning phase, not the writing phase. And prefill speed is exactly
   the surface that has had zero tuning: the server is spawned with no thread, batch, or
   flash-attention flags at all (VERIFIED, `backend/services/ai.py:174-181`).
2. **During the entire wait, the user sees nothing.** Transcription returns one blob at the end
   (VERIFIED — `api.transcribe()` is a single fetch, no streaming). Beautify streams, but its
   time-to-first-visible-token was 92s on a short session and 298s on a long one (MEASURED) — the
   user stares at a static state for 1.5–5 minutes before the first word appears. Your own finding
   ("nothing shows and everything just dumps once finished") is the correct diagnosis of the biggest
   *product* problem, independent of raw speed.

### 1.2 What an i5 / 8GB office laptop will do (ESTIMATE — no such machine has been tested yet)

A 4-core/8-thread i5 with dual-channel (often single-channel!) DDR4 has roughly 2.5–3.5× less CPU
throughput and half-to-a-third the memory bandwidth of your Vivobook. Straight-line projection for
one 45-minute session, **today's build**:

- Transcribe: RTF ~0.25–0.35 → **11–16 minutes**
- Beautify: prefill ~20–30 tok/s on ~13k tokens ≈ 8–11 min, + reasoning/writing at ~4–7 tok/s ≈
  4–7 min → **12–18 minutes**
- **Total ≈ 25–34 minutes per session — with zero feedback on screen.** That is the "genuinely
  fails" scenario, and your instinct about it is right.
- **And it can be much worse than that**, because of the RAM problem in §4.2: the server reserves a
  32k-token KV cache up front. On an 8GB machine running Windows + Electron + Chrome renderer +
  Python + Whisper, that can push the working set into the pagefile, and paging doesn't slow LLM
  inference by 20% — it slows it by 3–10×. This is the silent killer for exactly the tier you're
  worried about, and it's fixable (§4.2).

### 1.3 The conclusion in one paragraph

The good news: the levers to fix this exist, most are already on your checklist, and this review
adds several new ones. Realistic end-state after the work below (ESTIMATE, to be verified phase by
phase): mid-tier laptop ≈ **5–7 min total** per 45-min session (your stretch target); weak tier ≈
**10–16 min** (your honest "roughly halve" commitment) — and, with the live-transcription idea in
§5.1, the *visible* wait on any tier collapses to roughly the Beautify time alone. Combined with a
real progress system (§3), that is a sellable product. Not "as fast as a cloud service" — that was
never the bar for a 100%-offline privacy product — but "reliably done inside the between-sessions
gap, and you can watch it working."

---

## 2. Two findings that are not tuning at all — fix these regardless of everything else

### 2.1 The app lets Windows go to sleep in the middle of long jobs (VERIFIED — high impact)

There is **no `powerSaveBlocker` anywhere in `electron/`** (grep-verified) and nothing in the Python
backend calls `SetThreadExecutionState`. Windows laptops default to sleeping after 15–30 minutes of
no input. Your own "walk away" scenario — a 4-session backlog taking 75–95 minutes unattended — will
be interrupted by system sleep on most customer machines unless the user happens to touch the mouse.
When the machine sleeps, Whisper/llama threads are suspended mid-decode; the user comes back to a
stalled queue and concludes the app is broken or impossibly slow. **Some fraction of "it's too slow"
on real customer machines will actually be "it went to sleep."**

**Fix (small, ~30 lines, no Electron changes needed):** pulse the Windows idle timer from the
backend while any long job runs. `SetThreadExecutionState(ES_SYSTEM_REQUIRED)` *without*
`ES_CONTINUOUS` resets the system idle timer once per call — no persistent state, nothing to clean
up, safe from any thread. This matches the `ctypes.windll` pattern you already use for
`on_ac_power()` and DPAPI.

New file `backend/services/power.py`:

```python
"""Keeps Windows awake while a long local AI job is running.

SetThreadExecutionState(ES_SYSTEM_REQUIRED) without ES_CONTINUOUS just resets
the system idle timer — like a mouse wiggle. Called (throttled) from inside the
transcribe/beautify work loops, so the machine can never sleep mid-job, but
normal sleep behaviour returns automatically the moment the loops stop calling.
The DISPLAY is deliberately allowed to sleep — only the system must stay up.
"""
import ctypes
import threading
import time

ES_SYSTEM_REQUIRED = 0x00000001

_last_pulse = 0.0
_pulse_lock = threading.Lock()

def pulse_keep_awake(min_interval_s: float = 30.0) -> None:
    """Best-effort, throttled. Never raises — must never break a clinical job."""
    global _last_pulse
    try:
        now = time.monotonic()
        with _pulse_lock:
            if now - _last_pulse < min_interval_s:
                return
            _last_pulse = now
        ctypes.windll.kernel32.SetThreadExecutionState(ES_SYSTEM_REQUIRED)
    except Exception:
        pass
```

Call sites (one line each, inside loops that already exist):

- `backend/routers/transcribe.py` — inside the `for seg in segments:` loop (~line 108)
- `backend/routers/audio_queue.py` — inside both bulk workers' `for seg in segments:` loops and the
  per-item endpoint's loop
- `backend/routers/sessions.py` — inside the beautify `gen()` token loop (~line 403)
- `backend/services/ai.py` — inside `_chat_stream`'s line loop (covers digest/take-away/template
  calls too, since they go through `_chat`; add one pulse at the top of `_chat` as well — a single
  pulse before a ≤2-min non-streamed call is enough)

This is a day of work including testing, it has zero performance risk, and it removes a whole class
of "mysteriously unfinished batch" support cases before you ever get one.

### 2.2 llama-server's output pipes are never drained → possible "random hang after heavy use" (VERIFIED structure, severity NEEDS TEST)

`_ensure_server` spawns llama-server with `stdout=subprocess.PIPE, stderr=subprocess.PIPE`
(`backend/services/ai.py:187-192`), and after startup **nothing ever reads those pipes** (stderr is
only read in the early-death path of `_wait_for_server`). llama-server logs several lines per
request to stderr. A Windows anonymous pipe has a small fixed buffer; once it fills, the child's
next write **blocks forever** — the server would freeze mid-request and every later AI call would
hang until timeout. Whether the b9585 build's default log volume fills the buffer in a realistic
day is unverified — but the failure mode is structurally present, it gets more likely the longer the
app runs, and it is consistent with the one unexplained event in your logs (row 233: a
`beautify-single` that started and never completed). Electron, by contrast, drains Python's pipes
correctly (`electron/main.js:345-349`) — so Python itself is safe; only the grandchild is at risk.

**Fix (small):** drain both pipes with daemon threads into a ring buffer. This also *upgrades* your
diagnostics — any future llama-server failure can log its last output lines.

In `backend/services/ai.py`, next to the process globals:

```python
from collections import deque

_server_log_tail: deque = deque(maxlen=200)  # last N lines, for diagnostics only

def _drain_pipe(pipe) -> None:
    """Daemon thread: keeps the child's pipe empty so it can never block on a
    full buffer, keeping only a short tail for failure diagnostics."""
    try:
        for raw in iter(pipe.readline, b""):
            _server_log_tail.append(raw[-300:])
    except Exception:
        pass
```

Right after the `subprocess.Popen(...)` call in `_ensure_server`:

```python
threading.Thread(target=_drain_pipe, args=(_server_process.stderr,), daemon=True).start()
threading.Thread(target=_drain_pipe, args=(_server_process.stdout,), daemon=True).start()
```

And change `_wait_for_server`'s early-death branch to read from `_server_log_tail` instead of
`_server_process.stderr.read()` (which would now race the drain thread). Bonus: after the server
reports healthy, the drained stderr contains llama.cpp's own printed line stating the **exact KV
cache size in MiB** — log it once to the activity log and you get ground truth for §4.2 on every
machine, free.

---

## 3. Perceived speed: the progress system (your #1 ask, designed end-to-end)

Users don't abandon software because a job takes four minutes. They abandon it because a job takes
four minutes **while looking frozen**. Everything in this section is quality-neutral (touches no
model settings), so it can ship independently of all benchmarking, and it changes the product feel
more than any single engine flag will.

### 3.1 Transcription progress — the real numbers already exist, they're just thrown away

faster-whisper yields segments incrementally, and every segment carries `seg.end` — the number of
audio-seconds completed. `info.duration` (total audio length) is available *before* the loop starts.
Your cancel fix (2a) already converted every decode into an explicit per-segment loop — which means
**the progress hook point already exists in all four transcription paths.** This is the cheapest
high-impact change in this whole document.

**Backend — extend the existing job registry** (`backend/services/whisper_service.py`, right beside
the `_cancel_events` block, same style):

```python
# Live progress for single-item transcribe jobs — shares job ids with the
# cancel registry above. Values are non-PHI (seconds only).
_progress: dict[str, dict] = {}
_progress_lock = threading.Lock()

def report_progress(job_id: Optional[str], processed_s: float, total_s: float) -> None:
    if not job_id:
        return
    with _progress_lock:
        _progress[job_id] = {"processed_s": round(processed_s, 1),
                             "total_s": round(total_s, 1)}

def get_progress(job_id: Optional[str]) -> Optional[dict]:
    if not job_id:
        return None
    with _progress_lock:
        return dict(_progress[job_id]) if job_id in _progress else None
```

Clear the entry inside `end_cancellable_job` (same finally-block lifecycle as the cancel token).

**Hook it into the loops** — `backend/routers/transcribe.py` (~line 108), and the same three lines
in `audio_queue.py`'s per-item endpoint and both bulk workers:

```python
total_s = getattr(info, "duration", 0.0) or 0.0
for seg in segments:
    texts.append(seg.text)
    report_progress(job_id, seg.end, total_s)
    pulse_keep_awake()                      # §2.1
    if is_cancelled(job_id):
        ...
```

**New endpoint** (in `transcribe.py`, next to `/transcribe/cancel`, same licence gate):

```python
@router.get("/transcribe/progress")
async def transcribe_progress(job_id: str, category: str = "meetings"):
    ws = 'meetings' if category == 'meetings' else 'counselor'
    require_active_license(ws)
    p = get_progress(job_id)
    # No entry yet = model still loading (the 6-8s cold-load window) — the
    # frontend renders that as its own "Preparing the transcription engine…" stage.
    return p or {"processed_s": 0.0, "total_s": None}
```

**Frontend** (`SessionsPage.tsx`): in `transcribeBlob()` / `handleTranscribeQueueItem()`, after the
fetch starts, poll `api.getTranscribeProgress(jobId)` on a 1s interval into new state
`transcribeProgress: {processed: number; total: number | null} | null`; clear the interval in the
same `finally` that clears the job-id ref. Replace the two static "Transcribing in progress…" blocks
(the sidebar one at ~line 5158 and the editor blur overlay at ~line 5249) with:

- a real bar: `width = processed / total`
- the text you asked for: **`12:30 / 47:00 transcribed`**
- an ETA computed from the *live observed rate*, which self-corrects mid-run:
  `remaining = (total − processed) / rate`, where `rate` = exponentially-smoothed
  `Δprocessed / Δwall-clock` over the last few polls. Label it "~" because VAD makes progress jump
  over silences (that's fine — the bar only ever moves forward; clamp at 100%).
- while `total === null`: "Preparing the transcription engine…" (this makes the cold-load window
  honest instead of dead).

**Bulk queue:** `_queue_state` in `audio_queue.py:44` already carries `done/total` and is already
polled by the frontend via `/audio-queue/process-status`. Add two fields updated from the worker's
segment loop — `"item_processed_s"` and `"item_total_s"` — and the background banner can show
"Item 2 of 4 — 61% (~3 min left)" instead of only item counts. The overall-batch ETA falls out of
the same numbers plus each remaining item's known duration (`audio_queue` rows store the files; if
duration isn't stored per row yet, show per-item progress only — still a huge upgrade).

Total effort: ~2–3 focused days across backend + frontend, no risk to output quality, and it
directly implements every bullet in `MyFindings.md`'s recommendation list.

### 3.2 Beautify progress — three honest stages instead of one silent wait

Beautify's wait has three phases with completely different characters, and the UI should say which
one it's in:

**Stage A — "Reading your notes" (prefill; 44–62% of the wait).**
This bundled llama-server exposes a `/slots` monitoring endpoint and it is **enabled by default**
(VERIFIED via `--help`: `--slots, --no-slots ... (default: enabled)`). During prompt processing the
slot object reports how many prompt tokens have been consumed. Add a tiny read-only proxy in the
backend (llama-server requires the API key, which only the backend holds):

```python
# backend/services/ai.py
def get_prefill_progress() -> Optional[dict]:
    """Non-PHI: token counts only. Returns None when idle/unavailable."""
    try:
        r = httpx.get(f"http://127.0.0.1:{LLAMA_SERVER_PORT}/slots",
                      headers=_AUTH_HEADERS, timeout=1.0)
        r.raise_for_status()
        for slot in r.json():
            # Field names to confirm once against this build with a real request
            # in flight (curl /slots mid-Beautify): recent builds expose the
            # prompt-processing position as e.g. n_past vs n_prompt_tokens.
            if slot.get("is_processing"):
                done  = slot.get("n_past") or 0
                total = slot.get("n_prompt_tokens") or 0
                if total:
                    return {"prompt_done": done, "prompt_total": total}
    except Exception:
        pass
    return None
```

…exposed as `GET /api/ai/progress` (licence-gated, in `sessions.py`), polled by the frontend once
per second while a Beautify is awaiting its first token. **One caveat, flagged honestly:** I
verified the endpoint exists and is on by default; I could not verify the exact field names without
a model loaded — confirm them with one curl during dev. If this build's `/slots` turns out not to
expose the position, fall back to the estimate approach: `prompt_total ≈ len(notes)/4 + ~800` and
the device's own measured prefill rate from §3.4 — an *estimated* bar labelled as such still beats
silence.

**Stage B — "Organising the note" (the invisible reasoning phase; 20–26%).**
The reasoning tokens are *already streaming into the backend* — `_chat_stream` receives every
`reasoning_content` delta and counts the characters for diagnostics
(`backend/services/ai.py:304`) — then throws the event away. Forward a heartbeat instead. Change
`_chat_stream` to yield structured events rather than bare strings:

```python
delta = choices[0].get("delta", {})
r = delta.get("reasoning_content")
if r:
    _capture_reasoning_chars(capture_stats, r)
    yield {"kind": "thinking", "chars": len(r)}      # count only — never the text
token = delta.get("content", "")
if token:
    yield {"kind": "token", "text": token}
```

Then in `beautify_notes_stream` pass events through unchanged; update the *two* consumers
(VERIFIED, only two exist): `sessions.py`'s `gen()` and the `beautify_notes_service` join —

```python
# sessions.py gen(): throttle thinking events to ~2/s so SSE stays light
for ev in beautify_notes_stream(..., capture_stats=capture_stats):
    if ev["kind"] == "token":
        ...existing ttft/produced bookkeeping...
        yield f"data: {json.dumps({'token': ev['text']})}\n\n"
    else:
        thinking_chars += ev["chars"]
        if _t.monotonic() - last_emit > 0.5:
            last_emit = _t.monotonic()
            yield f"data: {json.dumps({'thinking': thinking_chars})}\n\n"

# ai.py beautify_notes_service (non-stream fallback):
return "".join(ev["text"] for ev in beautify_notes_stream(...) if ev["kind"] == "token")
```

Frontend: `api.beautifyNotes`'s SSE parser gains an optional `onThinking?: (chars: number) => void`
beside `onToken`; SessionsPage shows a pulsing "Organising the note structure…" state the moment the
first thinking event arrives. This is a **real liveness signal** — the counsellor sees the machine
working within a second of prefill finishing, instead of at ttft.

**Stage C — "Writing" (already streams).** No change; the existing token append
(`SessionsPage.tsx:2553-2561`) is fine.

The state machine in the UI: *Preparing* (server cold start, if any) → *Reading your notes — 43%* →
*Organising the note…* → tokens streaming. Every stage is real, none of it lies, and the 92–298s
dead window disappears as a perceived phenomenon.

### 3.3 The other silent spinners

- **Meetings "Generate Summary"** — `POST /api/summarize` is fully non-streaming (VERIFIED:
  `summarize_transcript_service` → `_chat`; the UI shows only "Generating locally…",
  `MeetingDashboard.tsx:1009`). For a 60-minute meeting transcript on weak hardware this is a
  many-minute blind wait — the worst remaining one in the app once Beautify gets §3.2. Port it to
  the exact same SSE pattern as Beautify (the meeting-mode sanitizer runs on the input before
  prompting and on the final text after; with streaming, sanitize the input as today, stream tokens
  to the UI as "draft forming", then apply the output sanitizer to the final text on completion —
  the streamed preview is local-only display, the *stored* summary stays sanitizer-final).
- **Reporting summary ("Generate summary") and Take-away** — non-streamed `_chat` calls. Lower
  priority (shorter prompts), but at minimum give them the Stage A/B staged label treatment via
  `/api/ai/progress`, since it's the same server doing the same phases.

### 3.4 Replace the hand-written time estimates with the device's own measured speed

The Beautify-All modal currently hard-codes *"A note from a ~45-minute session takes about 10–15
minutes"* (`SessionsPage.tsx:3411-3422`). That number is wrong in both directions depending on the
machine — and you already log everything needed to compute the right one.

- Backend: at the end of each completed op, you already have `decode_ms`/`audio_duration_s`
  (transcribe) and `prompt_tokens`/`ttft_ms`/`duration_ms` (beautify). Return them in the response
  (transcribe already builds the `detail` dict — add the same numbers to the JSON response; for
  Beautify append one final SSE event `data: {"stats": {...}}` before `[DONE]`).
- Frontend: keep a tiny rolling profile in localStorage, e.g. `private_perf_profile =
  {rtf: EMA, prefill_tps: EMA, decode_tps: EMA}` updated after each success.
- Estimates everywhere become computed: batch modal per-note estimate =
  `words*1.33/prefill_tps + expected_output/decode_tps` (+ measured reasoning share); transcribe
  estimate = `audio_duration * rtf`. Show "~" and a range. First-ever run (no profile yet): fall
  back to a conservative canned range — but label it "first run on this computer — this estimate
  will get smarter."

This also fixes the checklist's Phase 10 bullet ("replace the hand-written estimate copy") with a
mechanism instead of another hand-written number.

### 3.5 Small honesty chips (cheap, disproportionate trust value)

- **Battery chip:** backend already knows `on_ac_power()` — expose it (e.g. on the health or a tiny
  status endpoint) and show a small amber chip when starting a long job on battery: *"Running on
  battery — plugged in is usually much faster."* Windows aggressively throttles unplugged; this is
  free real-world speed users can action themselves.
- **Cold-start honesty:** the first transcription after launch pays a 6–8s model load
  (MEASURED) — §3.1's "Preparing the transcription engine…" stage covers it.
- **Settings copy for "Higher Accuracy":** once §7's numbers exist, state the real multiplier
  ("takes ~4× longer than Standard on this computer") next to the toggle, so nobody discovers it
  mid-crisis.

---

## 4. Raw engine speed — ordered by what it buys the weak machine

Your checklist's Phases 4–7 are the right levers in nearly the right order. This section endorses
them with expected magnitudes, and adds what's missing. Rule you already wrote, worth repeating
because everything below obeys it: **one lever per change, measure before/after, never silently
lower quality.**

### 4.1 Whisper threads (checklist Phase 5 — in flight, finish it)

`CPU_THREADS = 0` → library default 4 (VERIFIED, `whisper_service.py:36`). Your informal 6→8 result
(+27%) says the ceiling is real. Guidance to add to the harness run: the best default is almost
certainly **physical core count, not logical** (hyperthreads share the FPU/memory ports that int8
GEMM saturates; oversubscription usually loses). Ship it adaptively, not as a constant:

```python
# whisper_service.py — replace the constant with a resolved-at-import default
def _default_cpu_threads() -> int:
    try:
        import os
        logical = os.cpu_count() or 4
        # Physical-core detection without psutil: logical/2 is right for almost
        # every Intel/AMD laptop CPU with SMT; hybrid chips get benchmarked in
        # Phase 5 and can override. Clamp so a 4-core i5 isn't over-threaded
        # and a 16-thread machine isn't under-used.
        return max(4, min(8, logical // 2))
    except Exception:
        return 4
CPU_THREADS = _default_cpu_threads()
```

(NEEDS TEST — exactly what your harness exists for; the snippet is the *shape* of the ship, the
clamp values come from the benchmark, including the i5-class run.) Expected: **~20–30% off decode
time on most machines** for free, more on high-core machines.

### 4.2 Right-size the 32k context — the silent 8GB killer (my strongest new engine finding)

`_ensure_server` passes `-c 32768` unconditionally (VERIFIED, `ai.py:180`). llama.cpp reserves the
KV cache for the *full* context at startup, whether or not a request ever uses it. For models this
size at 32k fp16 that reservation is on the order of **1.5–3 GB of RAM before the first token**
(ESTIMATE — get ground truth from the "KV self size" line in the drained server log, §2.2, or Task
Manager's llama-server.exe working set right after spawn). On your 32GB machine it's invisible. On
an 8GB machine it is very plausibly the difference between "slow" and "paging to disk" — and paging
is the 3–10× catastrophe, not a percentage.

Meanwhile the *actual* need: your longest measured prompt is 14,062 tokens, completions ≤ ~1,800
tokens. Even the 47-minute session fits comfortably in 16k with the current `max_tokens` formula's
real-world outputs.

Two-step fix, cheapest first (both NEEDS TEST for speed-neutrality, both quality-safe):

1. **Quantize the KV cache and pin flash attention on** — halves KV RAM at negligible quality cost
   for q8 (this is cache precision, not weights):
   ```python
   args = [
       LLAMA_SERVER_EXE, "-m", target_path,
       "--host", "127.0.0.1", "--port", str(LLAMA_SERVER_PORT),
       "--api-key", _LLAMA_API_KEY,
       "-c", "32768",
       "-fa", "on",                # required for quantized V cache; benchmark vs 'auto' anyway (Phase 5)
       "-ctk", "q8_0", "-ctv", "q8_0",
   ]
   ```
2. **Make the context RAM-aware** rather than one-size:
   ```python
   def _pick_ctx_size() -> str:
       """32k only where RAM is plentiful; 16k covers every measured real
       session (max observed prompt 14k) and halves the KV reservation."""
       try:
           import ctypes
           class MEMORYSTATUSEX(ctypes.Structure):
               _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                           ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                           ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                           ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                           ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
           st = MEMORYSTATUSEX(); st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
           ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
           total_gb = st.ullTotalPhys / (1024 ** 3)
           return "32768" if total_gb >= 15 else "16384"
       except Exception:
           return "16384"
   ```
   Plus a guard in the beautify router: if `len(notes)//4 + 2000` exceeds the loaded context, return
   the existing "notes too long" 400 with the existing friendly message (the 400 branch in
   `_chat_stream` already handles server-side overflow — this just fails it earlier and clearer).

Also reuse `GlobalMemoryStatusEx` in Settings to warn before selecting **Better Quality (E4B)** on a
<10GB machine — the description already says "10 GB+ RAM" but nothing enforces or explains it at
selection time.

### 4.3 The reasoning phase (checklist Phase 4) — where to cut first

VERIFIED: the bundled b9585 supports `--reasoning on|off|auto` and `--reasoning-budget N`. MEASURED
cost of reasoning: ~20% of a long Beautify, ~26% of a short one — but proportionally **much** larger
for the small utility ops (digest, take-away, template mapping), whose visible outputs are tiny
(2–4 sentences) while the QAT model reasons at length first. Your own bug history proves it: the
digest once burned its whole 320-token budget on reasoning and returned empty.

Strategy:

- **A/B the global `--reasoning off` first on the *small* ops** (digest, take-away, template
  mapping): highest relative win, lowest quality risk — these are extraction/condensation tasks, not
  clinical composition. If quality holds there but Beautify suffers, test the middle ground
  `--reasoning-budget 512`.
- **Caveat you already know:** it's a server-spawn flag, so it applies to every op at once. Two
  extra options worth one curl each before accepting that constraint: (a) test whether this build
  honours a per-request `"reasoning_budget"` field in the request JSON (some builds do; if yes, you
  can turn reasoning off per-op with zero restarts — the ideal outcome); (b) if not, and the A/B
  says "off for small ops, on for Beautify", note that `_ensure_server` already restarts on
  model/mmproj change — adding reasoning-mode to its identity key is possible but adds a ~5s restart
  when alternating op types; probably not worth it vs. one global setting.
- If the decision is "off everywhere": also shrink `reasoning_est` in the Beautify token-budget
  formula (`ai.py:663-666`) and the "generous budget because reasoning" comments — your checklist
  already has this bullet.

Expected: **−20–26% Beautify time; −40–70% digest/take-away time** (the latter transforms the
Reports-page bulk generation and the pending-summaries backlog). (NEEDS TEST — quality gate.)

### 4.4 llama-server prefill/thread flags (checklist Phase 5, llama half) — the biggest Beautify lever

62–64 tok/s prefill on a Core Ultra 7 is far below what a ~2B-effective Q4 model should do on that
silicon; multiple hundreds of tok/s is the plausible range once `-t`/`-tb`/`-ub`/`-fa` are tuned
(ESTIMATE — your checklist's own audit note agrees: "genuine headroom, not a hardware ceiling").
Concrete benchmark matrix for the harness-equivalent on the llama side, one variable at a time:

- `-t` (decode threads): physical cores; try physical−1 (leaves a core for the UI/whisper).
- `-tb` (prefill threads): try logical count — prefill is compute-bound and often *does* scale past
  physical cores, which is exactly why the flag exists separately.
- `-ub` 512 (default) vs 1024 vs 2048 — larger microbatches usually help CPU prefill on long
  prompts; watch RAM.
- `-fa on` vs `auto`, with F16 KV fixed. Test Q8 KV separately; combining
  flash and cache precision would make the result uninterpretable.
- Measure with the `timings` field (§6.1) rather than stopwatch.

Even **prefill ×2** cuts the 47-min-session Beautify by ~1.9 min (−31%); prefill ×3 ≈ −41%. On the
weak tier the same multiplier applies to a much bigger number. This is the single largest pure-speed
lever in the whole document. (NEEDS TEST.)

### 4.5 `--cache-reuse` + prompt caching (checklist Phase 7) — keep expectations modest

VERIFIED available. Your checklist's expectation note is correct: across *different* sessions only
the shared system prompt (~600–900 tokens) is reusable ≈ 10–15s off a long Beautify; the big wins
are re-Beautify of the same note and template-mapping right after a Beautify of the same session
(near-full prefix reuse). Cheap to add (`--cache-reuse 256` + confirm request-level `cache_prompt`
default on this build + confirm `-np` resolves to 1 slot so the KV budget isn't split). Do it after
4.4 so the benchmark deltas stay attributable.

### 4.6 Whisper micro-levers (bundle into the Phase 5 harness runs)

- **Language lock:** language is auto-detected per file today (VERIFIED — no `language=` arg,
  `transcribe.py:96-101`). Add a Settings option "Spoken language: English (NZ) / Auto-detect",
  passing `language="en"` when set. Small speed win (skips detection) but the *real* value is
  robustness: one misdetected file (soft-spoken opening, music, te reo greeting) transcribes into
  the wrong language and wastes an entire multi-minute run. Default: keep Auto for safety, let
  pilots flip it.
- **`condition_on_previous_text=False`:** currently library-default True. On long,
  silence-heavy counselling audio, conditioning is the classic cause of repetition-loop hallucination
  — which *also* wastes decode time. Test in the harness; whisper folk wisdom says quality holds or
  improves for this content type with VAD on. (NEEDS TEST.)
- **`beam_size=1` "Fast draft" profile** (checklist Phase 9): ~25–40% off decode vs beam 2
  (ESTIMATE), never a silent default — exactly as you designed it.
- **Batched inference** (checklist Phase 6, after the 1.2.1 upgrade): this is the transcribe
  multiplier — upstream reports 2–4× on multi-core CPUs for long files; on a 4-core i5 expect the
  low end (ESTIMATE). Combined with threads, a 45-min file on the weak tier plausibly drops from
  11–16 min to **4–7 min**.

### 4.7 Model lineup for the weak tier (additive only — never rename, per your own hard rule)

- The gap between base (fast, okay) and medium (accurate, brutal on i5) is wide. Two candidates to
  evaluate as a **new middle "Higher Accuracy (Fast)" option**, both supported by faster-whisper as
  plain model names, both additive (base and medium keep shipping untouched): `small` (~2.5× base
  cost, meaningfully better accuracy) and the **distilled English models** (`distil-medium.en`
  class): near-medium accuracy at a fraction of medium's decode cost, English-only. Caution for NZ
  use: test on your own NZ-accented recordings including te reo Māori words before offering —
  English-only distil models will mangle te reo more than multilingual models do. (NEEDS TEST.)
- Beautify side: E2B stays the right default. Don't chase a sub-2B model for speed — clinical prose
  quality is the product; §4.3/§4.4 get the time down without touching quality.

### 4.8 Warm-ups that hide seconds (cheap, do late — your Phase 2, correctly demoted)

Two targeted warm-ups beat the general "keep everything hot all day" design:

- **Whisper warm on record-start:** the moment recording begins, fire a background
  `get_whisper_model(selected_size)` (guarded by `TRANSCRIBE_LOCK` etiquette — skip if busy). The
  6–8s load happens invisibly during the session; stop-click transcription starts instantly.
- **llama warm on transcribe-completion:** when a transcription finishes in the counsellor
  workspace, Beautify is the likely next click — fire `_ensure_server()` in the background
  (RAM-aware via §4.2's helper: skip below ~10GB free-total heuristics on 8GB machines). Cold start
  is only ~4.4s on your machine but will be 15–30s on slow SSDs with AV scanning (ESTIMATE) — this
  hides it.

### 4.9 GPU (Vulkan) — the one architecture experiment worth a later spike

The shipped llama-server is deliberately CPU-only (VERIFIED via your build notes). llama.cpp's
Vulkan backend runs on the Intel/AMD **integrated** GPUs that your target office laptops actually
have, and typically multiplies prefill several-fold even on iGPUs — it would also light up your own
RTX 4050 for demos. The honest costs: a second binary variant to bundle (~tens of MB), a driver
compatibility matrix you can't fully test alone, and a mandatory automatic-fallback design (spawn
Vulkan build → health-check fails or crashes → respawn CPU build, remember the choice). Verdict:
**not now.** Do it as a contained spike after Phases 4–7 land, behind a Settings toggle labelled
"Use graphics acceleration (experimental)". If it works on 70% of machines it's a step-change for
exactly the hardware tier you fear; if it doesn't, the CPU path you tuned remains the floor.
Transcription stays CPU regardless (CTranslate2 has no Vulkan; do not switch whisper engines for
this — see §8).

---

## 5. Change the shape of the wait (bigger than any flag)

### 5.1 Live transcription while recording — the headline idea

Today the pipeline is strictly serial: record 45 minutes → *then* transcribe (4–16 min) → *then*
beautify. But the machine is nearly idle during the 45 recorded minutes. Transcribing the audio *as
it is being recorded* — with base + low thread count, RTF only needs to stay under 1.0 — means the
transcript is ~95% finished the moment the counsellor clicks stop. **Perceived transcription time
collapses from minutes to seconds, on every hardware tier, including the i5.** No cloud service
feels faster than "it was already done."

Design sketch (deliberately additive — the current pipeline stays as the fallback and the durable
path):

- **Frontend:** keep MediaRecorder exactly as-is for the durable full recording (audio_queue upload
  at stop unchanged — the safety model is untouched). Add an `AudioWorkletNode` tap on the same
  merged stream that accumulates 16 kHz mono PCM and posts a WAV slice to the backend every ~60s of
  audio. Slice at a quiet moment: track a simple RMS window in the worklet and cut at the last
  ≥400ms-quiet point before the 60s mark, with ~1s overlap carried into the next slice (kills the
  mid-word-cut problem without fancy alignment).
- **Backend:** `POST /api/transcribe/live-chunk` (job_id, seq, wav bytes) → under `TRANSCRIBE_LOCK`,
  decode the slice with `initial_prompt` = the tail (~200 chars) of the accumulated text (keeps
  names/terms consistent across slices), append to an in-memory per-job transcript. Never touches
  disk (same in-memory rule as `/api/transcribe`). `POST /api/transcribe/live-finalize` decodes only
  the last partial slice and returns the stitched text into the Source pane.
- **Guardrails:** dedicated low thread count for live slices (e.g. 2 — must not make fans audible in
  a counselling room, must not starve the UI); auto-pause live decode on battery; hard-fallback — if
  any slice fails, silently stop live mode, the full recording still transcribes classically at stop
  (the user just gets today's behaviour, never an error mid-session). Opt-in Settings toggle
  ("Transcribe while recording"), default OFF for the first release, ON once pilots confirm fan/CPU
  behaviour is acceptable.
- **Bonus:** the accumulating text is itself the ultimate progress indicator — an optional collapsed
  "live transcript preview" in the Audio tab.

Effort: the biggest single item in this document (worklet + two endpoints + stitch QA ≈ 1–2 focused
weeks). Do it *after* the progress system and the Phase 4/5 tuning — but seriously, do it. For the
recording path (your core scenario), it beats the sum of every flag in §4.

### 5.2 Auto-chain and the backlog (checklist Phase 10 — promote two items)

- **Auto-transcribe on recording stop** (opt-in checkbox): today the stop-click → Transcribe-click
  gap is pure human dead time. Near-zero engineering (the blob and the call site already exist in
  `mediaRecorder.onstop`).
- **"Beautify automatically when this transcription finishes"** (already spec'd as Phase 10's first
  bullet, opt-in, default OFF): this plus §2.1's sleep fix is what makes "walk away and come back to
  finished notes" *actually true*, which is the real product promise for the backlog scenario. With
  §4.3's reasoning cut for digests, a 4-draft backlog on the weak tier plausibly drops from ~3 hours
  to nearer **1 hour, unattended, survives lid-closed-timer** (ESTIMATE).
- `BATCH_MAX = 4` vs queue cap 10: after §3.4's honest per-device estimates exist, raising the cap
  becomes a UI-copy decision instead of a trust risk — the modal can *show* "≈52 min for 8 notes on
  this computer" and let the counsellor choose.

---

## 6. Instrumentation to add while you're in there (cheap, sharpens every later decision)

1. **Stop deriving prefill/decode rates — llama-server reports them.** The final chunk of a
   streamed response (and every non-streamed response) from this server family carries a `timings`
   object (`prompt_per_second`, `predicted_per_second`, `prompt_ms`, `predicted_ms`). One line in
   `_chat`/`_chat_stream` beside `_capture_usage`:
   ```python
   if capture_stats is not None and data.get("timings"):
       capture_stats["timings"] = {k: data["timings"].get(k) for k in
           ("prompt_ms", "prompt_per_second", "predicted_ms", "predicted_per_second")}
   ```
   …logged into the beautify row's detail. Your Phase 3 derivations were careful and correct, but
   ground truth per-row means the Phase 5 benchmarks read themselves. (Field presence NEEDS one
   curl to confirm on b9585; if absent, the derivation stands.)
2. **Log the server's resolved defaults once per spawn:** after `_wait_for_server` succeeds,
   `GET /props` returns the effective settings (including what `-t -1` resolved to). Log
   `n_threads`/`n_ctx` into the `ai-server-start` row — then every future customer log answers "what
   was llama actually running with on this machine" without guessing.
3. **Machine tier on the `app-start` row:** `ram_gb` (via §4.2's `GlobalMemoryStatusEx`),
   `os.cpu_count()`, and the bounded `PROCESSOR_IDENTIFIER` env string. Non-PHI, and it makes every
   pilot's diagnostic log self-describing for the weak-tier question. Add `on_ac_power` to the
   beautify row too (your checklist already flags this as the one missing `[~]`).
4. *(Optional, dev-only)* `scripts/perf_report.py`: reads a diagnostic-log JSON export, prints
   per-action median/p90 of `duration_ms`, `rtf`, `ttft_ms`, prefill tok/s by
   `model_size`/`cpu_threads`. Saves you the by-hand spreadsheet step every test round.

---

## 7. How to test the weak tier without owning one

Everything above eventually collides with the same wall: **no i5/8GB machine has ever run this
app.** Options, best first:

1. **Buy one used.** An i5-8250U/8GB/SSD ThinkPad-class machine is ~NZ$150–300. It is the single
   highest-ROI purchase available to this project — it's literally the customer's computer, it
   makes every benchmark real, and it doubles as the clean-machine smoke-test box your release
   checklist keeps needing (§6 restore drill, installer tests). If cash allows, do this and skip
   the simulations.
2. **VirtualBox VM** (Windows 11 Home has no Hyper-V): 4 vCPU + 8GB RAM. CPU-bound scaling shape and
   — critically — the **RAM ceiling/paging behaviour of §4.2** reproduce well; absolute speeds are
   only approximate (VM overhead, your faster memory). Free, today.
3. **Affinity + power-plan approximation on the Vivobook:** run the whole backend pinned to 4
   logical cores (`$p = Start-Process ... -PassThru; $p.ProcessorAffinity = 0x0F`) with Windows
   power mode set to "Best power efficiency". Roughly emulates core count and lower clocks; does NOT
   emulate the narrower memory bus. Label results accordingly.
4. **The pilot fleet is the real benchmark.** This is the quiet payoff of the Support Diagnostic
   Log: with §6.3's tier fields added, every pilot counsellor who emails you a log is contributing a
   hardware-tier datapoint. 3–5 pilots = the distributed test lab you don't otherwise have.

---

## 8. What I would NOT spend time on (protect your energy — you don't have spare)

- **Speculative decoding / draft models** — RAM cost and complexity, weak CPU gains at this model size.
- **Quantizing below Q4** — quality cliff for clinical prose; the product *is* the writing quality.
- **Swapping transcription engines** (whisper.cpp etc.) — churn and re-validation for a gain that
  tuned faster-whisper + batched mode largely matches on CPU.
- **NPU offload** (Core Ultra NPUs) — toolchains aren't shippable for your stack yet.
- **Running Whisper and llama concurrently to "use the whole CPU"** — they'd fight for the same
  cores and memory bandwidth; your sequential-engines product decision (the 2d/2e mutual-exclusion
  work) is *correct* performance engineering, keep it.
- **React/render micro-optimisation** — the UI is not the bottleneck anywhere I looked.
- **Raising `-c` or `max_tokens` further** — the opposite direction is the win (§4.2).
- **Chasing cloud-tool latency parity** — wrong bar; see §10.

---

## 9. Suggested order of execution

| # | Change | Where | Effort | Expected effect (mid / weak tier) | Risk |
|---|---|---|---|---|---|
| 1 | Sleep pulse (§2.1) | new `services/power.py` + 5 call sites | ~1 day | kills "stalled overnight batch" class entirely | none |
| 2 | Pipe drain (§2.2) | `services/ai.py` | ~½ day | removes latent hang class; better diagnostics | none |
| 3 | Transcription progress (§3.1) | `whisper_service.py`, `transcribe.py`, `audio_queue.py`, `SessionsPage.tsx` | 2–3 days | the product stops looking frozen | none |
| 4 | Beautify staged progress (§3.2) | `ai.py`, `sessions.py`, `api.ts`, `SessionsPage.tsx` | 3–5 days | 92–298s dead window becomes live status | low (SSE shape change — two consumers, both updated together) |
| 5 | Whisper threads decision (§4.1) | your Phase 5 harness → `CPU_THREADS` | in flight | −20–30% transcribe | none if output-hash-verified |
| 6 | llama `-t/-tb/-ub/-fa` bench (§4.4) + KV/ctx right-size (§4.2) | `ai.py` spawn args | 2–4 days bench | prefill ×2–3 plausible → Beautify −30–40%; 8GB tier saved from paging | benchmark-gated |
| 7 | Reasoning A/B (§4.3) | spawn flag + quality review | 1–2 days | −20–26% Beautify; −40–70% digest/take-away | quality-gated, explicit go/no-go |
| 8 | faster-whisper 1.2.1 + batched (§4.6) | your Phase 6 | 3–5 days | transcribe ×1.5–3 on top of threads | parity-tested per your plan |
| 9 | Honest estimates + battery chip (§3.4/3.5) + auto-transcribe-on-stop + auto-beautify opt-in (§5.2) | frontend + small backend | 2–3 days | "walk away" promise becomes real | low |
| 10 | `--cache-reuse` (§4.5) | `ai.py` | ~1 day | re-runs & template ops much faster | low |
| 11 | Live transcription while recording (§5.1) | worklet + 2 endpoints | 1–2 weeks | **perceived transcribe ≈ 0 on all tiers** | contained (opt-in, full fallback) |
| 12 | Vulkan spike (§4.9) | build pipeline | spike later | possible step-change on iGPU machines | needs fallback design |

Cumulative projection for one 45-min session (ESTIMATE — verify at your Phase 8 reality check):

| | Today | After #5–8 | After #11 too |
|---|---|---|---|
| Mid-tier (your Vivobook) | ~4.5 min + ~6 min ≈ **10.5 min** | ~1.5–2.5 + ~3.5–4.5 ≈ **5–7 min** | ~0 + ~3.5–4.5 ≈ **4–5 min visible** |
| Weak tier (i5/8GB) | ~11–16 + ~12–18 ≈ **25–34 min** (worse if paging) | ~4–7 + ~6–9 ≈ **10–16 min** | ~0 + ~6–9 ≈ **6–9 min visible** |

That takes the weak tier from "genuinely fails" to "runs during the between-sessions gap while
visibly working," and the mid tier to your stretch target.

---

## 10. The bottom line — is this sellable?

Objectively, as asked, no favours:

1. **Your fear is directionally correct.** Today's build on an average office i5 would take
   ~25–35 minutes of *silent* processing per 45-minute session. Counsellors would conclude it's
   broken. If nothing changed, the product would be very hard to sell to that tier. You were right
   to escalate this above feature work.
2. **The problem is not architectural.** Nothing in this review says "rewrite it." The engines are
   the right engines; the pipeline is clean; the instrumentation is genuinely good. The gaps are:
   an untuned engine surface (threads/batch/flash-attn/context were all still at defaults —
   confirmed in code), one RAM landmine on 8GB machines, two reliability bugs (sleep, pipes) that
   masquerade as slowness, and a total absence of progress feedback. Every one of those is normal,
   fixable engineering — the kind every real product goes through — not evidence the product is
   doomed.
3. **The bar is not cloud speed.** Heidi-class cloud scribes return notes in seconds by shipping
   the audio to a datacenter. You will never match that on a 4-core laptop, and you don't have to:
   your customer chose you *because* the audio never leaves the room. The bar for that customer is
   (a) done reliably within the natural gaps of their day, (b) visibly working the whole time,
   (c) they can walk away and trust it finishes. Sections 2, 3 and 5 are (b) and (c); section 4
   gets (a) inside the gap on both tiers. All three are reachable from where the code stands today.
4. **Sequence for morale as much as for engineering:** items #1–4 of the table are a fortnight of
   low-risk work that transforms how the product *feels* before a single benchmark decision is
   made. Do those first — partly because they're right, partly because watching a real progress bar
   crawl across your own screen will do more for your motivation than any percentage in this
   document.

You've carried this alone further than most funded teams carry products with help. The data you
collected is what made this review possible — that was the hard, unglamorous part, and it's done.
The path from here is enumerated above, one reversible step at a time, exactly the way you've been
working already.

---
---

# ✅ MAKE-IT-FAST EXECUTION CHECKLIST (tick as you go)

Groups follow the §9 execution order. Section references (§2.1 etc.) point back up into the review
above for the full reasoning and code snippets — don't re-derive, just scroll up.

## Current Status (update this block every session — single source of truth for this initiative)

**2026-08-01 — Machine-attribution repaired; durable-job orphan fixed; live-transcription
fidelity kill test run. Full record: `bugs-fixed/056-01082026(NewFindings).md`.**

1. **The 29-July baseline, ubatch-2048 A/B, and reasoning-1024 A/B (item 6/8 below and
   `053`) actually ran on jp-start, not the Dell** as this file and `CLAUDE.md` stated.
   Confirmed by direct hash reproduction on jp-start (identical seed/prompt/fixture/thread
   config reproduced `053`'s `long-private` output byte-for-byte, 3/3 reps) plus matching
   decode-rate signatures. The genuine Dell dataset is `054`'s Flash A/B and its same-day
   baseline confirmation only. Closure decisions unaffected; only the machine label was
   wrong. `CLAUDE.md`, the Flash handover, and `OpusPerformanceReview.md` corrected in place.
2. Ported machine/git/runtime attestation into `benchmark_beautify_first_run.py` (previously
   captured zero machine identity — the root cause item 1 exploited undetected for 3 days).
   Fails closed on a requested/resolved thread mismatch. 17 new tests, all pre-existing 36
   still pass.
3. Fixed a verified silent-failure gap: a bulk Transcribe & Beautify group interrupted by a
   crash mid-`_finalize_group` rolled back to `status='transcribed'` (Source-safe) but was
   never resumed — the only process-start query selects `pending` rows only, so the
   counsellor's requested note silently never arrived. New
   `resume_interrupted_structuring()`, called from `main.py` startup in a background thread.
   7 new tests. Not yet click-through verified via an actual force-kill-and-relaunch.
4. Ran the offline live-transcription slice-replay fidelity kill test (both reviews' #1 cheap
   decisive experiment) across all 5 fixtures — **KILLED as designed**. Real clinically-material
   content loss on 4/5 fixtures (12 missing spans ≥5 words total), including one statement the
   practitioner's own words flag as important, plus a generalising repetition-loop insertion
   risk neither prior review anticipated. Mechanism differs from batched Whisper (boundary
   seams, not structural chunk-independence) — reopening requires a larger-overlap/
   boundary-reconciliation re-test, not a UI build. See `bugs-fixed/056` §3.
5. No 135U/16 GB machine was available this session; exact commands are prepared in
   `bugs-fixed/056` §5 and are the single highest-priority next step — every remaining
   product decision (signed SLOs, thread default, whether live transcription is load-bearing)
   is blocked on it.

---

**2026-07-30 — PRIVATE Flash Attention experiment complete; 1024,
`-ub 2048`, and forced `-fa on` rejected.**

1. Privacy-safe per-item Bulk telemetry is built (`768c944`). The aggregate
   row remains, and each note request now records exact visible TTFT separately
   from hidden reasoning plus prompt/cache/decode/completion/outcome data.
2. Bundled b9585 ignores request-scoped `reasoning_budget`; startup-scoped
   control is proven (`a326582`). Production was not changed.
3. The byte-frozen short PRIVATE + long TE POU cold/warm A/B completed eight
   full requests. At 1024, aggregate visible TTFT changed `+0.014%` and total
   duration changed `+5.121%`; direction was unstable. Blind-reviewed quality
   was non-inferior, but the performance gate failed.
4. Written decision: **keep `auto/3072`; do not test 512/off under this staged
   gate.**
5. Exact immediate prompt reuse is proven (`99.88–99.94%`, five tokens newly
   evaluated), but repeat runs are not the normal workflow. Warm/cache results
   remain diagnostic and pre-warm is secondary.
6. Commit `67c3f9e` adds the four-role first-run harness. Three cold runs per
   role establish median totals of `129.453s`, `218.297s`, `174.968s`, and
   `227.375s`; all 12 calls stopped normally, were untruncated, retained exact
   heading order, reopened as DOCX, and left fixtures unchanged.
7. The exact no-completion tokenizer audit closes prompt contribution:
   Source is `79.5–84.2%` and fixed rules `12.9–17.1%` of long/template-heavy
   prompts; labels/guidance are too small for the required minute-scale win.
8. The single-variable `-ub 512` versus `2048` matrix completed 24 cold calls.
   Candidate median aggregate prompt time was `-4.309s`, visible time
   `+25.062s`, and total `+6.251s`. Blind review found a TE POU placement
   regression and a critical Psychiatric attribution/risk regression.
   **Reject `2048`; do not change production.**
9. The controlled `-fa auto` versus forced `-fa on` matrix completed 24 cold
   calls. Forced `on` made the short, long PRIVATE, and Psychiatric median
   totals `25.047s`, `19.813s`, and `22.562s` slower; NDIS improved only
   `4.844s`. Paired aggregate direction was unstable. Blind pairs were
   byte-identical, but both conditions shared material provenance, factual,
   risk, omission, and template-completeness defects. **Reject forced `on`;
   keep `auto`.** The routine 2–3-minute first-run target remains unmet.
10. Commit `efce97f` adds opt-in post-timing run-local reasoning capture for
    subsequent fake/de-identified tests. It is off by default, refuses
    packaged/audit/unsafe destinations, and did not cause a rerun of the 24
    calls. No production prompt, reasoning, model, or engine default changed.
    Next, repair/measure shared factual-provenance quality and record memory
    ground truth before selecting another isolated speed candidate. MTP has
    not started. Daily Korean record:
    [`thoughts/핵심-30072026.md`](../../thoughts/핵심-30072026.md);
    `thoughts/한국.md` remains the 2026-07-29 historical strategy note.

Full record:
[`bugs-fixed/054-30072026(SOL).md`](../../bugs-fixed/054-30072026(SOL).md).
For a new session, read that file and the completed Flash handover first.
Preserve the one-variable matrix, blind gate, and production defaults.

---

**2026-07-17 (later same day, fourth pass) — 2.5 wrapped up as far as it's going for now; two items
explicitly parked by user judgment call, not forgotten.**

1. **Batch modal ETA — FIXED.** Replaced the stale hand-written "~45-minute session takes about
   10–15 minutes" copy (`SessionsPage.tsx`, the batch intercept banner) with a real per-device
   estimate: new `batchEtaTotal` state + a `useEffect` (keyed on `batchQueue`/`batchPhase`) that
   calls `api.getBeautifyEta()` once per selected note (notes in a batch are rarely the same length,
   so summing per-note ranges is more honest than reusing one global number) and sums the low/high
   across all selected items. Falls back to honest "no estimate for this computer yet… gets smarter
   after a few notes" copy when there's no history yet — never the old fixed number. New
   `formatEtaSeconds()` helper (next to `secsToMMSS`) renders the summed range as "Xs"/"X min".
2. **Soft "this is an estimate, not live" disclaimer — DONE, wording finalized with user.** Added to
   all four places a simulated/estimated progress figure appears: the single-Beautify overlay, the
   batch modal's upfront banner, the batch queue per-item row (short form: "(estimated, not live)"),
   and the meetings-summary overlay. Final wording (user-edited): *"This is an estimated progress
   indicator, not a live measurement. Processing is still underway while this message is visible."*
   — same sentence reused verbatim in the three longer-form spots; the queue row uses the short form
   only because of real space constraints (~220px row).
3. **Battery chip (§3.5) — built, then explicitly REVERTED at user's request, parked for later.**
   A working version existed briefly this session: `GET /api/system/power-status` (system.py,
   reusing the existing `activity_log.on_ac_power()` WinAPI probe, no licence gate — same triviality
   as `/health`), `api.getPowerStatus()` (api.ts), and an amber chip in the single-Beautify overlay.
   User said to hold off — fully reverted (backend endpoint removed, frontend method removed, chip
   JSX removed; confirmed zero leftover references via repo-wide grep for
   `onBattery|getPowerStatus|BatteryLow|power-status|power_status`). `tsc --noEmit` and `py_compile`
   both clean after the revert. **Not abandoned — parked.** If picked up later, the design above is
   the known-working shape; no rediscovery needed.
4. **Settings "Higher Accuracy" real-multiplier copy — PARKED, not built, by explicit user judgment
   call.** Reasoning given: users already intuitively understand the heavier/slower model is
   heavier and slower — the real-measured-multiplier copy the original review wanted is a nice-to-
   have precision upgrade, not a "does it feel broken" fix, and not worth the backend aggregation
   work (a new `whisper_model`-keyed multiplier lookup, mirroring `get_beautify_eta`'s shape) right
   now. Revisit only if real user confusion about Higher Accuracy's slowness ever surfaces.

**2.5 is done for practical purposes** — the two remaining boxes below are parked, not oversights.

**Next up: Group 3 (instrumentation for the tuning phases, §6)** — land before any Group 4
benchmark work starts (llama `timings` capture, `GET /props` resolved-defaults logging, machine-tier
fields on `app-start`). Explicitly deferred to a later session per user ("prob move onto group 3
later") — not started this session.
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

---

**2026-07-17 (later same day, third pass) — Both real "feels frozen" gaps from the audit below
FIXED, user chose "both, batch first then meetings."**

1. **Batch "Beautify All Drafts" queue — per-item live progress, DONE.** Added
   `batchItemPct`/`batchItemEta` state + `startBatchItemProgress`/`finishBatchItemProgress`/
   `stopBatchItemProgress` (`SessionsPage.tsx`, right after `stopPrepProgress`) — same eased-curve
   math as the single-Beautify overlay, same real per-device ETA via `api.getBeautifyEta()`, scoped
   to whichever queue item is currently running (the loop is strictly sequential, so this is safe).
   `handleBatchBeautify`'s loop now starts progress before each item's `api.beautifyNotes` call,
   passes a real `onToken` callback (was `undefined` before — batch items got literally zero token
   callback previously) that snaps to 100% on first token, and stops progress in `finally` so it
   never leaks into the next item or a cancelled/errored run. Queue row UI: "Structuring…" now shows
   a live `%`, plus a thin bar + "usually ~Xs" ETA text under the item's title/word-count line,
   only while that row is the one actually running. **The stale batch-modal ETA copy from 2.5
   ("~45-minute session takes about 10–15 minutes") was intentionally left alone** — a separate,
   smaller item, not touched this session (still open, see 2.5 below).
2. **Meetings "Generate Summary" — SSE streaming, DONE.** Backend: extracted
   `_build_meeting_summary_messages()` out of `summarize_transcript_service` (ai.py) and added
   `summarize_meeting_stream()` mirroring `beautify_notes_stream`'s shape; new
   `POST /api/summarize/meeting/stream` in `system.py` mirrors `sessions.py`'s `/ai/beautify` SSE
   endpoint exactly — same `start_action`/`finish_action` diagnostic pattern (action name
   `summarize-meeting`, unchanged, for log continuity with the old non-streamed calls), same
   `_beautify_error_code`-shaped classifier (duplicated locally as `_summarize_error_code` rather
   than cross-importing a router-private helper). **Sanitizer ordering, the one thing that had to be
   right:** input is sanitized before prompting (unchanged); streamed tokens are a live preview only;
   the backend re-runs `sanitize_professional_text` on the FULLY accumulated text and sends it as its
   own `{"final": ...}` SSE event right before `[DONE]` — the frontend replaces its buffer with this
   exact string, so what gets saved is byte-identical to what the old non-streamed endpoint would
   have produced, never a pre-sanitize streamed preview. Frontend: `api.summarizeMeetingStream()`
   (api.ts) mirrors `beautifyNotes`'s SSE parser + the `final`-event handling; `MeetingDashboard.tsx`
   gained a small local eased-curve "preparing" overlay (`summaryAwaitingFirstToken`/
   `summaryPrepPct`, kept as its own copy rather than importing SessionsPage's version — the two
   files don't currently share a module for this) over the summary textarea, fading out on first
   token; button label now reads "Reading your notes…" → "Writing…" instead of the old static
   "Generating locally...". Reporting-summary/take-away staged labels (2.4's other two items) were
   **not** touched this session — still open.
   **Live-verified against the real backend (not just code-read):** `TestClient` POST to
   `/api/summarize/meeting/stream` actually spawned the real bundled `llama-server.exe`, streamed
   ~115 real SSE token events for a real meeting-mode prompt, emitted one `{"final": ...}` event
   with real sanitized markdown output, then `[DONE]`; confirmed 3 real `activity_log` rows under
   action `summarize-meeting`/workspace `meetings` with the full non-PHI detail payload (chars,
   ttft_ms 18–28s, cold_start, input/completion/prompt tokens, reasoning_chars) — matching the
   beautify path's diagnostic shape exactly.
3. **Verification done:** `npx tsc --noEmit` clean after both fixes; `py_compile` +
   full backend import (138 routes, was 137 — the one new endpoint) clean; full
   `run_security_tests.py` suite (incl. `test_power.py`) passes unchanged; the live `TestClient`
   run above for meetings-summary. **Not done:** an actual click-through in the real Electron/React
   desktop UI for either fix (watch the batch queue bar move across 2+ real drafts; watch the
   meetings overlay fade into live streaming text) — this session validated the backend live and the
   frontend via `tsc`, but did not drive the compiled UI by hand. Per this doc's own rule ("Done =
   verified on the real desktop app, not code written"), log that UI pass here before calling either
   fix fully closed.

**Next up:** the real desktop-UI click-through for both fixes above; then, if continuing 2.5, the
still-stale batch-modal ETA copy (`SessionsPage.tsx` ~4207-4225) is the next small, cheap item —
swap it for a `get_beautify_eta`-style real estimate the same way the per-item bar now does.
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

---

**2026-07-17 (later same day, second pass) — Group 2.3–2.5 audited against real code before
building anything new, per user's explicit instruction ("audit first, only fix what genuinely
feels frozen").** Findings, most important first:

1. **2.3 (Beautify staged progress) is ALREADY BUILT for single-session Beautify — via a better
   design than this doc originally sketched, not the one written above.** The doc's sketch wanted
   real `/slots` polling + a live reasoning-char SSE heartbeat. That backend half genuinely exists
   (`get_prefill_progress()` + `GET /api/ai/progress` in `ai.py`/`sessions.py`) but is **dead code —
   `api.getAiProgress()` is defined in `api.ts` and never called from anywhere in the frontend.** It
   was superseded: a code comment at `SessionsPage.tsx:991-999` explains the real `/slots` percentage
   was tried and rejected because the true prefill window is often shorter than any safe polling
   interval, so the number would randomly read 0%/100%/flip — "looked broken even when the model was
   working correctly." What shipped instead (`startPrepProgress`/`computePrepPct`/`finishPrepProgress`,
   `SessionsPage.tsx:991-1080`, overlay at `~6510-6553`): a hand-tuned eased curve that fills toward an
   88% cap over the first ~90s then crawls, labelled with a **real per-device ETA range** from
   `api.getBeautifyEta()` → backend `get_beautify_eta()` (nearest-neighbour off this machine's own
   `beautify-single` history), and snapped to 100%/"Writing your note…" the instant the real first
   token streams. Stages A+B are merged into one "Understanding your session…" bar rather than kept
   separate — reasonable, since the doc's own goal (kill the dead silent window) is fully met this
   way. **Verdict: 2.3 for single Beautify needs no further work.** The dead `/api/ai/progress`
   endpoint + `getAiProgress()` client method are candidates for deletion later (not urgent, zero risk
   either way) — do not build a consumer for them; the simulated approach is the better design and is
   already shipped.
2. **Real gap found: the Batch "Beautify All Drafts" queue has NO per-item live progress at all** —
   confirmed in code (`SessionsPage.tsx` queue list ~4270-4289): a running item shows only a plain
   spinning `Loader2` icon, no bar, no elapsed time, no ETA, for however long that single note's
   Beautify takes (multi-minute on a real session). The header updates between items ("X of Y done")
   but nothing moves *during* an item. This is the single Beautify overlay's exact "looked frozen"
   problem, un-fixed, sitting in precisely the "walk away and come back to a finished backlog"
   scenario this whole initiative exists for (§5.2, memory: batch/backlog "walk away" scenario).
   Arguably now the single biggest real "does it feel stuck" gap in the app, since single-Beautify
   already got fixed. **Not yet fixed — candidate for this session's actual work.**
3. **2.4 (other silent spinners) is NOT built, confirmed in code, exactly as the doc says.** Meetings
   "Generate Summary" (`MeetingDashboard.tsx:615-628`, button at `~1124-1133`) is a fully non-streamed
   `await api.summarize(...)` showing only a static "Generating locally..." spinner — for a real
   60-min meeting transcript on weak hardware this is a many-minute blind wait, unchanged from the
   doc's original assessment ("the worst remaining one in the app once Beautify gets §3.2" — and now
   that Beautify *has* gotten it, this is literally the worst one left). Reporting summary
   "Generate summary" (`runDigestGeneration`, button ~6913-6961) and take-away are similarly
   unstaged: during generation the button just swaps to a red "Stop" — abortable, but no percentage/
   stage text either. **Not yet fixed.**
4. **2.5 (honest estimates) is PARTIALLY built.** The real per-device ETA mechanism
   (`get_beautify_eta`/`get_visual_observation_eta` in `activity_log.py`, nearest-neighbour off real
   completed-op history) is a proven, already-twice-used pattern and powers the single-Beautify
   overlay (see #1). But the **Batch modal's estimate copy is still the old hand-written
   "~45-minute session takes about 10–15 minutes" text** (`SessionsPage.tsx:4207-4225`,
   confirmed unchanged) — exactly the copy §3.4 wanted replaced, sitting right next to the real gap
   in #2. No battery chip anywhere (`grep` for battery/on_ac_power in `src/` = zero hits) — real gap,
   but low priority since it's a trust/honesty feature, not a "feels frozen" one.

**Net: no new backend mechanism is needed** — `get_beautify_eta`-style history lookups and the
eased-curve overlay pattern already exist and are the right shape to extend, not replace. The two
live "feels frozen" gaps (batch queue per-item, meetings summary) plus the stale batch-modal copy
are the only things worth building next; everything else in 2.3–2.5 is either already shipped or
correctly low-priority.

**Next up:** pick one lever (per this doc's own rule) — batch-queue per-item live progress
(reuses the existing eased-curve/ETA pattern, smallest step, hits the backlog scenario directly) vs.
meetings-summary SSE streaming (bigger — mirrors Beautify's `_chat_stream` plumbing, needs the
meeting-mode sanitizer applied to the final text only, per §3.3) — awaiting user's choice.
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

---

**2026-07-17 (later same day) — Group 2.1/2.2 (transcription progress) audited: already built,
doc was stale. Two real gaps found and fixed.** User asked to move to 2.1 and questioned whether it
was already built — a code audit (not the doc) found the whole progress-bar feature genuinely
implemented in both workspaces under different names than this doc originally sketched (see 2.1/2.2's
entries below for the full detail). Two real gaps survived the audit and were fixed this session: (1)
`GET /api/transcribe/progress` had no licence gate at all, unlike its sibling `/transcribe/cancel` —
added `category` param + `require_active_license`, updated `api.ts` + both page call sites, verified
live via `TestClient` that both workspaces still 200 correctly; (2) the cold model-load window (6–8s,
`pct === null`) showed the same generic "Transcribing..." text as real decoding — added the
"Preparing the transcription engine…" copy the plan always wanted, in both `SessionsPage.tsx` and
`MeetingDashboard.tsx`. `tsc --noEmit`, `py_compile`, full backend import (137 routes), and
`run_security_tests.py` all clean/passing after both fixes. **Not done:** a real runtime click-through
on the desktop app (record → watch the bar/copy actually change) — this session was a code audit +
two targeted fixes, not a UI test pass.

**Next up:** the honest options, in rough order of value: (a) do the real runtime click-through for
2.1 now that the two fixes are in, closing it out properly; (b) given 2.1/2.2 turned out already
built contrary to the doc, it's worth briefly re-checking 2.3–2.5 the same way before assuming they're
genuinely still open — don't re-build something that already exists; (c) if 2.3–2.5 really are open,
2.3 (Beautify staged progress) is the biggest remaining "nothing shows" gap (92–298s dead window on
long sessions) but needs Group 0 item 0.1 answered first (`/slots` field names — still open).
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

---

**2026-07-17 — Group 1.2 (llama-server pipe drain, §2.2) DONE and verified live.** Fixes the
structurally-real hang risk (Windows pipe buffer fills → child's next stderr/stdout write blocks
forever → server freezes mid-request) by draining both pipes into a bounded 200-line ring buffer on
daemon threads started right after `Popen`. The logging half is genuinely upgraded, not just
retained: startup failures now log llama.cpp's real root-cause line (not just a generic timeout),
and Group 0 item **0.4** is answered from a real spawn on this machine (this build has no isolated
"KV size" line — it prints a total memory projection instead, 1843 MiB at `-c 32768` for
gemma4-e2b-qat on 32GB). One real bug caught and fixed during implementation, not just planned:
`activity_log.sanitize_error()` collapses multi-line text to its last line only (correct for
tracebacks, wrong for llama-server's tail, whose last line is usually the least specific one) — added
`_format_tail_for_log()` to join the last few ERROR-severity lines into one logical line first, so
the real cause survives sanitize_error's collapse while still getting its path-scrub + length bound.
Verified against the real bundled `llama-server.exe` + real model on this dev machine (see 1.2's
checklist entry for the three live cases run and their actual output): normal spawn, early-death on a
missing model file (root cause correctly logged, `C:\Users\<name>\...` correctly scrubbed to
`<user>`), the vision on/off model-switch path (old process cleanly terminated before new `Popen`, no
thread leak), and a 25-completion soak against one running server (no hang, latency flat, ring
buffer capped correctly). Not fully covered: a real multi-minute mixed beautify/digest/take-away soak
(the original "20+ AI ops" ask) — the 25-short-completion soak stresses the actual failure mechanism
(pipe fill under log-line volume) but isn't the same as the real op mix; worth doing before declaring
the whole MakeItFast initiative shippable, not blocking for this item alone. Full detail, all three
live-test transcripts summarized: 1.2's checklist entry below.

**Next up:** Group 1 is now fully done (1.1 + 1.2 code-complete; 1.1 still needs its human
runtime-verify pass — see 1.1's own checklist). Natural next step per §9 order is Group 2 (progress
system) — but Group 0 items 0.1–0.3 and 0.5 are still open fact-check spikes that de-risk Group 2/4
cheaply; consider knocking those out first, especially 0.1 (`/slots` field names) since it directly
gates 2.3's design.
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

---

**2026-07-16 — Keep-awake / sleep-reliability (Group 1.1) rebuilt as a full app-wide system.**
This item was originally sketched in §2.1 above as a backend-only fix ("pulse from inside the
transcribe/beautify work loops"). That sketch **undercounted the scope** in two ways: (1) live
audio recording happens in the Electron renderer via `MediaRecorder`, which the Python backend
cannot see at all, so a Python-only pulse can never protect a recording; (2) a single pulse
before a long blocking call (a whole non-streamed `_chat()`, or the silent llama-server prefill
wait before the first streamed token — measured at up to ~298s ttft on a long session, §1.1
above) doesn't reach a laptop with an aggressive sleep timer, because `ES_SYSTEM_REQUIRED`
resets the idle countdown once, not continuously. The rebuilt version below fixes both gaps.
**Two coordinated mechanisms now exist:**
1. **Electron (`electron/main.js` + `preload.js`)** — a reference-counted
   `powerSaveBlocker('prevent-app-suspension')`, held for exactly the span of a live recording,
   started/stopped via a narrow `startRecordingProtection`/`stopRecordingProtection` IPC pair
   called from `SessionsPage.tsx` / `MeetingDashboard.tsx`. Never `prevent-display-sleep` — the
   screen can still turn off. Safety-net resets (`forceStopRecordingProtection`) fire on renderer
   crash (`render-process-gone`), reload/(re)load (`did-finish-load`), window close, and every
   app-quit path, so a start can never survive past its renderer.
2. **Backend (`backend/services/power.py`)** — `pulse_keep_awake()` (throttled ≤1 call/30s
   `SetThreadExecutionState(ES_SYSTEM_REQUIRED)`, for loops that already iterate every few
   seconds) and `keep_awake_during()` (a background daemon-thread pulse for calls with **no**
   loop of their own to hook into — covers the prefill blind spot above). Wired into all 4
   Whisper segment-decode call sites and the 2 `ai.py` chat choke points (`_chat`/`_chat_stream`)
   — since every AI operation in the app routes through those two functions, this covers
   beautify, digest, take-away, template mapping, reporting summaries, meeting/clinical
   summarize, drawing observation, and the Visual Observation Record with **zero** per-feature
   duplication. Full call-site list and rationale in the rewritten §1.1 section below.
**Status: code complete.** `backend/test_power.py` (15 tests: throttling, thread-safety,
exception-safety, non-Windows no-op, background-thread start/stop lifecycle, repeated
start/stop cycles) passes, registered in `run_security_tests.py`. `npx tsc --noEmit` clean.
`backend/main.py` imports clean with all 137 routes registered. `electron/main.js` and
`preload.js` pass `node --check`. **The 14-point manual runtime validation checklist is NOT
yet run** — it requires a human to physically shorten the Windows sleep timer and leave real
hardware unattended for several minutes per scenario (recording, each single/bulk
transcribe/beautify combination, cancel paths, forced errors, window/app close mid-job,
overlapping activities), which cannot be executed or observed from inside this coding session.
Per this doc's own rule below ("Done = verified on the real desktop app, not code written"),
**do not consider this initiative shippable until that pass is run and recorded here.**

**In plain English — what today's testing (2026-07-04) actually found:** we tried two different
speed tricks for the AI note-writer. Trick 1 (more CPU threads at once) made it slower, not faster,
so we undid it. Trick 2 (skip the AI's invisible "thinking" step) made it a lot faster — but our
first check of the output looked like it made up a different client's name, which would have been a
dealbreaker. That turned out to be a mistake in how we set up the test, not a real problem — once we
fixed our understanding, the fast version looked just as good. But since the test was set up in a
confusing way, we're not confident enough to trust it yet, so both tricks are currently switched
back off — **nothing changed for real usage today.** We also found and fixed a bug where editing a
session's title while a note was being written could get silently lost, and spotted (but haven't
fixed) a case where returning to a session doesn't show the "still writing" indicator even when it's
still going in the background.

**Branch:** `performance-optimization`
**Last updated:** 2026-07-04 — Group 4.3 (llama thread/prefill flags) and Group 4.4 (reasoning phase)
both coded and first-tested directly on the real desktop app, ahead of the Group 0 spikes below
(which are all still untouched). Full detail lives in `CODEX-SONNET5-CHECKLIST.md` Session 7 —
this file only mirrors the one-line results, per the "tick THERE, mirror here" rule below.
- **4.3 llama thread flags: REJECTED.** `-t 9`/`-tb 16` tested against a same-prompt-token-count
  baseline — a clean +65% ttft / +64% duration regression, not a win. Reverted to `-1`/`-1`.
- **4.4 reasoning off: initial NO-GO RETRACTED same day — corrected status is INCONCLUSIVE.** ≈2.4×
  faster on Beautify. First read of the exported note looked like a fabricated second client ("Moon"
  → "Sarah"/"James"), but that was a false alarm — the test recording was a real YouTube
  couples-therapy session (Sarah/James) run under an unrelated demo client profile ("Moon"), so
  "Sarah"/"James" were correct. Re-read: `auto` was actually the one with the bigger fidelity
  problem (collapsed both real people into one, "Moon"). `off` was not lower quality on this sample —
  but the test is confounded by the mismatched demo name, so it isn't a clean read either way.
  `LLAMA_REASONING` stays at `"auto"` pending a clean re-test. Full write-up + correction:
  CS-CHECKLIST Session 7. Other op classes still untested.
**Historical next-up text, superseded 2026-07-30:** do not re-run `off`, 512,
or 1024 under this gate. The controlled 3072/1024 work rejected 1024, the
later first-run work rejected `-ub 2048`, and the completed 24-call Flash
matrix rejected forced `-fa on`. Production remains `-fa auto`; shared
factual/provenance quality and memory ground truth precede another engine
candidate. Group 0 spikes remain open.
**How to resume in a new session:** "continue the MakeItFast checklist" — this file is the full context.

## Rules (same discipline as CODEX-SONNET5-CHECKLIST.md)

- **One lever per change.** Never combine a tuning change with a feature change in one commit.
- **"Done" = verified on the real desktop app, not "code written."** Benchmark items are done when
  *measured and a decision was recorded*, not when the script ran once.
- **Never silently lower output quality.** Anything quality-adjacent (reasoning, beam, KV quant,
  model lineup) gets an explicit A/B and a written go/no-go.
- **Overlap note:** items marked **(= CS Phase N)** are already tracked in
  `CODEX-SONNET5-CHECKLIST.md`. That file stays the detailed tracker for those — tick them THERE,
  and only mirror a one-line `[x]` here when adopted, so the two files never disagree.
- Every new diagnostic field: numbers/bools/bounded strings only — no PHI, no filenames, no text.

---

## Group 0 — Fact-check spikes (do first; each is ≤1 hour and de-risks a whole group)

- [ ] **0.1** With a Beautify in flight, `curl -H "Authorization: Bearer <key>" http://127.0.0.1:8080/slots`
      — record the actual field names b9585 returns during prompt processing (looking for
      n_past / n_prompt_tokens / progress-like fields). Decision: real prefill bar vs estimated bar
      (§3.2 Stage A). Write the answer here: ______
- [ ] **0.2** Check one non-streamed `_chat` response and one final streamed chunk for a `timings`
      object (`prompt_per_second` etc.) (§6.1). Write the answer here: ______
- [ ] **0.3** Curl test: does a request-level `"reasoning_budget"` (or similar) field work on this
      build, or is reasoning control spawn-flag-only? (§4.3). Write the answer here: ______
      **Still worth doing (2026-07-04, corrected): full `--reasoning off` speed win is real (≈2.4× on
      Beautify) and the initial quality-fail finding was retracted (see 4.4 below) — status is
      INCONCLUSIVE, not failed. If per-request control works, a middle-ground/per-op budget could be
      tried without a global server-wide flag change, regardless of how the reasoning A/B lands.**
- [x] **0.4** Read the drained llama-server startup log (after Group 1.2 lands) or Task Manager
      right after spawn: record the actual KV-cache reservation at `-c 32768`. Write it here:
      **Answered 2026-07-17, live spawn on the Vivobook (32GB, gemma4-e2b-qat, `-c 32768`):
      this bundled llama-server build does NOT print an isolated "KV cache size" line — the
      closest real ground truth it exposes is a one-line total-memory projection:
      `common_params_fit_impl: projected to use 1843 MiB of host memory vs. 32363 MiB of total
      host memory`. 1843 MiB is the actual working-set projection for model + KV + overhead at
      32k context on this model — this is the number §4.2's RAM-aware sizing should reason
      about, not a separate isolated KV figure. Now auto-captured every spawn (see 1.2 below).**
- [ ] **0.5** Decide the weak-tier test rig (§7): buy used i5/8GB (recommended) / VirtualBox
      4vCPU+8GB / affinity approximation. Decision: ______

## Group 1 — Reliability fixes that masquerade as slowness (§2) — ship first, zero perf risk

### 1.1 Keep-awake / sleep-reliability system (§2.1 — rebuilt 2026-07-16)

Rebuilt 2026-07-16 as a full app-wide system; the original sketch below (kept for its
`SetThreadExecutionState` reasoning) was backend-loop-only and had two real blind spots — see
the Current Status entry above for why. **This is NOT audio-recording-only:** it is Electron
(recording) + backend (all Whisper/llama processing), reference-counted, not a single boolean.

**Electron side — live recording (the backend cannot see this):**

- [x] `electron/main.js`: reference-counted `_recordingProtectionCount` +
      `_recordingPowerBlockerId`; `startRecordingProtection()` / `stopRecordingProtection()` /
      `forceStopRecordingProtection()` (hard reset used by every safety net)
- [x] `powerSaveBlocker.start('prevent-app-suspension')` only — never `'prevent-display-sleep'`
      (screen stays allowed to turn off) and never `ES_CONTINUOUS`-style persistence
- [x] IPC pair `recording-protection-start` / `recording-protection-stop` (`ipcMain.on`), exposed
      via `preload.js` contextBridge as `startRecordingProtection`/`stopRecordingProtection` only
      — no broader Electron capability exposed through this channel
- [x] Cleanup on **normal Stop Recording** and **exit-flush** — both call `mediaRecorder.stop()`,
      both land in the one `onstop` handler, which calls `stopRecordingProtection()` once
- [x] Cleanup on **MediaRecorder error** — new `onerror` handler (didn't exist before this work)
      stops protection and routes through the same `onstop` cleanup path
- [x] Cleanup on **recording-start failure** — `startRecordingProtection()` is only called AFTER
      `mediaRecorder.start()` succeeds, so a `getUserMedia`/`MediaRecorder` failure never starts
      protection in the first place — nothing to release
- [x] Cleanup on **renderer reload/crash** — `did-finish-load` and `render-process-gone` on
      `mainWindow.webContents` both call `forceStopRecordingProtection()` unconditionally (a
      no-op on the very first load, since the count is already 0)
- [x] Cleanup on **window close** — `mainWindow.on('closed', ...)` calls
      `forceStopRecordingProtection()`
- [x] Cleanup on **app quit** — folded into `killPythonBackend()`, which every quit path
      (`window-all-closed`, `will-quit`) already calls
- [x] Wired into both recording call sites: `SessionsPage.tsx` (counsellor sessions) and
      `MeetingDashboard.tsx` (executive meetings) — same pattern in both
- [x] `App.tsx` `electronAPI` TypeScript interface extended; `npx tsc --noEmit` clean
- [ ] **Runtime verify (Electron):** confirm via logging/Task Manager that the blocker id is
      actually held during a real recording and released within ~1s of each cleanup path above

**Backend side — all Whisper/llama processing:**

- [x] `backend/services/power.py`: `pulse_keep_awake(min_interval_s=30.0)` (throttled one-shot
      `SetThreadExecutionState(ES_SYSTEM_REQUIRED)`, thread-safe via a lock, best-effort — never
      raises, no-op on non-Windows) for loops that already iterate every few seconds
- [x] `backend/services/power.py`: `keep_awake_during()` context manager — a background daemon
      thread pulsing every 25s, for calls with **no** loop of their own (a whole non-streamed
      `_chat()`, or the silent prefill wait before the first streamed token in `_chat_stream()`,
      where a single top-of-function pulse would leave a multi-minute gap on a short sleep timer)
- [x] Call site: `transcribe.py` — `with TRANSCRIBE_LOCK, keep_awake_during():` wraps model load
      + the full `for seg in segments:` loop (inline single Transcribe, both workspaces)
- [x] Call site: `audio_queue.py` — per-item retained-queue endpoint's segment loop
      (`transcribe_queued_item_inline`)
- [x] Call site: `audio_queue.py` — BOTH bulk workers' segment loops (`_run_transcription_queue`
      counsellor, `_run_meetings_transcription_queue` meetings) — covers Bulk Transcribe and the
      transcribe stage of Bulk Transcribe & Beautify
- [x] Call site: `ai.py` `_chat()` — wraps the single `httpx.post` call; covers every non-streamed
      AI op: digest, take-away, template mapping, drawing observation, Visual Observation Record,
      image-work-brief, holistic summary
- [x] Call site: `ai.py` `_chat_stream()` — wraps the `httpx.stream(...)` connection AND the full
      `for line in response.iter_lines():` iteration (stays entered across `yield`s for a
      generator, so it covers a slow caller too); covers Beautify (single, and the Beautify stage
      of Transcribe & Beautify / Bulk Beautify / Bulk Transcribe & Beautify, all of which call
      `beautify_notes_stream` → `_chat_stream`) and meeting/clinical "Generate Summary"
      (`summarize_transcript_service` → `_chat`)
- [x] No changes needed in `sessions.py`'s beautify `gen()` or anywhere else that merely consumes
      `beautify_notes_stream`/`_chat`/`_chat_stream` — the two `ai.py` functions are the sole
      choke point for every AI call in the app (verified: `grep` for `_chat(`/`_chat_stream(`
      call sites returns only `services/ai.py` itself)
- [x] `py_compile` + `main.py` import clean (137 routes registered)
- [x] `backend/test_power.py` (15 tests: throttling, thread-safety under 30 concurrent callers,
      exception-safety on WinAPI failure, non-Windows no-op, `keep_awake_during` background-thread
      start/prompt-pulse/repeat-pulse/clean-stop-on-normal-exit/clean-stop-on-raised-exception/
      no-leftover-thread/repeated-cycle safety), registered in `run_security_tests.py` — full
      suite passes
- [ ] **Runtime verify (backend + Electron combined):** the original "14-point" list referenced
      below was written into a one-off coding-agent prompt that wasn't preserved anywhere in this
      repo — reconstructed here 2026-07-18 from Group 1.1's own unchecked boxes above so it isn't
      lost a second time. Set Windows sleep timer to 1–2 min (Settings → System → Power & sleep →
      both "On battery" and "Plugged in"). For each numbered item: start the action, do NOT touch
      mouse/keyboard, wait past the sleep timer plus a buffer, confirm the machine did NOT suspend
      and the job completed/behaved correctly. The display turning off during this is expected and
      fine — only system suspend is the failure condition.
      1. Live recording, counsellor workspace — hands off 3–5 min.
      2. Live recording, meetings workspace — same (confirms `MeetingDashboard.tsx` wiring too).
      3. Single Transcribe on a several-minute clip — hands off through the whole decode.
      4. Single Beautify on a long note — hands off through the silent prefill wait (up to ~298s
         ttft on a long session — the exact gap this item exists to cover).
      5. Transcribe & Beautify chain (All-at-Once) — hands off across both stages.
      6. Bulk Transcribe (2+ queued recordings) — hands off across the whole batch.
      7. Bulk Beautify (2+ drafts) — hands off across the whole batch.
      8. Bulk Transcribe & Beautify — both stages, hands off.
      9. Cancel path — start a transcribe or beautify, click Cancel, confirm the app returns to
         idle cleanly (protection releases — doesn't need to stay awake once cancelled).
      10. Forced error path — e.g. a beautify that fails (bad state / server hiccup) — confirm
          protection still releases on failure, not only on success.
      11. Window/app close mid-job — start a long job, close the app partway through; confirm the
          existing close-during-job handshake still behaves and nothing is left running orphaned.
      12. Overlapping activities — start recording on one client, then start a transcribe on
          another; confirm protection stays held until BOTH finish (reference-count check), not
          released early by whichever finishes first.
      13. **After every scenario above:** confirm the laptop resumes sleeping normally on its own
          timer a few minutes after the job/recording actually ends — this is the "never stuck
          awake" check and is arguably the most important single item here.
      14. Repeat at least the Beautify test (#4) on battery power — confirm identical behaviour.
      Record pass/fail per item here when run; do not consider Group 1.1 shippable until this
      passes end to end.
- [ ] Confirm behaviour on battery too (pulse/thread work identically; this is not the battery
      *chip* from §3.5, that's a separate, not-yet-built UI affordance) — folded into item 14 above

**Exceptions / not covered (documented, not silently dropped):**

- Bulk-worker **model load** (`get_whisper_model(...)` before the per-item loop in
  `_run_transcription_queue`/`_run_meetings_transcription_queue`) is not individually wrapped in
  `keep_awake_during()` — it's a single ~6–30s call immediately followed by the wrapped per-item
  loop, well inside even the aggressive 1–2 min test setting. `transcribe.py`'s inline endpoint
  DOES wrap model load (it's the only call in that request), so the two are intentionally
  asymmetric, not inconsistent.
- The `keep_awake_during()` cleanup path for a generator that's abandoned via a bare `return`
  inside its consuming `for` loop (rather than an explicit `.close()`) relies on CPython's
  reference-counting GC to close the generator promptly — this is standard CPython behaviour
  (not guaranteed on other interpreters, which this app does not run on) and matches the existing
  explicit `gen.close()` pattern already used in `audio_queue.py`'s `_finalize_group`.

### 1.2 llama-server pipe drain (§2.2) — DONE 2026-07-17, verified live

- [x] Add `_server_log_tail` ring buffer + `_drain_pipe()` to `ai.py`
- [x] Start both daemon drain threads immediately after `Popen` in `_ensure_server`
- [x] `_wait_for_server` early-death branch reads from `_server_log_tail` (NOT `.stderr.read()` —
      that would race the drain thread)
- [x] Log the server's memory-projection line once per spawn into `ai-server-start` detail (feeds
      0.4) — **this build prints no isolated "KV size" line; adapted to the real line it exposes**
      (`projected to use N MiB of host memory`), captured as `model_mem_projected_mib`
- [x] Verify: model switch still works cleanly with fresh drain threads per spawn — tested via the
      vision on/off switch path (same model, mmproj toggled — the "Better Quality" size-tier model
      isn't downloaded on this dev machine, but this exercises the identical terminate-and-respawn
      branch): old process terminated before the new `Popen`, new process got its own 2 drain
      threads, no hang across two consecutive switches, old process's drain threads exited cleanly
      on pipe close (only the current process's 2 threads remained afterward — no thread leak).
      Early-death path verified separately by pointing `_resolve_model_path` at a nonexistent file:
      the logged `error_message` now contains the actual llama.cpp root cause (e.g. `gguf_init_from_file:
      failed to open GGUF file '<user>\...\bogus.gguf' (No such file or directory)`) instead of the
      old generic exception text — confirmed a real `C:\Users\<name>\...` path gets scrubbed to
      `<user>` by `sanitize_error()`'s existing central scrub (privacy check passed).
      **One correction made mid-implementation:** `activity_log.sanitize_error()` collapses
      multi-line text to its LAST non-empty line (built for Python tracebacks, where that's the
      useful one) — llama-server's tail doesn't follow that shape; its last line is usually a
      generic "exiting due to model loading error" wrapper while the real cause sits a few lines
      earlier. Added `_format_tail_for_log()` which joins the last few ERROR-severity lines with
      `'; '` (no `\n`) so sanitize_error sees one logical line and the real content survives its
      collapse, while still passing through its path-scrub + 500-char bound unchanged.
- [x] **Soak verify:** 25 real completions (short, `max_tokens=8`) against ONE running server in a
      row — no hang, consistent 0.4–0.8s latency throughout (no growing backpressure), ring buffer
      correctly grew then capped at its 200-line maxlen. (Narrower than the original "20+ mixed
      beautify/digest/take-away" ask — those are multi-minute ops each on this hardware, so a full
      mixed-op soak wasn't run this session; the pipe-fill risk this item exists to catch scales
      with request/log-line COUNT, which this soak stresses directly. Revisit with a real mixed-op
      soak if time allows before calling the whole MakeItFast initiative shippable.)
- [x] `py_compile` clean; full backend import (137 routes) clean; `run_security_tests.py` full
      suite (incl. `test_power.py`) passes unchanged.

## Group 2 — Progress system (§3) — the "nothing shows" fix

### 2.1 Transcription progress bar (§3.1) — DISCOVERED ALREADY BUILT 2026-07-17

**This checklist was stale — the doc still showed every box unchecked, but a code audit on
2026-07-17 (prompted by the user asking "hasn't this been built already?") found the whole feature
genuinely implemented, just under different names than this doc sketched.** Correcting the record
rather than re-building:

- [x] Progress registry: `whisper_service.py` (`begin_progress`/`update_progress`/`get_progress`/
      `end_progress` — same shape as the sketched `report_progress`/`get_progress`, different names)
- [x] Hooked into `transcribe.py`'s segment loop and `audio_queue.py`'s per-item endpoint
- [x] `GET /api/transcribe/progress` endpoint exists — **but was missing its licence gate** (its
      sibling `/transcribe/cancel` calls `require_active_license`; this one didn't, and had no
      `category` param to even map a workspace). **Fixed 2026-07-17:** added `category: str =
      "meetings"` param + `require_active_license(ws)`, mirroring `/transcribe/cancel` exactly.
      `api.ts`'s `getTranscribeProgress` now takes a `category` param too; `MeetingDashboard.tsx`'s
      call site updated to pass `'meetings'` explicitly (previously relied on the endpoint having no
      gate at all, so it would have silently resolved to the wrong workspace — `SessionsPage.tsx`
      already matched the new default of `'sessions'` so needed no change). Verified live via
      `TestClient`: both workspaces return 200 with the expected zeroed payload for an unknown job,
      identical to pre-change behaviour, gate confirmed present without breaking normal dev use.
- [x] `api.ts`: `getTranscribeProgress()` + `TranscribeProgress` interface — built
- [x] `SessionsPage.tsx` + `MeetingDashboard.tsx`: real 1s poll (`startTranscribeProgressPoll`),
      `transcribeProgress` state, interval cleared in `finally` — built in BOTH workspaces (the
      original sketch only mentioned SessionsPage)
- [x] UI: real bar with `MM:SS / MM:SS` + `%` (`renderTranscribeProgressBar`, present in both pages)
      — the doc's "two static blocks" framing was stale; today there's one live single-item overlay
      per workspace plus the bulk queue row, not two static spinners
- [x] "Preparing the transcription engine…" cold-load copy — **was genuinely missing** (fell back to
      generic "Transcribing in progress…"/"Transcribing..." the whole time `pct` was null). **Added
      2026-07-17** in both `SessionsPage.tsx`'s editor-overlay and `MeetingDashboard.tsx`'s inline
      label: conditional on `transcribeProgress?.pct === null`.
- [x] Bar is monotonic/clamped (backend does `min(processed/duration, 1.0)`)
- [x] Progress only renders for the owning client/queue-item (`transcribingHere` /
      `transcribingQueueId === item.id`) — no cross-client bleed
- [x] `npx tsc --noEmit` clean (re-confirmed 2026-07-17 after the two fixes above)
- [ ] **Runtime verify:** real recording end-to-end on the actual desktop app — NOT done this
      session (this was a code audit + two targeted backend/frontend fixes, not a UI click-through).
      Still the one honest gap before calling 2.1 fully closed.

### 2.2 Bulk queue progress (§3.1 end) — DISCOVERED ALREADY BUILT 2026-07-17

- [x] Both workers (`audio_queue.py` counsellor + meetings) populate `current_processed_s`/
      `current_duration_s` in `_queue_state` (doc sketched `item_processed_s`/`item_total_s` —
      same idea, different field names)
- [x] Exposed via `/audio-queue/process-status`; `AudioQueueState` interface has the fields
- [ ] Confirm the background banner / Home window actually surfaces per-item % from these fields
      (not re-checked this session — the plumbing is confirmed, the exact UI presentation wasn't)
- [ ] **Runtime verify** with 2+ queued items, including a Cancel partway through — not done

### 2.3 Beautify staged progress (§3.2) — SINGLE-SESSION PATH DISCOVERED ALREADY BUILT 2026-07-17 (different design); BATCH QUEUE IS A REAL OPEN GAP

**Audited 2026-07-17 against real code, not this checklist.** The single-Beautify overlay solves
the exact problem this section describes, but via a different, better-reasoned design than the
plan below — correcting the record instead of re-building:

- [x] `ai.py`: `get_prefill_progress()` reading `/slots` — **built, but confirmed dead code**:
      `GET /api/ai/progress` exists in `sessions.py` and `api.getAiProgress()` exists in `api.ts`,
      but nothing in the frontend calls it. Superseded on purpose — see next line.
- [x] (Design change, not in the original plan) `SessionsPage.tsx:991-1080`: a simulated eased-curve
      "prep" bar (`startPrepProgress`/`computePrepPct`/`finishPrepProgress`) replaces real `/slots`
      polling. Comment at line 991-999 documents why: real prefill is often shorter than any safe
      polling interval, so the true percentage would randomly read 0%/100%/flip — "looked broken
      even when the model was working correctly." The simulated bar eases toward an 88% cap, labelled
      with a REAL per-device ETA (`api.getBeautifyEta()` → `get_beautify_eta()`, nearest-neighbour off
      this machine's own `beautify-single` history — the honest mechanism §3.4/2.5 wanted, just wired
      here instead), and snaps to 100%/"Writing your note…" the instant the real first token streams.
      Stage A (reading) and Stage B (reasoning) are intentionally merged into one "Understanding your
      session…" label rather than split — the doc's actual goal (kill the dead silent window) is met
      without the added complexity of a live reasoning-char SSE heartbeat.
- [ ] `ai.py` `_chat_stream` yielding structured `{kind:'thinking'|'token'}` events — **NOT built,
      and NOT needed** given the design above solves the same user-facing problem more robustly.
      Leave as plain token yield unless a future need for real reasoning-phase telemetry appears.
- [x] Overlay wired into the actual single-Beautify call sites (`beautifyNotes` handler,
      `SessionsPage.tsx:2973-3004`), not just sketched: `startPrepProgress` before the request,
      `finishPrepProgress` on `isFirstToken`, `stopPrepProgress` in cleanup.
- [x] **Batch beautify path — FIXED 2026-07-17.** Added `batchItemPct`/`batchItemEta` state +
      `startBatchItemProgress`/`finishBatchItemProgress`/`stopBatchItemProgress` reusing the same
      eased-curve math and real `getBeautifyEta()` per-device estimate as the single-item overlay,
      scoped to whichever queue item is currently running (loop is strictly sequential — safe).
      `handleBatchBeautify` now passes a real `onToken` callback (was `undefined` — batch items got
      zero token callback before this fix) that snaps to 100% on first token; progress resets in
      `finally` so it can't leak into the next item or a cancelled run. Queue row now shows a live
      `%` + thin bar + "usually ~Xs" ETA text instead of a bare spinning icon. `tsc --noEmit` clean.
- [x] Privacy: only char counts / ETAs ever cross to the frontend — reasoning text itself never
      does, in both the built dead-endpoint and the shipped simulated design.
- [x] `tsc` + `py_compile` clean (already-shipped code, not new work this session)
- [ ] **Runtime verify (single-Beautify path):** short note + long note; Stop mid-"Understanding"
      rolls back cleanly — not explicitly re-verified this session (code-read only), but this path
      is already live in production use, not new work.
- [ ] **Runtime verify (batch path) — moot until the batch gap above is actually fixed.**

### 2.4 The other silent spinners (§3.3) — AUDITED 2026-07-17: confirmed still NOT built, exactly as below

`MeetingDashboard.tsx:615-628`/`~1124-1133` confirmed still `await api.summarize(...)` with a static
"Generating locally..." spinner — no change since the original review. `runDigestGeneration`
(`SessionsPage.tsx:3641`, button `~6913-6961`) confirmed still shows only a Stop-button swap during
generation, no staged label. Now that 2.3's single-Beautify path is fixed, meetings-summary is the
worst remaining silent wait in the app — real gap, not yet started.

- [x] Meetings "Generate Summary" → SSE streaming — **FIXED 2026-07-17.**
      `POST /api/summarize/meeting/stream` (`system.py`) mirrors `/ai/beautify`'s SSE pattern exactly;
      `summarize_meeting_stream()` (ai.py) mirrors `beautify_notes_stream`; input sanitized before
      prompting (unchanged); output sanitizer re-applied to the FULLY accumulated text, sent as its
      own `{"final": ...}` event before `[DONE]` — streamed tokens are display-only preview.
- [x] `MeetingDashboard.tsx` consumes the stream via `api.summarizeMeetingStream()` (replaces the old
      static "Generating locally..." with a "Reading your notes…"/"Writing…" staged button label +
      an eased-curve overlay over the summary textarea, fading out on first real token)
- [x] **Live-verified against the real backend** (not just code-read): `TestClient` call actually
      spawned the real bundled `llama-server.exe`, streamed ~115 real token events for a real
      meeting-mode prompt, emitted a real sanitized `final` event, then `[DONE]`; 3 real
      `activity_log` rows confirmed under `summarize-meeting`/`meetings` with full non-PHI detail
      (ttft_ms 18–28s, chars, cold_start, token counts, reasoning_chars) — same shape as beautify's.
- [ ] **Runtime verify in the actual desktop UI** (Electron/React, not TestClient) — not done this
      session; the backend-live + `tsc`-clean checks above are strong but aren't the same as
      watching it in the real app window.
- [ ] Reporting summary + take-away get at least the staged label via `/api/ai/progress`
      (full streaming optional/later) — **not touched this session, still open**

### 2.5 Honest estimates + trust chips (§3.4 / §3.5) — CLOSED OUT 2026-07-17 (2 items parked by explicit user call, not oversights)

The plan below sketched a frontend `private_perf_profile` EMA. What's actually shipped is a backend
history-lookup pattern instead (`get_beautify_eta`/`get_visual_observation_eta` in
`activity_log.py` — nearest-neighbour off real completed-op rows, already used twice, proven
reusable shape), which is arguably more honest than a client-side EMA since it's real measured rows,
not a decaying average. It already powers the single-Beautify overlay (see 2.3).

- [ ] Transcribe JSON response + a final beautify SSE `stats` event — not re-checked this session
- [x] Frontend perf profile — **shipped as backend history lookups instead of a client EMA; same
      goal, different (arguably better) mechanism.** Don't build the EMA version too — redundant.
- [x] **Batch modal estimate — FIXED 2026-07-17.** New `batchEtaTotal` state (`SessionsPage.tsx`) +
      a `useEffect` that calls `api.getBeautifyEta()` once per selected note and sums the low/high
      ranges (notes in a batch are rarely the same length, so per-note summing beats one global
      number); replaces the old fixed "~45-minute session takes 10–15 minutes" copy entirely, with
      an honest "no estimate yet… gets smarter after a few notes" fallback when there's no history.
      New `formatEtaSeconds()` helper next to `secsToMMSS`.
- [x] Single transcribe/beautify ETAs read a real profile — done (`getBeautifyEta`, per 2.3)
- [x] **Soft "estimate, not live" disclaimer — DONE, new item added beyond the original plan,** at
      user's request. Same finalized sentence (user-edited wording) in all three longer-form spots
      (single-Beautify overlay, batch modal banner, meetings overlay); short form "(estimated, not
      live)" in the space-constrained batch queue row.
- [x] Battery chip: **built, then explicitly reverted at user's request — PARKED, not abandoned.**
      A working version existed this session (`GET /api/system/power-status` reusing
      `activity_log.on_ac_power()`, `api.getPowerStatus()`, an amber chip in the single-Beautify
      overlay) and was fully removed on request — zero leftover references (repo-wide grep
      confirmed), `tsc`/`py_compile` clean after the revert. If revisited, this session's design is
      the known-working shape.
- [x] Settings: "Higher Accuracy" real-multiplier copy — **PARKED by explicit user judgment call,
      not built.** Reasoning: users already intuitively know the heavier/slower model is
      heavier/slower; the real-measured-multiplier copy is a precision nice-to-have, not a "feels
      frozen" fix, and not worth the new backend aggregation work (a `whisper_model`-keyed
      multiplier lookup mirroring `get_beautify_eta`'s shape) right now.
- [ ] **Runtime verify:** estimates within ~±30% of actual — not re-verified (existing shipped code);
      real desktop-UI click-through for the batch-ETA fix and disclaimer wording also still pending
      (user will do UI testing later, per this session's own note on 2.3/2.4).

**2.5 status: done for practical purposes.** The two open boxes above are parked by deliberate
choice, not gaps that were missed — don't re-open them without a new reason.

## Group 3 — Instrumentation for the tuning phases (§6) — land BEFORE Group 4 benchmarks

- [x] Capture llama `timings` into `capture_stats` → Beautify row detail. **Done
      2026-07-29:** total/evaluated/cached prompt tokens, prompt ms/rate,
      completion/decode counts/ms/rate, exact visible TTFT, reasoning onset,
      total duration, cold/warm state, finish/truncation, and review slugs;
      nested server usage is numeric-allowlisted
- [x] Bulk Beautify keeps the aggregate count row and records one
      `beautify-batch-item` row per model request, including success/failure/
      cancellation; focused privacy tests prove Source, names, generated text,
      reasoning text, and arbitrary template keys cannot enter detail
- [ ] After `_wait_for_server` succeeds: `GET /props`, log resolved `n_threads`/`n_ctx` into the
      `ai-server-start` row (answers "what does `-t -1` resolve to" on every machine forever)
- [ ] `app-start` row gains `ram_gb` (GlobalMemoryStatusEx) + `os.cpu_count()` + bounded
      `PROCESSOR_IDENTIFIER`
- [ ] `beautify-single` row gains `on_ac_power` (the one remaining `[~]` from CS Phase 1)
- [ ] PHI re-check on every new field; confirm they appear in the CSV/JSON diagnostic export
- [ ] (Optional) `scripts/perf_report.py` — reads a diagnostic JSON export, prints median/p90 per
      action by model/threads/power, so test rounds stop needing hand math

## Group 4 — Engine tuning (§4) — every item benchmark-gated, one lever at a time

### 4.1 Whisper threads **(= CS Phase 5, whisper half — tick the detail THERE)**

- [ ] Harness run on Vivobook: 4 (real baseline) / 6 / 8 / physical / logical, multi-pass,
      hash-verified output equality
- [ ] Same harness run on the weak-tier rig from 0.5
- [ ] Adopt new default (adaptive shape per §4.1, clamp values from the benchmark); mirror `[x]` here
      when CS Phase 5 records the decision

### 4.2 KV cache + context right-sizing (§4.2)

- [ ] Ground truth from 0.4 recorded
- [x] Flash attention was isolated from Q8 KV. The Group 4.3 / BH 5.7g
      `-fa auto` versus forced `-fa on` A/B completed at F16 KV; forced `on`
      was rejected and production remains `auto`
- [ ] Record memory ground truth and close the shared factual/provenance
      quality defects before choosing the next bounded engine test. If Q8 KV
      is later authorised, A/B `-ctk q8_0 -ctv q8_0` separately; KV quant is
      quality-adjacent and requires explicit blind review
- [ ] `_pick_ctx_size()` RAM-aware 16k/32k + early friendly 400 in the beautify router when
      `len(notes)//4 + budget` exceeds the loaded context
- [ ] Verify a 47-min-class session still Beautifies at 16k (max observed prompt was 14k)
- [ ] Settings warns when selecting Better Quality (E4B) on a <10GB-RAM machine
- [ ] **Weak-tier verify:** llama-server working set fits in RAM on the 8GB rig — no pagefile
      thrash during Beautify (Task Manager / perfmon while it runs)

### 4.3 llama thread/prefill flags **(= CS Phase 5, llama half — tick the detail THERE)**

- [~] Benchmark `-t` (physical, physical−1) / `-tb` (logical) /
      `-ub` (512/1024/2048) / `-fa` one at a time, using Group 3's
      `timings` capture as the measure. **Three rejected conditions:**
      `-t 9`/`-tb 16` was `+65%` TTFT / `+64%` duration and was reverted to
      `-1`/`-1`; explicit `-ub 512` versus `2048` then completed four fixtures
      × three cold repetitions per condition. `2048` median aggregate prefill
      was only `-4.309s`, visible `+25.062s`, and total `+6.251s`, with TE POU
      placement and critical Psychiatric attribution/risk regressions. Reject
      it and keep implicit `512`. The 24-call `-fa auto` versus forced `on`
      matrix then found forced `on` slower on three of four fixture medians,
      unstable across paired repetitions, and nowhere near the minute-scale
      target. Blind outputs were byte-identical but shared material quality
      defects. **Reject forced `on`; keep `auto`.** One narrower thread value
      (`10`/`10`) remains untried, but factual/provenance quality and memory
      ground truth come before another engine candidate.
- [ ] Adopt winners; hardware + values recorded in CS-CHECKLIST; mirror `[x]` here — no winner yet,
      only a rejected value so far.
- [ ] Re-run one real paired session (Phase 3 style) and confirm the wall-clock win shows up

### 4.4 Reasoning phase **(= CS Phase 4 — tick the detail THERE)**

- [~] A/B `--reasoning off` (and `--reasoning-budget 512` middle ground) across ALL op types —
      but judge the SMALL ops (digest / take-away / template mapping) separately from Beautify:
      cut there first if Beautify quality suffers (per 0.3's answer on per-request control) —
      **Beautify only tested 2026-07-04, then corrected same day:** full `off` is ≈2.4× faster; the
      first read of the exported note looked like a fabricated second client, but that was a false
      alarm — the test recording was a real couples-therapy session (Sarah/James) run under an
      unrelated demo client profile ("Moon"), so the "off" names were actually correct. Re-read: the
      `auto` note was the one with the bigger fidelity problem (collapsed both real people into a
      single person). Net: `off` was not lower quality on this sample, but the test is confounded by
      the mismatched demo name — full write-up in CS-CHECKLIST Session 7 (+ correction addendum).
      **Clean staged Beautify retest added 2026-07-29:** `auto/3072` versus
      `1024` used byte-frozen short PRIVATE and long TE POU fixtures, cold/warm
      separated, two pairs per condition, and blind quality review. 1024
      aggregate visible TTFT was `+0.014%` and total duration `+5.121%`;
      reject it. Per the gate, `512` and `off` were not extended from this
      failed candidate. Digest/take-away/template mapping/vision remain
      untested.
- [~] Explicit written go/no-go per op class — **Beautify: an initial NO-GO for full `off` was
      recorded 2026-07-04, then RETRACTED the same day** once the quality-regression finding turned
      out to be a false alarm. **Current split ruling:** full `off` remains
      historically inconclusive; **1024 is now an evidence-based NO-GO for
      Beautify** because it failed speed/stability despite non-inferior quality.
      `LLAMA_REASONING` stays `auto` and the production budget stays `3072`.
      Other op classes: no decision yet, not tested.
- [ ] If adopted: shrink `reasoning_est` in the token-budget formula + delete the stale
      "generous because reasoning" comments — N/A while the decision is NO-GO.

### 4.5 Prompt-cache reuse **(= CS Phase 7 — tick the detail THERE)**

- [~] Confirm `-np` resolves to ONE slot on our spawn; add `--cache-reuse 256`; measure
      re-Beautify / template-map-after-Beautify / cross-session cases; output
      byte-identical check. **Partial 2026-07-29:** spawn already has `-np 1`,
      `--cache-prompt`, and `--cache-reuse 256`; immediate identical Beautify
      repeats evaluated five of 4,334/8,387 tokens (`99.88–99.94%` reuse) and
      reduced prompt evaluation to `0.11–0.166s`. Long final outputs were
      byte-identical across reasoning budgets at the same cache state. Cross-
      session/source-prefix pre-warm and its lifecycle/thermal cost remain
      open but **secondary**: the normal counsellor path is one Beautify, so
      first-run end-to-end improvement governs adoption

### 4.6 Whisper micro-levers (§4.6)

- [ ] Settings option "Spoken language: English (NZ) / Auto-detect" → passes `language="en"`
      (default stays Auto; document why in Settings copy)
- [ ] Harness test `condition_on_previous_text=False` (quality + repetition-loop check on
      silence-heavy counselling-style audio) — adopt only on a clear win
- [ ] "Fast draft" beam-1 profile **(= CS Phase 9)** — explicit user choice only, never a default

### 4.7 faster-whisper 1.2.1 + BatchedInferencePipeline **(= CS Phase 6 — tick the detail THERE)**

- [ ] Mirror `[x]` here when the upgrade + batched go/no-go is recorded in CS-CHECKLIST

### 4.8 Whisper model lineup experiment (§4.7)

- [ ] Evaluate `small` and `distil-medium.en`-class as an ADDITIVE middle option
      ("Higher Accuracy (Fast)") — never rename/remove existing entries
- [ ] NZ-accent + te reo Māori A/B on your own recordings BEFORE offering (distil is English-only)
- [ ] Go/no-go written down

### 4.9 Warm-ups (§4.8) **(supersedes CS Phase 2's scope — small + targeted)**

- [ ] Whisper warm-load on record-start (background, skips if TRANSCRIBE_LOCK busy)
- [ ] llama warm-start on transcribe-completion in counsellor workspace — RAM-aware (skip on
      low-RAM machines via the §4.2 helper)
- [ ] Guardrail: never triggers during first-launch setup / licence entry / startup cover screen
      (CS Phase 2's guard list applies)
- [ ] Verify no repeat of the 1.0.3 licence-flash regression class (startup smoke)

## Group 5 — Workflow shape (§5)

### 5.1 Small glue (§5.2)

- [ ] Opt-in "Transcribe automatically when recording stops" checkbox (default OFF)
- [ ] Opt-in "Beautify automatically when this transcription finishes" **(= CS Phase 10 bullet 1)**
      — snapshot session/template at start; respects workspace lock; default OFF
- [ ] Chain bulk-transcribe completion → Beautify-All picker pre-population (ticks only, never
      auto-run) **(= CS Phase 10)**
- [ ] Revisit `BATCH_MAX = 4` AFTER 2.5's honest estimates exist **(= CS Phase 10)**
- [ ] **Runtime verify the walk-away promise end-to-end:** queue 3–4 recordings + auto-chain ON +
      lid untouched for the whole run (Group 1.1 keeps it awake) → return to finished notes

### 5.2 Live transcription while recording (§5.1) — the headline; do AFTER Groups 1–4

- [ ] **Spike:** AudioWorklet 16 kHz mono PCM tap alongside the existing MediaRecorder; RMS
      quiet-point slicing (~60s, ≥400ms quiet, 1s overlap); dump slices to scratch and verify
      gapless coverage vs the full recording
- [ ] Backend `POST /api/transcribe/live-chunk` + `/live-finalize` (in-memory only, under
      TRANSCRIBE_LOCK, `initial_prompt` = tail of accumulated text, dedicated LOW thread count e.g. 2)
- [ ] Stitch QA: same audio through live-slices vs classic single-pass — diff and judge acceptability
- [ ] Guardrails: pause on battery; ANY slice failure → silent fallback to classic path (never an
      error mid-session); Settings toggle "Transcribe while recording", default OFF at first release
- [ ] Fan/CPU acceptability test during a real quiet-room session (the counselling-room constraint)
- [ ] Verify the durable path is untouched: full recording still lands in `audio_queue` at stop
      exactly as today, and classic re-transcription of it still works
- [ ] (Optional) collapsed "live transcript preview" in the Audio tab
- [ ] Weak-tier verify: live decode keeps up with real time (RTF < 1.0) at the low thread count on
      the 0.5 rig

### 5.3 GPU / Vulkan spike (§4.9) — LAST, optional, contained

- [ ] Spike only after Groups 1–5.1 land: Vulkan llama-server variant behind
      "Use graphics acceleration (experimental)" with automatic health-check fallback to CPU build
- [ ] Go/no-go on ≥2 different iGPU machines before it ever defaults on

## Group 6 — Weak-tier validation (§7)

- [ ] Rig from 0.5 exists and boots the packaged app
- [ ] Repeat on it: 1.2 soak, 2.1 progress UX feel, 4.1/4.3 benchmark runs, 4.2 paging check
- [ ] Record the tier's real before/after numbers into CS-CHECKLIST Phase 3/8 tables
- [ ] Update all user-facing estimate fallbacks with the measured weak-tier reality

## Group 7 — Reality check + ship gates

- [ ] Re-measure 2–3 real paired sessions with everything adopted **(= CS Phase 8)** — write the
      honest achieved numbers next to §9's projection table above (mid tier AND weak tier)
- [ ] Decide: keep tuning, or declare the CPU ceiling reached and lean on §3/§5 UX (write it down)
- [ ] `npm run check:config` · `npx tsc --noEmit` · backend security suite · `npm run build:clinical`
- [ ] Installed clinical build smoke test (startup/auto-login especially — warm-up code touches it)
- [ ] Any dependency/binary change went exact-pin + SHA256; version bumped so updates actually ship
- [ ] Confirm nothing weakened local-token / workspace-lock / licence-gate behaviour


## WHAT WAS CONFIRMED AS SUMMARY:

Everything checks out: TypeScript clean, Electron files syntax-valid, full backend test suite (including the new power suite)
  passing. Let's mark the final task complete and clean up the task list.

● Summary

  I inspected every long-running code path first, then implemented keep-awake as a full app-wide system across two coordinated
  mechanisms, and updated the plan doc to correct its old backend-loop-only framing.

  Every protected workflow: live recording (counsellor + meetings), single Transcribe, single Beautify, Transcribe & Beautify,
  Bulk Transcribe, Bulk Beautify, Bulk Transcribe & Beautify (both stages), meeting transcription, meeting/clinical "Generate
  Summary", reporting summaries, take-aways, template mapping, drawing observation, and the Visual Observation Record.

  Central integration points (2 mechanisms, 8 total call sites):
  - Electron (electron/main.js, preload.js): reference-counted powerSaveBlocker('prevent-app-suspension'), narrow
  startRecordingProtection/stopRecordingProtection IPC pair, wired into SessionsPage.tsx and MeetingDashboard.tsx.
  - Backend (backend/services/power.py): pulse_keep_awake() for loops that already iterate (4 Whisper segment-decode sites:
  transcribe.py, audio_queue.py×3), and a new keep_awake_during() background-thread pulse wrapped around ai.py's
  _chat()/_chat_stream() — the sole choke point every AI call in the app routes through, so 2 call sites cover all AI workflows
  with zero duplication. This closes a real blind spot in the original MakeItFast.md sketch: a single pulse before a
  multi-minute blocking call (llama prefill can take up to ~298s with zero SSE lines) wouldn't survive an aggressive sleep
  timer.

  Cleanup paths covered: normal stop, cancel/discard, MediaRecorder error (new onerror handler — didn't exist before),
  recording-start failure (protection only starts after .start() succeeds), renderer reload/crash
  (did-finish-load/render-process-gone force-reset), window close, app quit (folded into killPythonBackend()), and every
  AI/exception path (finally-based, best-effort, never raises).

  Files changed: backend/services/power.py (new), backend/test_power.py (new, 15 tests), backend/run_security_tests.py,
  backend/services/ai.py, backend/routers/transcribe.py, backend/routers/audio_queue.py, electron/main.js, electron/preload.js,
  src/App.tsx, src/pages/SessionsPage.tsx, src/pages/MeetingDashboard.tsx, .claude/plan/MakeItFast.md.

  Tests performed: test_power.py (throttling, 30-thread concurrency, exception-safety, non-Windows no-op, background-thread
  lifecycle) — 15/15 pass; full run_security_tests.py suite — all pass; npx tsc --noEmit — clean; backend/main.py import (137
  routes) — clean; node --check on both Electron files — clean.

  Not covered (documented in the plan, not silently dropped): the 14-point manual runtime validation (real Windows sleep-timer
  test, hands-off for 5+ minutes per workflow, on real hardware) has not been run — that requires a human to physically alter
  system sleep settings and observe real suspend behavior, which isn't something I can safely or reliably do from inside this
  session. MakeItFast.md explicitly flags this as the remaining gate before the initiative can be called shippable.
