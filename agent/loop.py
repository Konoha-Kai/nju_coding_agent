from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agent.actions import LocalActions, parse_action
from agent.context import ConversationContext
from agent.model_client import ModelClient


@dataclass(frozen=True)
class AgentResult:
    success: bool
    final_message: str
    steps: int
    observations: list[str] = field(default_factory=list)


class Agent:
    def __init__(
        self,
        model_client: ModelClient,
        workspace: Path | str,
        max_steps: int = 12,
    ) -> None:
        self.model_client = model_client
        self.actions = LocalActions(workspace)
        self.max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        context = ConversationContext.start(task)
        observations: list[str] = []

        for step in range(1, self.max_steps + 1):
            reply = self.model_client.chat(context.messages)
            context.add_assistant(reply.content)

            try:
                action = parse_action(reply.content)
            except ValueError as exc:
                observation = f"Invalid model action: {exc}"
                observations.append(observation)
                context.add_observation(observation)
                continue

            if action["action"] == "final":
                return AgentResult(
                    success=True,
                    final_message=str(action.get("message", "")),
                    steps=step,
                    observations=observations,
                )

            result = self.actions.execute(action)
            observation = f"Action {action['action']} ok={result.ok}\n{result.content}"
            observations.append(observation)
            context.add_observation(observation)

        return AgentResult(
            success=False,
            final_message=f"Reached max_steps={self.max_steps} before final answer.",
            steps=self.max_steps,
            observations=observations,
        )

