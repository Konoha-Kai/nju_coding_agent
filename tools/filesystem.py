from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.tooling import ToolResult, ToolSpec


def build_filesystem_tools(workspace: Path | str) -> list[ToolSpec]:
    file_tools = FilesystemTools(workspace)
    return [
        ToolSpec(
            name="list_files",
            description="List files and directories under a workspace path.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Workspace-relative path to list.",
                        "default": ".",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list nested files recursively.",
                        "default": False,
                    },
                },
            },
            handler=file_tools.list_files,
        ),
        ToolSpec(
            name="read_file",
            description="Read a UTF-8 text file from the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Workspace-relative file path.",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Maximum characters to return before truncation.",
                        "default": 12000,
                    },
                },
                "required": ["path"],
            },
            handler=file_tools.read_file,
        ),
        ToolSpec(
            name="write_file",
            description="Write UTF-8 text content to a workspace file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Workspace-relative file path.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full content to write.",
                    },
                },
                "required": ["path", "content"],
            },
            handler=file_tools.write_file,
        ),
    ]


class FilesystemTools:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace).resolve()

    def list_files(self, arguments: dict[str, Any]) -> ToolResult:
        path = str(arguments.get("path", "."))
        recursive = bool(arguments.get("recursive", False))
        target = self.workspace / path
        if not target.exists():
            return ToolResult(False, f"Path does not exist: {path}", {"path": path})
        if not target.is_dir():
            return ToolResult(False, f"Path is not a directory: {path}", {"path": path})

        pattern = "**/*" if recursive else "*"
        entries = []
        for item in sorted(target.glob(pattern), key=lambda item: item.as_posix()):
            rel = item.relative_to(self.workspace)
            suffix = "/" if item.is_dir() else ""
            entries.append(f"{rel.as_posix()}{suffix}")

        return ToolResult(
            True,
            "\n".join(entries) if entries else "(empty)",
            {"path": path, "recursive": recursive, "count": len(entries)},
        )

    def read_file(self, arguments: dict[str, Any]) -> ToolResult:
        path = str(arguments["path"])
        max_chars = int(arguments.get("max_chars", 12000))
        target = self.workspace / path

        if not target.exists():
            return ToolResult(False, f"File does not exist: {path}", {"path": path})
        if not target.is_file():
            return ToolResult(False, f"Path is not a file: {path}", {"path": path})

        content = target.read_text(encoding="utf-8")
        truncated = len(content) > max_chars
        if truncated:
            content = content[:max_chars] + "\n...[truncated]"
        return ToolResult(
            True,
            content,
            {
                "path": path,
                "characters": len(content),
                "truncated": truncated,
            },
        )

    def write_file(self, arguments: dict[str, Any]) -> ToolResult:
        path = str(arguments["path"])
        content = str(arguments.get("content", ""))
        target = self.workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult(
            True,
            f"Wrote {len(content)} characters to {path}",
            {"path": path, "characters": len(content)},
        )

