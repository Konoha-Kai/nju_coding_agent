from __future__ import annotations

from pathlib import Path
from typing import Callable

from agent.tooling import ToolRegistry
from tools.filesystem import build_filesystem_tools
from tools.shell import build_shell_tools

DangerousCommandConfirmation = Callable[[str, str], bool]


def build_default_registry(
    workspace: Path | str,
    confirm_dangerous: DangerousCommandConfirmation | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in build_filesystem_tools(workspace):
        registry.register(tool)
    for tool in build_shell_tools(workspace, confirm_dangerous=confirm_dangerous):
        registry.register(tool)
    return registry
