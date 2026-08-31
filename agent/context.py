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


@dataclass
class ConversationContext:
    messages: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def start(cls, task: str) -> "ConversationContext":
        context = cls()
        context.add_system(SYSTEM_PROMPT)
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
