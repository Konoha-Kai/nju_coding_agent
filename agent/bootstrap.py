from __future__ import annotations

from pathlib import Path

from agent.tooling import ToolRegistry
from tools.filesystem import build_filesystem_tools
from tools.shell import build_shell_tools


def build_default_registry(workspace: Path | str) -> ToolRegistry:
    registry = ToolRegistry()
    for tool in build_filesystem_tools(workspace):
        registry.register(tool)
    for tool in build_shell_tools(workspace):
        registry.register(tool)
    return registry

