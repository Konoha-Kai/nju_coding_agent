from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from agent.tooling import ToolResult, ToolSpec


def build_shell_tools(workspace: Path | str) -> list[ToolSpec]:
    shell_tools = ShellTools(workspace)
    return [
        ToolSpec(
            name="run_command",
            description="Run a shell command in the workspace and return exit code, stdout, and stderr.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to run from the workspace directory.",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum runtime before the command is stopped.",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
            handler=shell_tools.run_command,
        )
    ]


class ShellTools:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace).resolve()

    def run_command(self, arguments: dict[str, Any]) -> ToolResult:
        command = str(arguments["command"])
        timeout_seconds = int(arguments.get("timeout_seconds", 30))

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
            return ToolResult(
                ok=False,
                content=(
                    f"Command timed out after {timeout_seconds}s\n"
                    f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                ),
                metadata={
                    "command": command,
                    "timeout_seconds": timeout_seconds,
                    "timed_out": True,
                    "exit_code": None,
                },
            )

        return ToolResult(
            ok=completed.returncode == 0,
            content="\n".join(
                [
                    f"exit_code={completed.returncode}",
                    "STDOUT:",
                    completed.stdout.strip(),
                    "STDERR:",
                    completed.stderr.strip(),
                ]
            ).strip(),
            metadata={
                "command": command,
                "timeout_seconds": timeout_seconds,
                "timed_out": False,
                "exit_code": completed.returncode,
            },
        )

