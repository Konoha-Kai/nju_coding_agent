import shutil
import sys
import uuid
from pathlib import Path

from tools.shell import build_shell_tools


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def run_command_tool(workspace: Path):
    tools = {tool.name: tool for tool in build_shell_tools(workspace)}
    return tools["run_command"]


def test_build_shell_tools_exports_run_command() -> None:
    workspace = make_workspace()

    try:
        tools = {tool.name: tool for tool in build_shell_tools(workspace)}
    finally:
        remove_workspace(workspace)

    assert list(tools) == ["run_command"]
    assert tools["run_command"].to_openai_tool()["function"]["name"] == "run_command"


def test_run_command_returns_stdout_stderr_exit_code_and_metadata() -> None:
    workspace = make_workspace()
    command = (
        f'"{sys.executable}" -c "import sys; '
        f"print('out'); print('err', file=sys.stderr)\""
    )

    try:
        result = run_command_tool(workspace).handler(
            {"command": command, "timeout_seconds": 10}
        )
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "exit_code=0" in result.content
    assert "out" in result.content
    assert "err" in result.content
    assert result.metadata["exit_code"] == 0
    assert result.metadata["timed_out"] is False


def test_run_command_reports_nonzero_exit_as_not_ok() -> None:
    workspace = make_workspace()
    command = f'"{sys.executable}" -c "import sys; print(\'bad\'); sys.exit(3)"'

    try:
        result = run_command_tool(workspace).handler(
            {"command": command, "timeout_seconds": 10}
        )
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "exit_code=3" in result.content
    assert "bad" in result.content
    assert result.metadata["exit_code"] == 3
    assert result.metadata["timed_out"] is False


def test_run_command_reports_timeout() -> None:
    workspace = make_workspace()
    command = f'"{sys.executable}" -c "import time; time.sleep(2)"'

    try:
        result = run_command_tool(workspace).handler(
            {"command": command, "timeout_seconds": 1}
        )
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "timed out" in result.content
    assert result.metadata["timed_out"] is True


def test_run_command_uses_workspace_as_cwd() -> None:
    workspace = make_workspace()
    (workspace / "marker.txt").write_text("ok", encoding="utf-8")
    command = f'"{sys.executable}" -c "from pathlib import Path; print(Path(\'marker.txt\').read_text())"'

    try:
        result = run_command_tool(workspace).handler({"command": command})
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "ok" in result.content


def test_run_command_rejects_dangerous_delete_by_default() -> None:
    workspace = make_workspace()
    (workspace / "keep.txt").write_text("keep", encoding="utf-8")

    try:
        result = run_command_tool(workspace).handler({"command": "del keep.txt"})
        still_exists = (workspace / "keep.txt").exists()
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "dangerous command" in result.content
    assert result.metadata["blocked"] is True
    assert still_exists is True


def test_run_command_rejects_dependency_install_by_default() -> None:
    workspace = make_workspace()

    try:
        result = run_command_tool(workspace).handler({"command": "pip install requests"})
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "dangerous command" in result.content
    assert result.metadata["reason"] == "dependency_install"


def test_run_command_rejects_network_download_by_default() -> None:
    workspace = make_workspace()

    try:
        result = run_command_tool(workspace).handler({"command": "curl https://example.com/file"})
    finally:
        remove_workspace(workspace)

    assert not result.ok
    assert "dangerous command" in result.content
    assert result.metadata["reason"] == "network_download"


def test_run_command_allows_dangerous_command_when_explicitly_enabled() -> None:
    workspace = make_workspace()
    command = f'"{sys.executable}" -c "print(\'safe execution path\')"'

    try:
        result = run_command_tool(workspace).handler(
            {
                "command": command,
                "allow_dangerous": True,
            }
        )
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "safe execution path" in result.content
