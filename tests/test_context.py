from agent.context import ConversationContext


def test_context_starts_with_system_and_user_messages() -> None:
    context = ConversationContext.start("fix the bug")

    assert context.messages[0]["role"] == "system"
    assert context.messages[1] == {"role": "user", "content": "fix the bug"}


def test_context_can_start_in_tool_call_mode() -> None:
    context = ConversationContext.start("fix the bug", use_tool_calls=True)

    assert context.messages[0]["role"] == "system"
    assert "Use the provided tools" in context.messages[0]["content"]
    assert "Reply with JSON only" not in context.messages[0]["content"]


def test_context_adds_observation_as_user_feedback() -> None:
    context = ConversationContext.start("task")
    context.add_observation("exit_code=0")

    assert context.messages[-1]["role"] == "user"
    assert "Observation:" in context.messages[-1]["content"]
    assert "exit_code=0" in context.messages[-1]["content"]
