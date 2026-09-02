from pathlib import Path

from main import build_chat_task, format_verbose_event, parse_args, run_chat_session


def test_parse_args_accepts_logging_options() -> None:
    args = parse_args(
        [
            "--workspace",
            "demo",
            "--max-steps",
            "5",
            "--max-errors",
            "2",
            "--log-dir",
            "logs",
            "--session-id",
            "abc",
            "--verbose",
            "--chat",
            "--compress-context",
            "--context-max-messages",
            "9",
            "--context-keep-recent",
            "4",
            "do task",
        ]
    )

    assert args.workspace == "demo"
    assert args.max_steps == 5
    assert args.max_errors == 2
    assert args.log_dir == "logs"
    assert args.session_id == "abc"
    assert args.verbose is True
    assert args.chat is True
    assert args.compress_context is True
    assert args.context_max_messages == 9
    assert args.context_keep_recent == 4
    assert args.task == "do task"


def test_build_session_logger_uses_workspace_relative_log_dir() -> None:
    from main import build_session_logger

    logger = build_session_logger(
        workspace=Path("project"),
        log_dir="logs",
        session_id="session-1",
    )

    assert logger.session_id == "session-1"
    assert logger.log_path == Path("project") / "logs" / "session-1.jsonl"


def test_format_verbose_event_for_tool_call() -> None:
    line = format_verbose_event(
        "tool_call",
        {"step": 2, "name": "read_file", "arguments": '{"path":"README.md"}'},
    )

    assert line == '[step 2] tool read_file {"path":"README.md"}'


def test_format_verbose_event_for_tool_result_truncates_output() -> None:
    line = format_verbose_event(
        "tool_result",
        {"step": 2, "name": "read_file", "ok": True, "content": "x" * 120},
    )

    assert line.startswith("[step 2] tool read_file ok=True ")
    assert line.endswith("...")
    assert len(line) < 120


def test_format_verbose_event_for_context_compression() -> None:
    line = format_verbose_event(
        "context_compressed",
        {"step": 3, "original_count": 12, "compressed_count": 6},
    )

    assert line == "[step 3] context compressed 12 -> 6 messages"


def test_build_chat_task_includes_previous_turns() -> None:
    task = build_chat_task(
        history=[("first question", "first answer")],
        user_message="second question",
    )

    assert "Conversation so far" in task
    assert "User: first question" in task
    assert "Agent: first answer" in task
    assert "Latest user request:\nsecond question" in task


def test_build_chat_task_returns_first_message_without_history() -> None:
    assert build_chat_task([], "hello") == "hello"


def test_run_chat_session_keeps_turn_history_and_stops_on_exit() -> None:
    class FakeResult:
        def __init__(self, final_message: str) -> None:
            self.final_message = final_message

    class FakeAgent:
        def __init__(self) -> None:
            self.tasks: list[str] = []

        def run(self, task: str) -> FakeResult:
            self.tasks.append(task)
            return FakeResult(f"answer {len(self.tasks)}")

    agent = FakeAgent()
    inputs = iter(["hello", "what did I ask?", "exit"])
    outputs: list[str] = []

    code = run_chat_session(
        agent=agent,
        input_func=lambda prompt: next(inputs),
        output_func=outputs.append,
    )

    assert code == 0
    assert agent.tasks[0] == "hello"
    assert "User: hello" in agent.tasks[1]
    assert "Agent: answer 1" in agent.tasks[1]
    assert "Latest user request:\nwhat did I ask?" in agent.tasks[1]
    assert outputs == [
        "Interactive chat mode. Type exit or quit to stop.",
        "Agent: answer 1",
        "Agent: answer 2",
        "Bye.",
    ]
