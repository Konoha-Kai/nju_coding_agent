from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ModelReply:
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    finish_reason: str | None = None


class ModelClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        openai_client: Any | None = None,
    ) -> None:
        load_dotenv()
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.client = openai_client or OpenAI(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url=base_url
            or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ModelReply:
        request: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        if tools is not None:
            request["tools"] = tools
            request["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**request)
        choice = response.choices[0]
        message = choice.message
        return ModelReply(
            content=message.content or "",
            tool_calls=self._parse_tool_calls(getattr(message, "tool_calls", None)),
            finish_reason=choice.finish_reason,
        )

    def _parse_tool_calls(self, raw_tool_calls: Any | None) -> list[ToolCall]:
        if not raw_tool_calls:
            return []

        calls = []
        for raw in raw_tool_calls:
            function = raw.function
            calls.append(
                ToolCall(
                    id=str(raw.id),
                    name=str(function.name),
                    arguments=str(function.arguments or "{}"),
                )
            )
        return calls
