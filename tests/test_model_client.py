from __future__ import annotations

import pytest

from agent.model_client import ModelClient, ModelClientError, ToolCall


class FakeTransport:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[dict] = []

    def __call__(self, url: str, payload: dict, headers: dict[str, str], timeout_seconds: int) -> dict:
        self.calls.append(
            {
                "url": url,
                "payload": payload,
                "headers": headers,
                "timeout_seconds": timeout_seconds,
            }
        )
        return self.response


def make_response(message: dict, finish_reason: str = "stop") -> dict:
    return {"choices": [{"message": message, "finish_reason": finish_reason}]}


def test_model_client_posts_messages_and_tools_to_api() -> None:
    transport = FakeTransport(make_response({"content": "done"}))
    client = ModelClient(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        transport=transport,
    )
    tools = [{"type": "function", "function": {"name": "echo"}}]

    reply = client.chat([{"role": "user", "content": "hello"}], tools=tools)

    call = transport.calls[0]
    assert call["url"] == "https://api.deepseek.com/chat/completions"
    assert call["headers"]["Authorization"] == "Bearer test-key"
    assert call["payload"]["model"] == "deepseek-chat"
    assert call["payload"]["messages"] == [{"role": "user", "content": "hello"}]
    assert call["payload"]["tools"] == tools
    assert call["payload"]["tool_choice"] == "auto"
    assert reply.content == "done"
    assert reply.tool_calls == []


def test_model_client_omits_tools_when_none() -> None:
    transport = FakeTransport(make_response({"content": "done"}))
    client = ModelClient(api_key="test-key", model="deepseek-chat", transport=transport)

    client.chat([{"role": "user", "content": "hello"}])

    payload = transport.calls[0]["payload"]
    assert "tools" not in payload
    assert "tool_choice" not in payload


def test_model_client_parses_tool_calls() -> None:
    transport = FakeTransport(
        make_response(
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "function": {
                            "name": "read_file",
                            "arguments": '{"path":"README.md"}',
                        },
                    }
                ],
            },
            finish_reason="tool_calls",
        )
    )
    client = ModelClient(api_key="test-key", model="deepseek-chat", transport=transport)

    reply = client.chat([{"role": "user", "content": "read"}], tools=[])

    assert reply.content == ""
    assert reply.finish_reason == "tool_calls"
    assert reply.tool_calls == [
        ToolCall(
            id="call_1",
            name="read_file",
            arguments='{"path":"README.md"}',
        )
    ]


def test_model_client_requires_api_key() -> None:
    with pytest.raises(ModelClientError, match="DEEPSEEK_API_KEY"):
        ModelClient(api_key="", transport=FakeTransport({}))


def test_model_client_rejects_malformed_response() -> None:
    client = ModelClient(api_key="test-key", transport=FakeTransport({"choices": []}))

    with pytest.raises(ModelClientError, match="missing choices"):
        client.chat([{"role": "user", "content": "hello"}])
