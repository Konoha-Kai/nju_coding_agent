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
    parser.add_argument("--max-errors", type=int, default=3, help="Maximum consecutive tool errors")
    parser.add_argument("--log-dir", default="logs", help="Directory for JSONL session logs")
    parser.add_argument("--session-id", help="Stable session id for log filename")
    parser.add_argument("--verbose", action="store_true", help="Print agent loop events while running")
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


def format_verbose_event(event: str, data: dict) -> str:
    step = data.get("step")
    prefix = f"[step {step}] " if step is not None else ""
    if event == "user_task":
        return "[task] started"
    if event == "model_reply":
        calls = data.get("tool_calls") or []
        if calls:
            names = ", ".join(str(call.get("name", "")) for call in calls)
            return f"{prefix}model requested {names}"
        return f"{prefix}model final reply"
    if event == "tool_call":
        return f"{prefix}tool {data.get('name')} {data.get('arguments', '{}')}"
    if event == "tool_result":
        content = str(data.get("content", "")).replace("\n", " ")
        if len(content) > 64:
            content = content[:61] + "..."
        return f"{prefix}tool {data.get('name')} ok={data.get('ok')} {content}"
    if event == "agent_finish":
        return f"[final] success steps={data.get('steps')}"
    if event == "agent_error":
        return f"[error] {data.get('final_message', '')}"
    return f"{prefix}{event}"


def print_verbose_event(event: str, data: dict) -> None:
    print(format_verbose_event(event, data), flush=True)


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
        event_handler=print_verbose_event if args.verbose else None,
        max_steps=args.max_steps,
        max_errors=args.max_errors,
    )
    result = agent.run(task)
    print(result.final_message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
