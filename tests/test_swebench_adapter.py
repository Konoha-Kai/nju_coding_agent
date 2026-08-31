from __future__ import annotations

import json
import shutil
from uuid import uuid4
from pathlib import Path

import pytest

from benchmarks.swebench_adapter import (
    SwebenchInstance,
    build_agent_task,
    create_prediction_record,
    extract_git_diff,
    write_predictions_jsonl,
)


def make_workspace(name: str) -> Path:
    workspace = Path(__file__).resolve().parent / "test_workspace" / f"{name}_{uuid4().hex}"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    return workspace


def test_build_agent_task_includes_issue_and_constraints() -> None:
    instance = SwebenchInstance(
        instance_id="django__django-12345",
        repo="django/django",
        base_commit="abc123",
        problem_statement="Fix the timezone regression.",
        hints_text="Look at date parsing.",
        test_patch="diff --git a/tests/test_dates.py b/tests/test_dates.py",
    )

    task = build_agent_task(instance)

    assert "django__django-12345" in task
    assert "django/django" in task
    assert "abc123" in task
    assert "Fix the timezone regression." in task
    assert "Look at date parsing." in task
    assert "Do not modify files outside the workspace." in task
    assert "Run the relevant tests" in task


def test_build_agent_task_omits_empty_optional_fields() -> None:
    instance = SwebenchInstance(
        instance_id="sympy__sympy-20590",
        repo="sympy/sympy",
        base_commit="def456",
        problem_statement="Fix simplify output.",
    )

    task = build_agent_task(instance)

    assert "Hints:" not in task
    assert "Test patch summary:" not in task
    assert "sympy__sympy-20590" in task


def test_create_prediction_record_matches_swebench_jsonl_shape() -> None:
    record = create_prediction_record(
        instance_id="sympy__sympy-20590",
        model_name_or_path="deepseek-chat",
        model_patch="diff --git a/sympy/core.py b/sympy/core.py\n+fixed\n",
    )

    assert record == {
        "instance_id": "sympy__sympy-20590",
        "model_name_or_path": "deepseek-chat",
        "model_patch": "diff --git a/sympy/core.py b/sympy/core.py\n+fixed\n",
    }


def test_create_prediction_record_rejects_empty_patch() -> None:
    with pytest.raises(ValueError, match="model_patch"):
        create_prediction_record(
            instance_id="sympy__sympy-20590",
            model_name_or_path="deepseek-chat",
            model_patch="",
        )


def test_write_predictions_jsonl_writes_one_json_object_per_line() -> None:
    workspace = make_workspace("swebench_predictions")
    output_path = workspace / "predictions.jsonl"
    records = [
        create_prediction_record("repo__repo-1", "deepseek-chat", "diff --git a/a.py b/a.py\n+1\n"),
        create_prediction_record("repo__repo-2", "deepseek-chat", "diff --git a/b.py b/b.py\n+2\n"),
    ]

    write_predictions_jsonl(records, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert [json.loads(line)["instance_id"] for line in lines] == ["repo__repo-1", "repo__repo-2"]


def test_write_predictions_jsonl_rejects_empty_records() -> None:
    workspace = make_workspace("swebench_empty_predictions")

    with pytest.raises(ValueError, match="records"):
        write_predictions_jsonl([], workspace / "predictions.jsonl")


def test_extract_git_diff_returns_current_patch() -> None:
    workspace = make_workspace("swebench_git_diff")
    (workspace / "module.py").write_text("value = 1\n", encoding="utf-8")

    import subprocess

    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace, check=True)
    subprocess.run(["git", "add", "module.py"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=workspace, check=True, capture_output=True, text=True)
    (workspace / "module.py").write_text("value = 2\n", encoding="utf-8")

    diff = extract_git_diff(workspace)

    assert "diff --git a/module.py b/module.py" in diff
    assert "-value = 1" in diff
    assert "+value = 2" in diff


def test_extract_git_diff_rejects_non_git_workspace() -> None:
    workspace = make_workspace("swebench_no_git")

    with pytest.raises(RuntimeError, match="git diff"):
        extract_git_diff(workspace)
