from __future__ import annotations

import argparse
from pathlib import Path

from agent import Agent
from agent.model_client import ModelClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal NJU coding agent harness")
    parser.add_argument("task", nargs="?", help="Programming task for the agent")
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--max-steps", type=int, default=12, help="Maximum agent loop steps")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task = args.task or input("Task: ").strip()
    if not task:
        print("No task provided.")
        return 1

    agent = Agent(
        model_client=ModelClient(),
        workspace=Path(args.workspace),
        max_steps=args.max_steps,
    )
    result = agent.run(task)
    print(result.final_message)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())

