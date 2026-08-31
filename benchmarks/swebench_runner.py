from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from agent import Agent
from agent.bootstrap import build_default_registry
from agent.logger import SessionLogger
from agent.model_client import ModelClient
from benchmarks.swebench_adapter import (
    SwebenchInstance,
    build_agent_task,
    create_prediction_record,
    extract_git_diff,
    write_predictions_jsonl,
)


class AgentLike(Protocol):
    def run(self, task: str) -> Any:
        ...


@dataclass(frozen=True)
class SwebenchRunResult:
    instance_id: str
    success: bool
    run_id: str
    model_name: str
    model_patch: str
    prediction_path: Path | None
    report_path: Path
    changed_files: list[str]
    executed_commands: list[str]
    failure_reason: str | None = None


def load_instance_file(path: Path | str) -> SwebenchInstance:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("SWE-bench instance file must contain a JSON object")
    return SwebenchInstance.from_mapping(data)


def run_swebench_instance(
    instance: SwebenchInstance,
    workspace: Path | str,
    output_dir: Path | str,
    model_name: str,
    run_id: str,
    agent_factory: Callable[[Path], AgentLike] | None = None,
) -> SwebenchRunResult:
    workspace_path = Path(workspace).resolve()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    task = build_agent_task(instance)
    agent = agent_factory(workspace_path) if agent_factory else _build_agent(workspace_path, run_id, model_name)
    agent_result = agent.run(task)
    patch = extract_git_diff(workspace_path)

    changed_files = list(getattr(agent_result, "changed_files", []) or [])
    executed_commands = list(getattr(agent_result, "executed_commands", []) or [])
    report_path = output_path / f"{run_id}.report.json"

    if not patch.strip():
        result = SwebenchRunResult(
            instance_id=instance.instance_id,
            success=False,
            run_id=run_id,
            model_name=model_name,
            model_patch="",
            prediction_path=None,
            report_path=report_path,
            changed_files=changed_files,
            executed_commands=executed_commands,
            failure_reason="empty_patch",
        )
        _write_report(result, agent_result)
        return result

    prediction_path = output_path / f"{run_id}.predictions.jsonl"
    record = create_prediction_record(
        instance_id=instance.instance_id,
        model_name_or_path=model_name,
        model_patch=patch,
    )
    write_predictions_jsonl([record], prediction_path)

    result = SwebenchRunResult(
        instance_id=instance.instance_id,
        success=bool(getattr(agent_result, "success", False)),
        run_id=run_id,
        model_name=model_name,
        model_patch=patch,
        prediction_path=prediction_path,
        report_path=report_path,
        changed_files=changed_files,
        executed_commands=executed_commands,
    )
    _write_report(result, agent_result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one prepared SWE-bench instance with this agent")
    parser.add_argument("--instance-file", required=True, help="Path to a SWE-bench instance JSON object")
    parser.add_argument("--workspace", required=True, help="Prepared repository workspace at the base commit")
    parser.add_argument("--output-dir", default="benchmarks/reports", help="Directory for predictions and report")
    parser.add_argument("--model", default=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"), help="Model name")
    parser.add_argument("--run-id", required=True, help="Stable run id")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_swebench_instance(
        instance=load_instance_file(args.instance_file),
        workspace=args.workspace,
        output_dir=args.output_dir,
        model_name=args.model,
        run_id=args.run_id,
    )
    print(result.report_path)
    return 0 if result.success else 1


def _build_agent(workspace: Path, run_id: str, model_name: str) -> Agent:
    return Agent(
        model_client=ModelClient(model=model_name),
        workspace=workspace,
        tool_registry=build_default_registry(workspace),
        logger=SessionLogger(workspace / "logs" / f"{run_id}.jsonl", run_id),
        max_steps=20,
    )


def _write_report(result: SwebenchRunResult, agent_result: Any) -> None:
    payload = asdict(result)
    payload["prediction_path"] = str(result.prediction_path) if result.prediction_path else None
    payload["report_path"] = str(result.report_path)
    payload["agent"] = {
        "success": bool(getattr(agent_result, "success", False)),
        "final_message": str(getattr(agent_result, "final_message", "")),
        "steps": int(getattr(agent_result, "steps", 0)),
    }
    result.report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
