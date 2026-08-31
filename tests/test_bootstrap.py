import shutil
import uuid
from pathlib import Path

from agent.bootstrap import build_default_registry


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_build_default_registry_contains_all_sprint_2_tools() -> None:
    workspace = make_workspace()

    try:
        registry = build_default_registry(workspace)
        tool_names = [tool["function"]["name"] for tool in registry.to_openai_tools()]
    finally:
        remove_workspace(workspace)

    assert tool_names == ["list_files", "read_file", "write_file", "run_command"]


def test_default_registry_tools_are_executable() -> None:
    workspace = make_workspace()

    try:
        registry = build_default_registry(workspace)
        write_result = registry.run("write_file", {"path": "hello.txt", "content": "hi"})
        read_result = registry.run("read_file", {"path": "hello.txt"})
    finally:
        remove_workspace(workspace)

    assert write_result.ok
    assert read_result.ok
    assert read_result.content == "hi"
