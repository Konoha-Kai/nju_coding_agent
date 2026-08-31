from dataclasses import dataclass
from pathlib import Path
import shutil
import uuid

from agent.loop import Agent
from agent.model_client import ModelReply


@dataclass
class FakeModelClient:
    replies: list[str]

    def chat(self, messages):
        return ModelReply(content=self.replies.pop(0))


def make_workspace() -> Path:
    root = Path("test_workspace") / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=False)
    return root


def remove_workspace(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def test_agent_runs_actions_until_final() -> None:
    workspace = make_workspace()
    model = FakeModelClient(
        [
            '{"action":"write_file","path":"result.txt","content":"ok"}',
            '{"action":"final","message":"task complete"}',
        ]
    )
    agent = Agent(model_client=model, workspace=workspace, max_steps=3)

    try:
        result = agent.run("create result")

        assert result.success
        assert result.final_message == "task complete"
        assert (workspace / "result.txt").read_text(encoding="utf-8") == "ok"
        assert result.steps == 2
    finally:
        remove_workspace(workspace)
