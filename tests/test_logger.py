import json
import shutil
import uuid
from pathlib import Path

from agent.logger import SessionLogger


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_session_logger_writes_jsonl_events() -> None:
    workspace = make_workspace()
    log_path = workspace / "logs" / "session.jsonl"
    logger = SessionLogger(log_path=log_path, session_id="session-1")

    try:
        logger.log("user_task", {"task": "hello"})
        logger.log("agent_finish", {"success": True})
        records = [
            json.loads(line)
            for line in log_path.read_text(encoding="utf-8").splitlines()
        ]
    finally:
        remove_workspace(workspace)

    assert [record["event"] for record in records] == ["user_task", "agent_finish"]
    assert records[0]["session_id"] == "session-1"
    assert records[0]["data"] == {"task": "hello"}
    assert "time" in records[0]


def test_session_logger_creates_parent_directory() -> None:
    workspace = make_workspace()
    log_path = workspace / "nested" / "logs" / "session.jsonl"
    logger = SessionLogger(log_path=log_path, session_id="session-1")

    try:
        logger.log("event", {})
        exists = log_path.exists()
    finally:
        remove_workspace(workspace)

    assert exists

