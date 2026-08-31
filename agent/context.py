from __future__ import annotations

from dataclasses import dataclass, field


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
    messages: list[dict[str, str]] = field(default_factory=list)

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

    def add_assistant(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def add_observation(self, content: str) -> None:
        self.messages.append({"role": "user", "content": f"Observation:\n{content}"})

