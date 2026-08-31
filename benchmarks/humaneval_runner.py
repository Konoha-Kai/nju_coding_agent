from __future__ import annotations

import argparse
import gzip
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

from agent import Agent
from agent.bootstrap import build_default_registry
from agent.logger import SessionLogger
from agent.model_client import ModelClient


@dataclass(frozen=True)
class HumanEvalProblem:
    task_id: str
    prompt: str
    canonical_solution: str
    test: str
    entry_point: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "HumanEvalProblem":
        return cls(
            task_id=str(data["task_id"]),
            prompt=str(data["prompt"]),
            canonical_solution=str(data.get("canonical_solution") or ""),
            test=str(data["test"]),
            entry_point=str(data["entry_point"]),
        )


class AgentLike(Protocol):
    def run(self, task: str) -> Any:
        ...


def load_humaneval_problems(
    dataset_path: Path | str,
    limit: int | None = None,
) -> list[HumanEvalProblem]:
    problems: list[HumanEvalProblem] = []
    with gzip.open(dataset_path, "rt", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                problems.append(HumanEvalProblem.from_mapping(json.loads(line)))
            if limit is not None and len(problems) >= limit:
                break
    return problems


def build_humaneval_agent_task(problem: HumanEvalProblem) -> str:
    return "\n".join(
        [
            "Solve this public HumanEval Python programming task.",
            f"Task id: {problem.task_id}",
            "",
            "Write only the function completion for the given prompt.",
            "The completion should be valid Python code that continues the prompt.",
            "Do not include markdown unless you need to explain; final answer should contain code.",
            "Do not modify files outside the workspace.",
            "Run the provided tests when possible.",
            "",
            "Target file: solution.py",
            "Prompt:",
            problem.prompt.rstrip(),
            "",
            "Entry point:",
            problem.entry_point,
        ]
    )


def evaluate_completion(problem: HumanEvalProblem, completion: str, timeout_seconds: int = 5) -> dict[str, Any]:
    workspace = Path("test_workspace") / "humaneval_exec" / _safe_task_name(problem.task_id)
    workspace.mkdir(parents=True, exist_ok=True)
    script = workspace / "check_solution.py"
    candidate_code = problem.prompt + completion
    script.write_text(
        "\n\n".join(
            [
                candidate_code,
                problem.test,
                f"check({problem.entry_point})",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        ["python", str(script)],
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    if completed.returncode == 0:
        return {"passed": True, "result": "passed", "stdout": completed.stdout, "stderr": completed.stderr}
    return {"passed": False, "result": "failed", "stdout": completed.stdout, "stderr": completed.stderr}


def run_humaneval_subset(
    problems: Iterable[HumanEvalProblem],
    output_dir: Path | str,
    model_name: str,
    agent_factory: Callable[[Path], AgentLike] | None = None,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    samples_path = output_path / "samples.jsonl"
    report_path = output_path / "report.json"
    rows = []
    passed = 0

    with samples_path.open("w", encoding="utf-8", newline="\n") as samples_file:
        for problem in problems:
            workspace = output_path / "workspaces" / _safe_task_name(problem.task_id)
            workspace.mkdir(parents=True, exist_ok=True)
            agent = agent_factory(workspace) if agent_factory else _build_agent(workspace, problem.task_id, model_name)
            agent_result = agent.run(build_humaneval_agent_task(problem))
            completion = _load_completion(problem, workspace, agent_result)
            evaluation = evaluate_completion(problem, completion)
            passed += int(evaluation["passed"])
            sample = {"task_id": problem.task_id, "completion": completion}
            samples_file.write(json.dumps(sample, ensure_ascii=False) + "\n")
            rows.append(
                {
                    "task_id": problem.task_id,
                    "passed": evaluation["passed"],
                    "result": evaluation["result"],
                    "agent_success": bool(getattr(agent_result, "success", False)),
                    "steps": int(getattr(agent_result, "steps", 0)),
                    "stdout": evaluation["stdout"],
                    "stderr": evaluation["stderr"],
                }
            )

    total = len(rows)
    report = {
        "benchmark": "HumanEval",
        "model": model_name,
        "total": total,
        "passed": passed,
        "pass@1": passed / total if total else 0.0,
        "samples_path": str(samples_path),
        "results": rows,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def extract_completion(text: str) -> str:
    fenced = re.search(r"```(?:python)?[ \t]*\r?\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip("\n") + "\n"
    return text.strip("\n") + "\n"


def _load_completion(problem: HumanEvalProblem, workspace: Path, agent_result: Any) -> str:
    solution_path = workspace / "solution.py"
    if solution_path.exists():
        solution = solution_path.read_text(encoding="utf-8")
        if solution.startswith(problem.prompt):
            return solution[len(problem.prompt) :].strip("\n") + "\n"
        return solution.strip("\n") + "\n"
    return extract_completion(str(getattr(agent_result, "final_message", "")))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight HumanEval benchmark subset")
    parser.add_argument("--dataset", default="benchmarks/data/HumanEval/HumanEval.jsonl.gz")
    parser.add_argument("--output-dir", default="benchmarks/reports/humaneval")
    parser.add_argument("--model", default="deepseek-chat")
    parser.add_argument("--limit", type=int, default=1)
    return parser.parse_args(argv)


def main(
    argv: list[str] | None = None,
    agent_factory: Callable[[Path], AgentLike] | None = None,
) -> int:
    args = parse_args(argv)
    problems = load_humaneval_problems(args.dataset, limit=args.limit)
    report = run_humaneval_subset(problems, args.output_dir, args.model, agent_factory=agent_factory)
    print(json.dumps({"pass@1": report["pass@1"], "passed": report["passed"], "total": report["total"]}))
    return 0 if report["passed"] == report["total"] else 1


def _build_agent(workspace: Path, task_id: str, model_name: str) -> Agent:
    safe_id = _safe_task_name(task_id)
    return Agent(
        model_client=ModelClient(model=model_name),
        workspace=workspace,
        tool_registry=build_default_registry(workspace),
        logger=SessionLogger(workspace / "logs" / f"{safe_id}.jsonl", safe_id),
        max_steps=8,
    )


def _safe_task_name(task_id: str) -> str:
    return task_id.replace("/", "_").replace("\\", "_")


if __name__ == "__main__":
    raise SystemExit(main())
