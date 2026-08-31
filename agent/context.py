from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent.model_client import ToolCall
    from agent.tooling import ToolResult


SYSTEM_PROMPT = """You are a minimal coding agent.
You can inspect and change the local workspace only by replying with one JSON object.

Allowed JSON actions:
{"action":"list_files","path":".","recursive":false}
{"action":"read_file","path":"relative/path.py","max_chars":12000}
{"action":"write_file","path":"relative/path.py","content":"file content"}
{"action":"run_command","command":"python script.py","timeout_seconds":30}
{"action":"final","message":"summary for the user"}

Rules:
- Reply with JSON only. Do not use markdown.
- Use one action per reply.
- After an observation, decide the next action.
- Use final only when the task is complete or cannot proceed.
"""

TOOL_CALLING_SYSTEM_PROMPT = """You are a coding agent running inside a local harness.
Use the provided tools to inspect files, edit files, run commands, and verify work.

Rules:
- Prefer reading relevant files before editing.
- Use tools whenever local workspace state is needed.
- After command failures, inspect the error and continue fixing.
- When the task is complete, respond with a concise final summary.
- Mention changed files, commands run, and validation results when available.
"""


@dataclass
class ConversationContext:
    messages: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def start(cls, task: str, use_tool_calls: bool = False) -> "ConversationContext":
        context = cls()
        context.add_system(TOOL_CALLING_SYSTEM_PROMPT if use_tool_calls else SYSTEM_PROMPT)
        context.add_user(task)
        return context

    def add_system(self, content: str) -> None:
        self.messages.append({"role": "system", "content": content})

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(
        self,
        content: str,
        tool_calls: list["ToolCall"] | None = None,
    ) -> None:
        message: dict[str, Any] = {"role": "assistant", "content": content}
        if tool_calls:
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in tool_calls
            ]
        self.messages.append(message)

    def add_observation(self, content: str) -> None:
        self.messages.append({"role": "user", "content": f"Observation:\n{content}"})

    def add_tool_result(self, tool_call_id: str, result: "ToolResult") -> None:
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": f"ok={result.ok}\n{result.content}",
            }
        )
