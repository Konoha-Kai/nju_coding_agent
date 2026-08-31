from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class SwebenchInstance:
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str
    hints_text: str = ""
    test_patch: str = ""

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SwebenchInstance":
        return cls(
            instance_id=str(data["instance_id"]),
            repo=str(data["repo"]),
            base_commit=str(data["base_commit"]),
            problem_statement=str(data["problem_statement"]),
            hints_text=str(data.get("hints_text") or ""),
            test_patch=str(data.get("test_patch") or ""),
        )


def build_agent_task(instance: SwebenchInstance) -> str:
    sections = [
        "You are solving a public SWE-bench instance.",
        f"Instance id: {instance.instance_id}",
        f"Repository: {instance.repo}",
        f"Base commit: {instance.base_commit}",
        "",
        "Issue:",
        instance.problem_statement.strip(),
    ]

    if instance.hints_text.strip():
        sections.extend(["", "Hints:", instance.hints_text.strip()])
    if instance.test_patch.strip():
        sections.extend(["", "Test patch summary:", _summarize_patch(instance.test_patch)])

    sections.extend(
        [
            "",
            "Instructions:",
            "- Inspect the repository before editing.",
            "- Make the smallest code change that resolves the issue.",
            "- Do not modify files outside the workspace.",
            "- Do not edit environment files, credentials, or generated logs.",
            "- Run the relevant tests when possible.",
            "- If tests fail, use the failure output to continue debugging.",
            "- Finish with a concise summary of changed files and test results.",
        ]
    )
    return "\n".join(sections)


def create_prediction_record(
    instance_id: str,
    model_name_or_path: str,
    model_patch: str,
) -> dict[str, str]:
    if not instance_id.strip():
        raise ValueError("instance_id must not be empty")
    if not model_name_or_path.strip():
        raise ValueError("model_name_or_path must not be empty")
    if not model_patch.strip():
        raise ValueError("model_patch must not be empty")
    return {
        "instance_id": instance_id,
        "model_name_or_path": model_name_or_path,
        "model_patch": model_patch,
    }


def write_predictions_jsonl(records: Iterable[dict[str, str]], output_path: Path | str) -> Path:
    materialized = list(records)
    if not materialized:
        raise ValueError("records must not be empty")

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as file:
        for record in materialized:
            _validate_prediction_record(record)
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return target


def extract_git_diff(workspace: Path | str) -> str:
    workspace_path = Path(workspace).resolve()
    if not (workspace_path / ".git").exists():
        raise RuntimeError(f"git diff failed: workspace is not a git repository: {workspace_path}")

    completed = subprocess.run(
        ["git", "diff", "--binary"],
        cwd=workspace_path,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git diff failed: {completed.stderr.strip()}")
    return completed.stdout


def _validate_prediction_record(record: dict[str, str]) -> None:
    required = {"instance_id", "model_name_or_path", "model_patch"}
    missing = sorted(required - set(record))
    if missing:
        raise ValueError(f"prediction record missing fields: {', '.join(missing)}")
    create_prediction_record(
        instance_id=record["instance_id"],
        model_name_or_path=record["model_name_or_path"],
        model_patch=record["model_patch"],
    )


def _summarize_patch(patch: str, max_lines: int = 40) -> str:
    lines = patch.strip().splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)
    shown = "\n".join(lines[:max_lines])
    return f"{shown}\n...[truncated {len(lines) - max_lines} lines]"
