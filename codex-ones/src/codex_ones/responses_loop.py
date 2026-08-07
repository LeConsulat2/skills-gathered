"""A transparent Responses API function-calling loop."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any

ToolHandler = Callable[[dict[str, Any]], Any]


class ToolLoopLimitError(RuntimeError):
    pass


class ToolDispatchError(RuntimeError):
    pass


def run_responses_tool_loop(
    client: Any,
    *,
    model: str,
    instructions: str,
    user_input: str,
    tools: Sequence[Mapping[str, Any]],
    handlers: Mapping[str, ToolHandler],
    max_turns: int = 6,
    max_tool_calls: int = 8,
) -> Any:
    """Run a bounded loop and return the final SDK response object."""

    if max_turns < 1 or max_tool_calls < 1:
        raise ValueError("max_turns and max_tool_calls must be positive")

    input_items: list[Any] = [{"role": "user", "content": user_input}]
    tool_call_count = 0

    for _turn in range(max_turns):
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=input_items,
            tools=list(tools),
        )
        input_items.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response

        for call in calls:
            tool_call_count += 1
            if tool_call_count > max_tool_calls:
                raise ToolLoopLimitError(f"Tool call limit exceeded ({max_tool_calls})")
            handler = handlers.get(call.name)
            if handler is None:
                raise ToolDispatchError(f"Model requested an unregistered tool: {call.name}")
            try:
                arguments = json.loads(call.arguments)
            except json.JSONDecodeError as exc:
                raise ToolDispatchError("Tool arguments were not valid JSON") from exc
            if not isinstance(arguments, dict):
                raise ToolDispatchError("Tool arguments must be a JSON object")

            try:
                result = handler(arguments)
                output = {"ok": True, "result": result}
            except ValueError as exc:
                output = {
                    "ok": False,
                    "error": {"code": "invalid_arguments", "message": str(exc)},
                }
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(output, sort_keys=True),
                }
            )

    raise ToolLoopLimitError(f"Model did not finish within {max_turns} turns")

