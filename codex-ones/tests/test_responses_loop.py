from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from codex_ones.responses_loop import ToolLoopLimitError, run_responses_tool_loop


class FakeResponses:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(output=next(self.outputs), output_text="finished")


class ResponsesLoopTests(unittest.TestCase):
    def test_dispatches_tool_and_returns_final_response(self) -> None:
        call = SimpleNamespace(
            type="function_call",
            name="lookup",
            arguments=json.dumps({"period": "2026-S1"}),
            call_id="call-1",
        )
        message = SimpleNamespace(type="message")
        responses = FakeResponses([[call], [message]])
        client = SimpleNamespace(responses=responses)

        final = run_responses_tool_loop(
            client,
            model="test-model",
            instructions="Use the tool.",
            user_input="Give me the count.",
            tools=[{"type": "function", "name": "lookup"}],
            handlers={"lookup": lambda args: {"period": args["period"], "count": 13}},
        )

        self.assertEqual(final.output_text, "finished")
        second_input = responses.requests[1]["input"]
        tool_outputs = [item for item in second_input if isinstance(item, dict)]
        self.assertEqual(tool_outputs[-1]["call_id"], "call-1")
        self.assertIn('"count": 13', tool_outputs[-1]["output"])

    def test_turn_limit_is_bounded(self) -> None:
        call = SimpleNamespace(
            type="function_call", name="lookup", arguments="{}", call_id="call-1"
        )
        responses = FakeResponses([[call]])
        client = SimpleNamespace(responses=responses)
        with self.assertRaises(ToolLoopLimitError):
            run_responses_tool_loop(
                client,
                model="test-model",
                instructions="Use the tool.",
                user_input="Loop.",
                tools=[],
                handlers={"lookup": lambda _args: {}},
                max_turns=1,
            )


if __name__ == "__main__":
    unittest.main()

