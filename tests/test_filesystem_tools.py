import shutil
import uuid
from pathlib import Path

from agent.tooling import ToolResult
from tools.filesystem import build_filesystem_tools


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def tools_by_name(workspace: Path):
    return {tool.name: tool for tool in build_filesystem_tools(workspace)}


def test_build_filesystem_tools_exports_three_tools() -> None:
    workspace = make_workspace()

    try:
        tools = tools_by_name(workspace)
    finally:
        remove_workspace(workspace)

    assert sorted(tools) == ["list_files", "read_file", "write_file"]


def test_list_files_returns_non_recursive_entries() -> None:
    workspace = make_workspace()
    (workspace / "pkg").mkdir()
    (workspace / "pkg" / "inner.py").write_text("x = 1", encoding="utf-8")
    (workspace / "README.md").write_text("demo", encoding="utf-8")

    try:
        result = tools_by_name(workspace)["list_files"].handler(
            {"path": ".", "recursive": False}
        )
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "README.md" in result.content
    assert "pkg/" in result.content
    assert "pkg/inner.py" not in result.content


def test_list_files_returns_recursive_entries() -> None:
    workspace = make_workspace()
    (workspace / "pkg").mkdir()
    (workspace / "pkg" / "inner.py").write_text("x = 1", encoding="utf-8")

    try:
        result = tools_by_name(workspace)["list_files"].handler(
            {"path": ".", "recursive": True}
        )
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "pkg/" in result.content
    assert "pkg/inner.py" in result.content


def test_list_files_reports_missing_path() -> None:
    workspace = make_workspace()

    try:
        result = tools_by_name(workspace)["list_files"].handler({"path": "missing"})
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "does not exist" in result.content


def test_read_file_returns_file_content() -> None:
    workspace = make_workspace()
    (workspace / "hello.txt").write_text("hello", encoding="utf-8")

    try:
        result = tools_by_name(workspace)["read_file"].handler({"path": "hello.txt"})
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert result.content == "hello"
    assert result.metadata == {
        "path": "hello.txt",
        "characters": 5,
        "truncated": False,
    }


def test_read_file_truncates_long_content() -> None:
    workspace = make_workspace()
    (workspace / "long.txt").write_text("abcdef", encoding="utf-8")

    try:
        result = tools_by_name(workspace)["read_file"].handler(
            {"path": "long.txt", "max_chars": 3}
        )
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert result.content == "abc\n...[truncated]"
    assert result.metadata["truncated"] is True


def test_read_file_reports_directory_error() -> None:
    workspace = make_workspace()
    (workspace / "pkg").mkdir()

    try:
        result = tools_by_name(workspace)["read_file"].handler({"path": "pkg"})
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "not a file" in result.content


def test_write_file_creates_parent_directories_and_reports_metadata() -> None:
    workspace = make_workspace()

    try:
        result = tools_by_name(workspace)["write_file"].handler(
            {"path": "pkg/generated.py", "content": "VALUE = 42\n"}
        )
        content = (workspace / "pkg" / "generated.py").read_text(encoding="utf-8")
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert content == "VALUE = 42\n"
    assert result.metadata["path"] == "pkg/generated.py"
    assert result.metadata["characters"] == 11
