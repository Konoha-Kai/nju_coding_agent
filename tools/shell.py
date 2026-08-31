from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from agent.safety import CommandSafetyPolicy
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
                    "allow_dangerous": {
                        "type": "boolean",
                        "description": "Explicitly allow commands that are normally blocked by safety policy.",
                        "default": False,
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
        self.command_policy = CommandSafetyPolicy()

    def run_command(self, arguments: dict[str, Any]) -> ToolResult:
        command = str(arguments["command"])
        timeout_seconds = int(arguments.get("timeout_seconds", 30))
        allow_dangerous = bool(arguments.get("allow_dangerous", False))
        decision = self.command_policy.evaluate(command, allow_dangerous=allow_dangerous)
        if not decision.allowed:
            return ToolResult(
                ok=False,
                content=decision.message,
                metadata={
                    "command": command,
                    "blocked": True,
                    "reason": decision.reason,
                    "timed_out": False,
                    "exit_code": None,
                },
            )

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
