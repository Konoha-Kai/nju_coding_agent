from types import SimpleNamespace

from agent.model_client import ModelClient, ToolCall


class FakeCompletions:
    def __init__(self, response) -> None:
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeOpenAIClient:
    def __init__(self, response) -> None:
        self.chat = SimpleNamespace(
            completions=FakeCompletions(response),
        )


def make_response(message, finish_reason="stop"):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=message,
                finish_reason=finish_reason,
            )
        ]
    )


def test_model_client_passes_messages_and_tools_to_api() -> None:
    message = SimpleNamespace(content="done", tool_calls=None)
    fake_client = FakeOpenAIClient(make_response(message))
    client = ModelClient(openai_client=fake_client, model="deepseek-chat")
    tools = [{"type": "function", "function": {"name": "echo"}}]

    reply = client.chat([{"role": "user", "content": "hello"}], tools=tools)

    call = fake_client.chat.completions.calls[0]
    assert call["model"] == "deepseek-chat"
    assert call["messages"] == [{"role": "user", "content": "hello"}]
    assert call["tools"] == tools
    assert call["tool_choice"] == "auto"
    assert reply.content == "done"
    assert reply.tool_calls == []


def test_model_client_omits_tools_when_none() -> None:
    message = SimpleNamespace(content="done", tool_calls=None)
    fake_client = FakeOpenAIClient(make_response(message))
    client = ModelClient(openai_client=fake_client, model="deepseek-chat")

    client.chat([{"role": "user", "content": "hello"}])

    call = fake_client.chat.completions.calls[0]
    assert "tools" not in call
    assert "tool_choice" not in call


def test_model_client_parses_tool_calls() -> None:
    raw_tool_call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(
            name="read_file",
            arguments='{"path":"README.md"}',
        ),
    )
    message = SimpleNamespace(content=None, tool_calls=[raw_tool_call])
    fake_client = FakeOpenAIClient(make_response(message, finish_reason="tool_calls"))
    client = ModelClient(openai_client=fake_client, model="deepseek-chat")

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

