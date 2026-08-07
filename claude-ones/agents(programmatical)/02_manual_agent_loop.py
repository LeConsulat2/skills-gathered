"""
LESSON 2 — The same agent as Lesson 1, but the loop is written by hand.

Lesson 1 used the Tool Runner, which hides the mechanism. This file exposes it,
because the mechanism itself is what's PORTABLE. Every agent framework, every
provider's SDK (OpenAI, Anthropic, open-source ones you build for a client on
their own infra), and every from-scratch agent you'll ever build is a variation
on this exact loop:

    1. Send the conversation so far, plus the list of tools available, to the model.
    2. Look at what the model did:
       - If it just wrote text and stopped -> you're done, return the answer.
       - If it asked to call a tool -> run that tool yourself, in your own code.
    3. Append the tool's result to the conversation as if it were a message.
    4. Go back to step 1. Repeat until step 2 says "done".

That's it. That's the whole idea behind "agent" as a software pattern, independent
of Anthropic, OpenAI, or any framework. The exact field names below (`tool_use`,
`stop_reason`, `tool_result`) are Anthropic's wire format — a different provider's
SDK will use different field names for the identical four steps. If you're ever
handed "build us an agent" on a stack that isn't Claude, THIS is the shape you
re-implement; only the JSON keys change.

Run:
    python 02_manual_agent_loop.py
"""

import os

import anthropic

client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# STEP 1: Tool definitions, this time as raw JSON schema (no decorator magic).
# This is closer to what actually gets sent over the wire to the model.
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "list_directory",
        "description": "List the files and subdirectories directly inside a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "A directory path, relative to the working directory.",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a text file, truncated to max_chars.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read."},
                "max_chars": {
                    "type": "integer",
                    "description": "Maximum characters to return.",
                    "default": 4000,
                },
            },
            "required": ["path"],
        },
    },
]


def execute_tool(name: str, tool_input: dict) -> str:
    """This is YOUR code running YOUR logic. The model never runs this —
    it only ever asks you to. That boundary is the entire security model:
    nothing the model wants to do happens unless this function lets it."""
    if name == "list_directory":
        try:
            entries = os.listdir(tool_input["path"])
        except OSError as exc:
            return f"Error: {exc}"
        return "\n".join(entries) if entries else "(empty directory)"

    if name == "read_file":
        try:
            with open(tool_input["path"], "r", encoding="utf-8", errors="replace") as f:
                return f.read(tool_input.get("max_chars", 4000))
        except OSError as exc:
            return f"Error: {exc}"

    return f"Unknown tool: {name}"


# ---------------------------------------------------------------------------
# STEP 2: The loop itself.
# ---------------------------------------------------------------------------


def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-opus-5",
            max_tokens=2048,
            tools=TOOLS,
            messages=messages,
        )

        # Print anything the model said out loud this turn (its "thinking out
        # loud" text, separate from tool calls) so you can watch it work.
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print("[claude]", block.text)

        # --- The decision point. Everything hinges on stop_reason. ---
        if response.stop_reason != "tool_use":
            # The model produced a final answer with no further tool calls.
            final_text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return final_text

        # The model wants to call one or more tools. Always append its FULL
        # response (including the tool_use blocks) before continuing — the
        # API needs that exact content back on the next turn, or it 400s.
        messages.append({"role": "assistant", "content": response.content})

        # A single turn can request MULTIPLE tool calls at once (parallel tool
        # use). Run every one of them and send ALL results back together in a
        # single user message — never split them across separate messages.
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        tool_results = []
        for block in tool_use_blocks:
            print(f"[tool call] {block.name}({block.input})")
            result_text = execute_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # ties this result to that specific call
                    "content": result_text,
                }
            )

        messages.append({"role": "user", "content": tool_results})
        # Loop back to step 1 with the growing conversation history.


if __name__ == "__main__":
    answer = run_agent(
        "Look at the current directory. If there's a README or START-HERE "
        "style file, read it and give me a two-sentence summary of what "
        "this folder is for."
    )
    print("\n--- final answer ---")
    print(answer)

# ---------------------------------------------------------------------------
# WHY YOU'D EVER WRITE THIS INSTEAD OF USING THE TOOL RUNNER
#
# In practice: rarely, for exactly this task. But you now understand every
# piece a higher-level framework will ever build on top of this, which means:
#   - You can debug it when the framework's abstraction leaks.
#   - You can add things the framework doesn't support yet (a custom retry
#     policy, a non-standard transport, a weird approval workflow).
#   - You can port the SAME MENTAL MODEL to a provider whose SDK doesn't have
#     a Tool Runner at all — you just write this loop against their API.
# ---------------------------------------------------------------------------
