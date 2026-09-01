from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from dotenv import load_dotenv


Transport = Callable[[str, dict[str, Any], dict[str, str], int], dict[str, Any]]


class ModelClientError(RuntimeError):
    pass


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
        transport: Transport | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        load_dotenv()
        self.api_key = api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            raise ModelClientError("DEEPSEEK_API_KEY is not set")
        self.base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")).rstrip("/")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.transport = transport or _post_json
        self.timeout_seconds = timeout_seconds

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] = "auto",
    ) -> ModelReply:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        if tools is not None:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        response = self.transport(
            f"{self.base_url}/chat/completions",
            payload,
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            self.timeout_seconds,
        )
        return self._parse_response(response)

    def _parse_response(self, response: dict[str, Any]) -> ModelReply:
        choices = response.get("choices")
        if not choices:
            raise ModelClientError("model response missing choices")
        choice = choices[0]
        message = choice.get("message") or {}
        return ModelReply(
            content=message.get("content") or "",
            tool_calls=self._parse_tool_calls(message.get("tool_calls")),
            finish_reason=choice.get("finish_reason"),
        )

    def _parse_tool_calls(self, raw_tool_calls: Any | None) -> list[ToolCall]:
        if not raw_tool_calls:
            return []

        calls = []
        for raw in raw_tool_calls:
            function = raw.get("function") or {}
            calls.append(
                ToolCall(
                    id=str(raw.get("id", "")),
                    name=str(function.get("name", "")),
                    arguments=str(function.get("arguments") or "{}"),
                )
            )
        return calls


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout_seconds: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ModelClientError(f"model API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ModelClientError(f"model API request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ModelClientError(f"model API returned invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ModelClientError("model API returned non-object JSON")
    return parsed
