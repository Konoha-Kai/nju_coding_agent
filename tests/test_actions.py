import shutil
import uuid
from pathlib import Path

from agent.actions import LocalActions, parse_action


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_parse_action_accepts_plain_json() -> None:
    action = parse_action('{"action":"final","message":"done"}')

    assert action == {"action": "final", "message": "done"}


def test_parse_action_accepts_fenced_json() -> None:
    action = parse_action('```json\n{"action":"list_files","path":"."}\n```')

    assert action["action"] == "list_files"


def test_local_actions_can_write_read_and_list_files() -> None:
    workspace = make_workspace()
    actions = LocalActions(workspace)

    try:
        write_result = actions.write_file("demo/hello.txt", "hello")
        read_result = actions.read_file("demo/hello.txt")
        list_result = actions.list_files("demo")
    finally:
        remove_workspace(workspace)

    assert write_result.ok
    assert read_result.ok
    assert read_result.content == "hello"
    assert "demo/hello.txt" in list_result.content


def test_local_actions_can_run_command() -> None:
    workspace = make_workspace()
    actions = LocalActions(workspace)

    try:
        result = actions.run_command('python -c "print(1 + 1)"', timeout_seconds=10)
    finally:
        remove_workspace(workspace)

    assert result.ok
    assert "2" in result.content
