from dataclasses import dataclass
from pathlib import Path
import shutil
import uuid

from agent.context import ConversationContext
from agent.loop import Agent
from agent.model_client import ModelReply, ToolCall
from agent.tooling import ToolRegistry, ToolResult, ToolSpec


@dataclass
class FakeModelClient:
    replies: list[str]
    calls: list[dict] = None

    def __post_init__(self) -> None:
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append({"messages": [dict(message) for message in messages], "tools": tools})
        reply = self.replies.pop(0)
        if isinstance(reply, ModelReply):
            return reply
        return ModelReply(content=reply)


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_agent_runs_actions_until_final() -> None:
    workspace = make_workspace()
    model = FakeModelClient(
        [
            '{"action":"write_file","path":"result.txt","content":"ok"}',
            '{"action":"final","message":"task complete"}',
        ]
    )
    agent = Agent(model_client=model, workspace=workspace, max_steps=3)

    try:
        result = agent.run("create result")

        assert result.success
        assert result.final_message == "task complete"
        assert (workspace / "result.txt").read_text(encoding="utf-8") == "ok"
        assert result.steps == 2
    finally:
        remove_workspace(workspace)


def make_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo",
            description="Echo text.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=lambda args: ToolResult(True, args["text"]),
        )
    )
    return registry


def test_agent_passes_tool_schemas_to_model() -> None:
    workspace = make_workspace()
    model = FakeModelClient(['{"action":"final","message":"done"}'])
    agent = Agent(
        model_client=model,
        workspace=workspace,
        tool_registry=make_registry(),
        max_steps=1,
    )

    try:
        agent.run("use tools")
    finally:
        remove_workspace(workspace)

    assert model.calls[0]["tools"][0]["function"]["name"] == "echo"


def test_agent_executes_tool_calls_and_returns_final_message() -> None:
    workspace = make_workspace()
    model = FakeModelClient(
        [
            ModelReply(
                content="",
                tool_calls=[
                    ToolCall(id="call_1", name="echo", arguments='{"text":"hello"}')
                ],
                finish_reason="tool_calls",
            ),
            ModelReply(content="done", finish_reason="stop"),
        ]
    )
    agent = Agent(
        model_client=model,
        workspace=workspace,
        tool_registry=make_registry(),
        max_steps=3,
    )

    try:
        result = agent.run("echo hello")
    finally:
        remove_workspace(workspace)

    assert result.success
    assert result.final_message == "done"
    assert result.observations == ["Tool echo ok=True\nhello"]
    assert model.calls[1]["messages"][-1] == {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": "ok=True\nhello",
    }


def test_agent_reports_invalid_tool_arguments_to_model() -> None:
    workspace = make_workspace()
    model = FakeModelClient(
        [
            ModelReply(
                content="",
                tool_calls=[ToolCall(id="call_1", name="echo", arguments="{bad json")],
                finish_reason="tool_calls",
            ),
            ModelReply(content="failed cleanly", finish_reason="stop"),
        ]
    )
    agent = Agent(
        model_client=model,
        workspace=workspace,
        tool_registry=make_registry(),
        max_steps=3,
    )

    try:
        result = agent.run("bad args")
    finally:
        remove_workspace(workspace)

    assert result.success
    assert "Invalid tool arguments" in result.observations[0]
    assert model.calls[1]["messages"][-1]["role"] == "tool"


def test_context_adds_assistant_tool_calls_and_tool_results() -> None:
    context = ConversationContext.start("task")
    call = ToolCall(id="call_1", name="echo", arguments='{"text":"hello"}')

    context.add_assistant("need tool", tool_calls=[call])
    context.add_tool_result("call_1", ToolResult(True, "hello"))

    assert context.messages[-2]["tool_calls"] == [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": "echo", "arguments": '{"text":"hello"}'},
        }
    ]
    assert context.messages[-1] == {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": "ok=True\nhello",
    }
