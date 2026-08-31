from pathlib import Path

from main import build_session_logger, parse_args


def test_parse_args_accepts_logging_options() -> None:
    args = parse_args(
        [
            "--workspace",
            "demo",
            "--max-steps",
            "5",
            "--log-dir",
            "logs",
            "--session-id",
            "abc",
            "do task",
        ]
    )

    assert args.workspace == "demo"
    assert args.max_steps == 5
    assert args.log_dir == "logs"
    assert args.session_id == "abc"
    assert args.task == "do task"


def test_build_session_logger_uses_workspace_relative_log_dir() -> None:
    logger = build_session_logger(
        workspace=Path("project"),
        log_dir="logs",
        session_id="session-1",
    )

    assert logger.session_id == "session-1"
    assert logger.log_path == Path("project") / "logs" / "session-1.jsonl"

