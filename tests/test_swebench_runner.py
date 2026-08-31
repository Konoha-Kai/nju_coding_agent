from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from benchmarks.swebench_runner import (
    SwebenchRunResult,
    load_instance_file,
    run_swebench_instance,
)


@dataclass
class FakeAgentResult:
    success: bool = True
    final_message: str = "fixed"
    steps: int = 2
    observations: list[str] | None = None
    changed_files: list[str] | None = None
    executed_commands: list[str] | None = None


class EditingFakeAgent:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.received_task = ""

    def run(self, task: str) -> FakeAgentResult:
        self.received_task = task
        (self.workspace / "module.py").write_text("value = 2\n", encoding="utf-8")
        return FakeAgentResult(
            changed_files=["module.py"],
            executed_commands=["python -m pytest"],
        )


def make_workspace(name: str) -> Path:
    workspace = Path(__file__).resolve().parent / "test_workspace" / f"{name}_{uuid4().hex}"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    return workspace


def init_git_workspace(workspace: Path) -> None:
    (workspace / "module.py").write_text("value = 1\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace, check=True)
    subprocess.run(["git", "add", "module.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=workspace, check=True, capture_output=True, text=True)


def test_load_instance_file_reads_public_swebench_shape() -> None:
    workspace = make_workspace("runner_instance_file")
    instance_path = workspace / "instance.json"
    instance_path.write_text(
        json.dumps(
            {
                "instance_id": "sympy__sympy-20590",
                "repo": "sympy/sympy",
                "base_commit": "abc123",
                "problem_statement": "Fix the issue.",
                "hints_text": "",
            }
        ),
        encoding="utf-8",
    )

    instance = load_instance_file(instance_path)

    assert instance.instance_id == "sympy__sympy-20590"
    assert instance.repo == "sympy/sympy"
    assert instance.problem_statement == "Fix the issue."


def test_run_swebench_instance_writes_prediction_and_report() -> None:
    workspace = make_workspace("runner_workspace")
    init_git_workspace(workspace)
    output_dir = make_workspace("runner_output")
    instance = load_instance_file(
        _write_instance(
            output_dir,
            instance_id="demo__demo-1",
            problem_statement="Change value from 1 to 2.",
        )
    )
    created_agents: list[EditingFakeAgent] = []

    def agent_factory(agent_workspace: Path) -> EditingFakeAgent:
        agent = EditingFakeAgent(agent_workspace)
        created_agents.append(agent)
        return agent

    result = run_swebench_instance(
        instance=instance,
        workspace=workspace,
        output_dir=output_dir,
        model_name="deepseek-chat",
        run_id="unit-run",
        agent_factory=agent_factory,
    )

    assert isinstance(result, SwebenchRunResult)
    assert result.instance_id == "demo__demo-1"
    assert result.success is True
    assert result.prediction_path == output_dir / "unit-run.predictions.jsonl"
    assert result.report_path == output_dir / "unit-run.report.json"
    assert "diff --git a/module.py b/module.py" in result.model_patch
    assert created_agents[0].received_task.startswith("You are solving a public SWE-bench instance.")

    prediction = json.loads(result.prediction_path.read_text(encoding="utf-8").strip())
    assert prediction["instance_id"] == "demo__demo-1"
    assert prediction["model_name_or_path"] == "deepseek-chat"
    assert prediction["model_patch"] == result.model_patch

    report = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert report["instance_id"] == "demo__demo-1"
    assert report["changed_files"] == ["module.py"]
    assert report["executed_commands"] == ["python -m pytest"]


def test_run_swebench_instance_fails_when_agent_makes_no_patch() -> None:
    workspace = make_workspace("runner_empty_patch")
    init_git_workspace(workspace)
    output_dir = make_workspace("runner_empty_output")
    instance = load_instance_file(_write_instance(output_dir))

    class NoopAgent:
        def run(self, task: str) -> FakeAgentResult:
            return FakeAgentResult(changed_files=[], executed_commands=[])

    result = run_swebench_instance(
        instance=instance,
        workspace=workspace,
        output_dir=output_dir,
        model_name="deepseek-chat",
        run_id="empty-run",
        agent_factory=lambda _: NoopAgent(),
    )

    assert result.success is False
    assert result.model_patch == ""
    assert result.prediction_path is None
    assert result.report_path.exists()
    report = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert report["failure_reason"] == "empty_patch"


def _write_instance(
    directory: Path,
    instance_id: str = "demo__demo-1",
    problem_statement: str = "Fix issue.",
) -> Path:
    path = directory / "instance.json"
    path.write_text(
        json.dumps(
            {
                "instance_id": instance_id,
                "repo": "demo/demo",
                "base_commit": "abc123",
                "problem_statement": problem_statement,
            }
        ),
        encoding="utf-8",
    )
    return path
