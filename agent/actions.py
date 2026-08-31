from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    content: str


def parse_action(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model reply is not valid JSON: {exc}") from exc

    if not isinstance(value, dict):
        raise ValueError("Model reply must be a JSON object.")
    if not isinstance(value.get("action"), str):
        raise ValueError("Model reply must include a string action field.")
    return value


class LocalActions:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace).resolve()

    def execute(self, action: dict[str, Any]) -> ActionResult:
        name = action["action"]
        if name == "list_files":
            return self.list_files(
                path=str(action.get("path", ".")),
                recursive=bool(action.get("recursive", False)),
            )
        if name == "read_file":
            return self.read_file(
                path=str(action["path"]),
                max_chars=int(action.get("max_chars", 12000)),
            )
        if name == "write_file":
            return self.write_file(
                path=str(action["path"]),
                content=str(action.get("content", "")),
            )
        if name == "run_command":
            return self.run_command(
                command=str(action["command"]),
                timeout_seconds=int(action.get("timeout_seconds", 30)),
            )
        return ActionResult(False, f"Unknown action: {name}")

    def list_files(self, path: str = ".", recursive: bool = False) -> ActionResult:
        target = self.workspace / path
        if not target.exists():
            return ActionResult(False, f"Path does not exist: {path}")

        pattern = "**/*" if recursive else "*"
        entries = []
        for item in sorted(target.glob(pattern)):
            rel = item.relative_to(self.workspace)
            suffix = "/" if item.is_dir() else ""
            entries.append(f"{rel.as_posix()}{suffix}")

        return ActionResult(True, "\n".join(entries) if entries else "(empty)")

    def read_file(self, path: str, max_chars: int = 12000) -> ActionResult:
        target = self.workspace / path
        if not target.exists():
            return ActionResult(False, f"File does not exist: {path}")
        if not target.is_file():
            return ActionResult(False, f"Path is not a file: {path}")

        content = target.read_text(encoding="utf-8")
        if len(content) > max_chars:
            return ActionResult(True, content[:max_chars] + "\n...[truncated]")
        return ActionResult(True, content)

    def write_file(self, path: str, content: str) -> ActionResult:
        target = self.workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ActionResult(True, f"Wrote {len(content)} characters to {path}")

    def run_command(self, command: str, timeout_seconds: int = 30) -> ActionResult:
        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            return ActionResult(
                False,
                f"Command timed out after {timeout_seconds}s\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}",
            )

        return ActionResult(
            completed.returncode == 0,
            "\n".join(
                [
                    f"exit_code={completed.returncode}",
                    "STDOUT:",
                    completed.stdout.strip(),
                    "STDERR:",
                    completed.stderr.strip(),
                ]
            ).strip(),
        )

