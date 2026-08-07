"""
LESSON 1 — The minimum viable agent.

A "prompt" is one request: you send text, you get text back, nothing else happens.
An "agent" is a prompt PLUS the ability to call tools (functions you write) and
re-prompt itself with the results, until the task is actually done. That's the
entire definition. Everything fancier in this folder is this idea, scaled up.

This script gives Claude one real tool — the ability to list files in a directory
and read one — and asks it a question it can only answer by using that tool. Watch
the console output: Claude will call list_directory, look at the result, then decide
to call read_file, then answer. You didn't write that decision-making — the model
did. That's the difference between an agent and a script that just calls an API.

We use the "Tool Runner" here, which is the Anthropic Python SDK's helper that
handles the request -> check-for-tool-call -> execute -> feed-back -> repeat loop
FOR you. Lesson 2 rebuilds this exact same agent by hand so you can see what the
Tool Runner is doing under the hood — read that one right after this one.

Run:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...        (or: ant auth login)
    python 01_single_tool_agent.py
"""

import os

import anthropic
from anthropic import beta_tool

# ---------------------------------------------------------------------------
# STEP 1: Define the tool(s) the agent is allowed to use.
#
# The @beta_tool decorator turns an ordinary Python function into something the
# model can call. The SDK reads the type hints and the docstring to build the
# JSON schema Claude actually sees — you never hand-write that schema here.
#
# This is the single most important design decision in any agent: what tools
# does it have, and how well is each one described? A vague description means
# the model guesses wrong about when to use it. Be specific, and say what the
# tool does NOT do too, if that matters.
# ---------------------------------------------------------------------------


@beta_tool
def list_directory(path: str) -> str:
    """List the files and subdirectories directly inside a directory.

    Args:
        path: A directory path, relative to where this script is run from.
    """
    try:
        entries = os.listdir(path)
    except OSError as exc:
        # Tools fail sometimes. Return the error as TEXT, not a raised exception —
        # a raised exception crashes your script; returned error text lets the
        # model see what went wrong and decide what to do next (try a different
        # path, tell the user, etc.). This is "is_error" behavior baked in simply
        # by what string you return.
        return f"Error listing '{path}': {exc}"
    return "\n".join(entries) if entries else "(empty directory)"


@beta_tool
def read_file(path: str, max_chars: int = 4000) -> str:
    """Read the contents of a text file, truncated to max_chars.

    Args:
        path: Path to the file to read.
        max_chars: Maximum number of characters to return, to avoid flooding
            the model's context with a huge file.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
    except OSError as exc:
        return f"Error reading '{path}': {exc}"
    return content


# ---------------------------------------------------------------------------
# STEP 2: Give the agent a job and let the Tool Runner drive the loop.
# ---------------------------------------------------------------------------


def main() -> None:
    client = anthropic.Anthropic()

    # The Tool Runner takes the same parameters as a normal request, plus a
    # `tools` list of your decorated functions. Everything else — deciding to
    # call a tool, running it, sending the result back, deciding to call
    # another tool or finally answer — happens inside `runner`.
    runner = client.beta.messages.tool_runner(
        model="claude-opus-5",
        max_tokens=2048,
        tools=[list_directory, read_file],
        messages=[
            {
                "role": "user",
                "content": (
                    "Look at the current directory. If there's a README or "
                    "START-HERE style file, read it and give me a two-sentence "
                    "summary of what this folder is for."
                ),
            }
        ],
    )

    # Each iteration of this loop is one full turn of the conversation — a
    # point where Claude either called a tool (and the runner already handled
    # it) or produced a final answer. We just print what happened as we go.
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print("[claude]", block.text)
            elif block.type == "tool_use":
                print(f"[tool call] {block.name}({block.input})")

    print("\n--- done ---")


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------
# WHAT TO NOTICE
#
# 1. You never wrote an if/else that says "if the user asks about files, call
#    list_directory". The MODEL decided that, based on the tool descriptions
#    and the task. That's the whole value proposition of an agent over a
#    hand-coded script: it generalizes to requests you didn't anticipate.
#
# 2. This is also the risk. A tool that can delete files, send emails, or
#    spend money needs to be gated (see LESSON 3's note on human-in-the-loop,
#    and 06-consulting-playbook.md's security checklist) — because the model
#    deciding when to call it is exactly what makes it powerful AND exactly
#    what makes an ungated version dangerous.
#
# 3. Try changing the user message to something that needs BOTH tools in
#    sequence (list a directory, then read a specific file it found) — you'll
#    see two tool-call iterations before the final text answer.
# ---------------------------------------------------------------------------
