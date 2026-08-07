"""
LESSON 4 — Supervisor + parallel cheap workers + synthesis.

This is the pattern that actually scales to real workloads ("summarize these 50
documents", "review these 30 files", "research these 8 competitors") and the one
that controls cost while doing it. It's ALSO, not coincidentally, the exact pattern
used earlier in this session: an expensive model (design + interpret) dispatching a
cheap model (execute the mechanical part) so the expensive model's time isn't spent
babysitting something that doesn't need it.

The shape:
    1. SUPERVISOR (strong model) looks at the overall task and breaks it into
       independent, self-contained pieces.
    2. WORKERS (cheap, fast model) each handle exactly one piece, IN PARALLEL —
       real concurrency, not just a for-loop that happens to call the API
       multiple times.
    3. SUPERVISOR (strong model again) reads all the worker outputs and produces
       the final, synthesized result.

Why parallel, and why cheap workers specifically:
    - Each worker's job is narrow and mechanical (extract, classify, summarize
      ONE document) — it doesn't need the most capable model, just a competent one.
    - Running them concurrently means wall-clock time is ~1 worker-call, not
      N worker-calls stacked serially.
    - The supervisor's expensive tokens are spent ONLY on the two things that
      actually need judgment: deciding how to split the work, and combining the
      results into something coherent. That's the entire cost-engineering pitch
      you can make to a client: "we don't run your most expensive model on
      mechanical work."

Run:
    python 04_supervisor_parallel_workers.py
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic

client = anthropic.Anthropic()

# A stand-in for "50 documents" — short fake customer feedback snippets.
# In a real engagement these would be loaded from files, a database, a CRM export.
FEEDBACK_ITEMS = [
    "The new dashboard is so much faster, but I can't find the export button anymore.",
    "Billing charged me twice this month, please fix.",
    "Support was amazing, resolved my issue in 10 minutes.",
    "The mobile app crashes every time I try to upload a photo.",
    "I love the new dark mode! Only feature request: bigger font option.",
]


# ---------------------------------------------------------------------------
# STEP 1: The supervisor decomposes the task.
#
# For a task this uniform (classify each item the same way), decomposition is
# almost mechanical — one worker call per item. For a genuinely uneven task
# ("research these 3 competitors, but competitor B needs way more digging"),
# you'd have the supervisor MODEL do this split, not hardcode it. Both are
# legitimate; hardcode the split when the pieces are naturally uniform, ask
# the model to split when the right division of labor isn't obvious upfront.
# ---------------------------------------------------------------------------


def classify_one_item(item: str) -> dict:
    """One worker's entire job: classify one piece of feedback. Nothing else."""
    response = client.messages.create(
        # Cheap and fast — this task does not need deep reasoning, just
        # competent classification. This is the single most important line
        # in this file from a cost-engineering standpoint.
        model="claude-haiku-4-5",
        max_tokens=256,
        system=(
            "Classify one piece of customer feedback. Respond with ONLY a "
            "JSON object: {\"sentiment\": \"positive\"|\"negative\"|\"mixed\", "
            "\"category\": \"bug\"|\"billing\"|\"feature_request\"|\"praise\", "
            "\"one_line_summary\": \"...\"}"
        ),
        messages=[{"role": "user", "content": item}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # A worker's job failing shouldn't crash the whole batch — record the
        # failure and let the supervisor decide what to do with a partial set.
        parsed = {"sentiment": "unknown", "category": "unknown", "error": text}
    parsed["source_text"] = item
    return parsed


# ---------------------------------------------------------------------------
# STEP 2: Run the workers CONCURRENTLY.
#
# ThreadPoolExecutor is enough here — each worker call is I/O-bound (waiting
# on the network), so real Python threads give real concurrency without
# needing asyncio. For hundreds/thousands of items, or if you're already in
# an async codebase, swap this for asyncio + an async client; the SHAPE of
# the pattern (dispatch all, gather all, then synthesize) is identical either way.
# ---------------------------------------------------------------------------


def run_workers_in_parallel(items: list[str], max_workers: int = 5) -> list[dict]:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(classify_one_item, item): item for item in items}
        for future in as_completed(futures):
            results.append(future.result())
    return results


# ---------------------------------------------------------------------------
# STEP 3: The supervisor synthesizes the worker outputs into one deliverable.
# This is the call worth spending real capability on — turning 50 scattered
# classifications into a coherent, prioritized brief is a judgment task.
# ---------------------------------------------------------------------------


def synthesize(worker_results: list[dict]) -> str:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        system=(
            "You are a customer insights analyst. You'll be given a list of "
            "pre-classified customer feedback items. Write a short brief for "
            "a product manager: the 1-2 most urgent issues (prioritize bugs "
            "and billing problems over feature requests), overall sentiment, "
            "and anything worth celebrating."
        ),
        messages=[
            {
                "role": "user",
                "content": json.dumps(worker_results, indent=2),
            }
        ],
    )
    return next(b.text for b in response.content if b.type == "text")


def main() -> None:
    print(f"Dispatching {len(FEEDBACK_ITEMS)} items to parallel workers...")
    results = run_workers_in_parallel(FEEDBACK_ITEMS)

    print("\n--- worker results ---")
    for r in results:
        print(r)

    print("\n--- supervisor synthesis (this is the deliverable) ---")
    brief = synthesize(results)
    print(brief)


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# HOW THIS SCALES BEYOND THE TOY EXAMPLE
#
# - Swap FEEDBACK_ITEMS for a real data source (files on disk, rows from a
#   database query, results of a search). Nothing else in the shape changes.
# - `max_workers` is a real lever: too high and you'll hit rate limits (the
#   SDK retries 429s automatically, but you'll still see it slow down); too
#   low and you're not getting the parallelism benefit. Tune it against your
#   actual rate-limit tier.
# - If one worker's job is genuinely harder than the others (a longer, messier
#   document vs. a one-line comment), consider a size/complexity-based router:
#   have the supervisor (or even a cheap pre-check) decide which items need
#   the stronger model per-item, instead of one fixed model for every worker.
# - This is exactly the shape of a recurring client deliverable: point 04 at
#   a folder of documents on a schedule (see Lesson 5 for the "hosted and
#   scheduled" version of this idea) and you have an automated weekly report.
# ---------------------------------------------------------------------------
