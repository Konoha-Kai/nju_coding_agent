from pathlib import Path

from main import build_session_logger, format_verbose_event, parse_args


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
            "do task",
        ]
    )

    assert args.workspace == "demo"
    assert args.max_steps == 5
    assert args.max_errors == 2
    assert args.log_dir == "logs"
    assert args.session_id == "abc"
    assert args.verbose is True
    assert args.task == "do task"


def test_build_session_logger_uses_workspace_relative_log_dir() -> None:
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
