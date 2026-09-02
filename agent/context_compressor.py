from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompressionResult:
    messages: list[dict[str, Any]]
    compressed: bool
    original_count: int
    compressed_count: int
    summary: str = ""


class ContextCompressor:
    def __init__(
        self,
        max_messages: int = 14,
        keep_recent_messages: int = 6,
        max_summary_chars: int = 1800,
    ) -> None:
        if max_messages < 3:
            raise ValueError("max_messages must be at least 3")
        if keep_recent_messages < 1:
            raise ValueError("keep_recent_messages must be at least 1")
        self.max_messages = max_messages
        self.keep_recent_messages = keep_recent_messages
        self.max_summary_chars = max_summary_chars

    def compress(self, messages: list[dict[str, Any]]) -> CompressionResult:
        if len(messages) <= self.max_messages:
            return CompressionResult(
                messages=list(messages),
                compressed=False,
                original_count=len(messages),
                compressed_count=len(messages),
            )

        system_message = messages[0]
        recent_start = self._recent_start_index(messages)
        recent_messages = messages[recent_start:]
        summarized_messages = messages[1:recent_start]
        summary = self._build_summary(summarized_messages)
        compressed_messages = [
            dict(system_message),
            {"role": "system", "content": summary},
            *[dict(message) for message in recent_messages],
        ]
        return CompressionResult(
            messages=compressed_messages,
            compressed=True,
            original_count=len(messages),
            compressed_count=len(compressed_messages),
            summary=summary,
        )

    def _recent_start_index(self, messages: list[dict[str, Any]]) -> int:
        recent_count = min(self.keep_recent_messages, max(len(messages) - 1, 1))
        start = len(messages) - recent_count

        while start > 1 and messages[start].get("role") == "tool":
            start -= 1
        if start > 1 and _assistant_has_tool_calls(messages[start]):
            return start

        return start

    def _build_summary(self, messages: list[dict[str, Any]]) -> str:
        user_tasks: list[str] = []
        tool_calls: list[str] = []
        changed_files: list[str] = []
        commands: list[str] = []
        errors: list[str] = []
        tool_results: list[str] = []

        for message in messages:
            role = str(message.get("role", ""))
            content = str(message.get("content") or "")
            if role == "user" and content and not content.startswith("Observation:"):
                user_tasks.append(_one_line(content))
            if role == "assistant":
                for call in message.get("tool_calls") or []:
                    function = call.get("function") or {}
                    name = str(function.get("name") or "")
                    arguments = _parse_arguments(function.get("arguments"))
                    if name:
                        tool_calls.append(name)
                    if name == "write_file" and "path" in arguments:
                        changed_files.append(str(arguments["path"]))
                    if name == "run_command" and "command" in arguments:
                        commands.append(str(arguments["command"]))
            if role == "tool":
                tool_results.append(_one_line(content))
                if "ok=False" in content:
                    errors.append(_one_line(content))

        lines = [
            "Structured context summary:",
            f"Original user task: {_last_or_none(user_tasks)}",
            f"Tool calls: {_unique_join(tool_calls)}",
            f"Changed files: {_unique_join(changed_files)}",
            f"Commands run: {_unique_join(commands)}",
            f"Errors: {_unique_join(errors)}",
            f"Recent tool results: {_join_limited(tool_results, limit=4)}",
            "Instruction: use this summary as compressed history, then continue from the recent raw messages.",
        ]
        return _truncate("\n".join(lines), self.max_summary_chars)


def _parse_arguments(raw_arguments: Any) -> dict[str, Any]:
    if not isinstance(raw_arguments, str):
        return {}
    try:
        parsed = json.loads(raw_arguments or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _assistant_has_tool_calls(message: dict[str, Any]) -> bool:
    return message.get("role") == "assistant" and bool(message.get("tool_calls"))


def _one_line(content: str, max_chars: int = 180) -> str:
    collapsed = " ".join(content.split())
    return _truncate(collapsed, max_chars)


def _truncate(content: str, max_chars: int) -> str:
    if len(content) <= max_chars:
        return content
    suffix = "...[summary truncated]"
    keep = max(max_chars - len(suffix), 0)
    return content[:keep] + suffix


def _last_or_none(values: list[str]) -> str:
    return values[-1] if values else "(none)"


def _unique_join(values: list[str]) -> str:
    unique = list(dict.fromkeys(value for value in values if value))
    return ", ".join(unique) if unique else "(none)"


def _join_limited(values: list[str], limit: int) -> str:
    clipped = [value for value in values if value][:limit]
    return " | ".join(clipped) if clipped else "(none)"
