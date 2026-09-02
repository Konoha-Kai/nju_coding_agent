from agent.context_compressor import ContextCompressor


def test_compressor_keeps_short_context_unchanged() -> None:
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "task"},
        {"role": "assistant", "content": "done"},
    ]
    compressor = ContextCompressor(max_messages=10)

    result = compressor.compress(messages)

    assert result.compressed is False
    assert result.messages == messages


def test_compressor_preserves_system_summary_and_recent_messages() -> None:
    messages = [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "create fib.py"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "arguments": '{"path":"fib.py","content":"..."}',
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "ok=True\nWrote 20 characters to fib.py"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": "run_command",
                        "arguments": '{"command":"python fib.py"}',
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_2", "content": "ok=True\nexit_code=0\n88"},
        {"role": "assistant", "content": "sum is 88"},
    ]
    compressor = ContextCompressor(max_messages=5, keep_recent_messages=1)

    result = compressor.compress(messages)

    assert result.compressed is True
    assert result.original_count == 7
    assert len(result.messages) == 3
    assert result.messages[0] == {"role": "system", "content": "system prompt"}
    assert result.messages[1]["role"] == "system"
    assert "Structured context summary" in result.messages[1]["content"]
    assert "Original user task: create fib.py" in result.messages[1]["content"]
    assert "Tool calls: write_file, run_command" in result.messages[1]["content"]
    assert "Changed files: fib.py" in result.messages[1]["content"]
    assert "Commands run: python fib.py" in result.messages[1]["content"]
    assert result.messages[-1:] == messages[-1:]


def test_compressor_summarizes_errors_and_truncates_long_tool_output() -> None:
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "run tests"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "run_command",
                        "arguments": '{"command":"pytest"}',
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "ok=False\n" + ("x" * 400)},
        {"role": "assistant", "content": "tests failed"},
    ]
    compressor = ContextCompressor(max_messages=4, keep_recent_messages=1, max_summary_chars=260)

    result = compressor.compress(messages)

    summary = result.messages[1]["content"]
    assert "Errors: ok=False" in summary
    assert len(summary) <= 280
    assert "...[summary truncated]" in summary


def test_compressor_does_not_split_assistant_tool_call_from_tool_result() -> None:
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "task"},
        {"role": "assistant", "content": "planning"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "arguments": '{"path":"a.py"}',
                    },
                },
                {
                    "id": "call_2",
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "arguments": '{"path":"b.py"}',
                    },
                },
            ],
        },
        {"role": "tool", "tool_call_id": "call_1", "content": "ok=True\na"},
        {"role": "tool", "tool_call_id": "call_2", "content": "ok=True\nb"},
    ]
    compressor = ContextCompressor(max_messages=4, keep_recent_messages=2)

    result = compressor.compress(messages)

    assert result.compressed is True
    assert result.messages[-3]["role"] == "assistant"
    assert len(result.messages[-3]["tool_calls"]) == 2
    assert result.messages[-2]["role"] == "tool"
    assert result.messages[-1]["role"] == "tool"
