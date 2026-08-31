from __future__ import annotations

import json
from pathlib import Path

from benchmarks.humaneval_runner import (
    HumanEvalProblem,
    build_humaneval_agent_task,
    evaluate_completion,
    load_humaneval_problems,
    run_humaneval_subset,
)


DATASET_PATH = Path("benchmarks/data/HumanEval/HumanEval.jsonl.gz")


def test_load_humaneval_problems_reads_official_dataset() -> None:
    problems = load_humaneval_problems(DATASET_PATH, limit=3)

    assert len(problems) == 3
    assert problems[0].task_id.startswith("HumanEval/")
    assert "def " in problems[0].prompt
    assert problems[0].entry_point


def test_build_humaneval_agent_task_contains_prompt_and_output_contract() -> None:
    problem = HumanEvalProblem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n",
        canonical_solution="    return a + b\n",
        test="def check(candidate):\n    assert candidate(1, 2) == 3\n",
        entry_point="add",
    )

    task = build_humaneval_agent_task(problem)

    assert "HumanEval/0" in task
    assert "def add(a, b):" in task
    assert "solution.py" in task
    assert "Run the provided tests" in task
    assert "Do not modify files outside the workspace." in task


def test_evaluate_completion_passes_correct_solution() -> None:
    problem = HumanEvalProblem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n",
        canonical_solution="    return a + b\n",
        test="def check(candidate):\n    assert candidate(1, 2) == 3\n",
        entry_point="add",
    )

    result = evaluate_completion(problem, "    return a + b\n")

    assert result["passed"] is True
    assert result["result"] == "passed"


def test_evaluate_completion_fails_wrong_solution() -> None:
    problem = HumanEvalProblem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n",
        canonical_solution="    return a + b\n",
        test="def check(candidate):\n    assert candidate(1, 2) == 3\n",
        entry_point="add",
    )

    result = evaluate_completion(problem, "    return a - b\n")

    assert result["passed"] is False
    assert result["result"] == "failed"


def test_run_humaneval_subset_writes_samples_and_report() -> None:
    class FakeAgent:
        def run(self, task: str):
            class Result:
                success = True
                final_message = "```python\n    return a + b\n```"
                steps = 1
                changed_files = []
                executed_commands = []

            return Result()

    problem = HumanEvalProblem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n",
        canonical_solution="    return a + b\n",
        test="def check(candidate):\n    assert candidate(1, 2) == 3\n",
        entry_point="add",
    )
    output_dir = Path("test_workspace") / "humaneval_subset"
    output_dir.mkdir(parents=True, exist_ok=True)

    report = run_humaneval_subset(
        problems=[problem],
        output_dir=output_dir,
        model_name="fake-model",
        agent_factory=lambda workspace: FakeAgent(),
    )

    assert report["pass@1"] == 1.0
    samples = [
        json.loads(line)
        for line in (output_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert samples == [{"task_id": "HumanEval/0", "completion": "    return a + b\n"}]
    assert (output_dir / "report.json").exists()


def test_run_humaneval_subset_prefers_solution_file_over_final_message() -> None:
    class FileWritingAgent:
        def __init__(self, workspace: Path) -> None:
            self.workspace = workspace

        def run(self, task: str):
            (self.workspace / "solution.py").write_text(
                "def add(a, b):\n    return a + b\n",
                encoding="utf-8",
            )

            class Result:
                success = True
                final_message = "done"
                steps = 2
                changed_files = ["solution.py"]
                executed_commands = []

            return Result()

    problem = HumanEvalProblem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n",
        canonical_solution="    return a + b\n",
        test="def check(candidate):\n    assert candidate(1, 2) == 3\n",
        entry_point="add",
    )
    output_dir = Path("test_workspace") / "humaneval_solution_file"
    output_dir.mkdir(parents=True, exist_ok=True)

    report = run_humaneval_subset(
        problems=[problem],
        output_dir=output_dir,
        model_name="fake-model",
        agent_factory=lambda workspace: FileWritingAgent(workspace),
    )

    assert report["pass@1"] == 1.0
    sample = json.loads((output_dir / "samples.jsonl").read_text(encoding="utf-8").strip())
    assert sample["completion"] == "    return a + b\n"
