from __future__ import annotations

import argparse
from pathlib import Path
from uuid import uuid4

from agent import Agent
from agent.bootstrap import build_default_registry
from agent.logger import SessionLogger
from agent.model_client import ModelClient


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal NJU coding agent harness")
    parser.add_argument("task", nargs="?", help="Programming task for the agent")
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--max-steps", type=int, default=12, help="Maximum agent loop steps")
    parser.add_argument("--log-dir", default="logs", help="Directory for JSONL session logs")
    parser.add_argument("--session-id", help="Stable session id for log filename")
    return parser.parse_args(argv)


def build_session_logger(
    workspace: Path,
    log_dir: str = "logs",
    session_id: str | None = None,
) -> SessionLogger:
    resolved_session_id = session_id or uuid4().hex
    return SessionLogger(
        log_path=workspace / log_dir / f"{resolved_session_id}.jsonl",
        session_id=resolved_session_id,
    )


def main() -> int:
    args = parse_args()
    task = args.task or input("Task: ").strip()
    if not task:
        print("No task provided.")
        return 1

    workspace = Path(args.workspace)
    agent = Agent(
        model_client=ModelClient(),
        workspace=workspace,
        tool_registry=build_default_registry(workspace),
        logger=build_session_logger(workspace, args.log_dir, args.session_id),
        max_steps=args.max_steps,
    )
    result = agent.run(task)
    print(result.final_message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
