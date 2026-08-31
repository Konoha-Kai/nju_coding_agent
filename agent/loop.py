from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agent.actions import LocalActions, parse_action
from agent.context import ConversationContext
from agent.logger import SessionLogger
from agent.model_client import ModelClient
from agent.tooling import ToolRegistry, ToolResult


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
        tool_registry: ToolRegistry | None = None,
        logger: SessionLogger | None = None,
    ) -> None:
        self.model_client = model_client
        self.actions = LocalActions(workspace)
        self.tool_registry = tool_registry
        self.logger = logger
        self.max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        context = ConversationContext.start(task)
        observations: list[str] = []
        self._log("user_task", {"task": task, "max_steps": self.max_steps})

        for step in range(1, self.max_steps + 1):
            tools = self.tool_registry.to_openai_tools() if self.tool_registry else None
            reply = self.model_client.chat(context.messages, tools=tools)
            context.add_assistant(reply.content, tool_calls=reply.tool_calls)
            self._log(
                "model_reply",
                {
                    "step": step,
                    "finish_reason": reply.finish_reason,
                    "content": reply.content,
                    "tool_calls": [
                        {"id": call.id, "name": call.name, "arguments": call.arguments}
                        for call in reply.tool_calls
                    ],
                },
            )

            if reply.tool_calls and self.tool_registry:
                for call in reply.tool_calls:
                    self._log(
                        "tool_call",
                        {"step": step, "id": call.id, "name": call.name, "arguments": call.arguments},
                    )
                    try:
                        arguments = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError as exc:
                        result = ToolResult(
                            False,
                            f"Invalid tool arguments for {call.name}: {exc}",
                        )
                    else:
                        if not isinstance(arguments, dict):
                            result = ToolResult(
                                False,
                                f"Invalid tool arguments for {call.name}: expected object",
                            )
                        else:
                            result = self.tool_registry.run(call.name, arguments)

                    observation = f"Tool {call.name} ok={result.ok}\n{result.content}"
                    observations.append(observation)
                    context.add_tool_result(call.id, result)
                    self._log(
                        "tool_result",
                        {
                            "step": step,
                            "id": call.id,
                            "name": call.name,
                            "ok": result.ok,
                            "content": result.content,
                            "metadata": result.metadata,
                        },
                    )
                continue

            if self.tool_registry:
                agent_result = AgentResult(
                    success=True,
                    final_message=reply.content,
                    steps=step,
                    observations=observations,
                )
                self._log(
                    "agent_finish",
                    {
                        "success": agent_result.success,
                        "steps": agent_result.steps,
                        "final_message": agent_result.final_message,
                    },
                )
                return agent_result

            try:
                action = parse_action(reply.content)
            except ValueError as exc:
                observation = f"Invalid model action: {exc}"
                observations.append(observation)
                context.add_observation(observation)
                continue

            if action["action"] == "final":
                agent_result = AgentResult(
                    success=True,
                    final_message=str(action.get("message", "")),
                    steps=step,
                    observations=observations,
                )
                self._log(
                    "agent_finish",
                    {
                        "success": agent_result.success,
                        "steps": agent_result.steps,
                        "final_message": agent_result.final_message,
                    },
                )
                return agent_result

            result = self.actions.execute(action)
            observation = f"Action {action['action']} ok={result.ok}\n{result.content}"
            observations.append(observation)
            context.add_observation(observation)

        agent_result = AgentResult(
            success=False,
            final_message=f"Reached max_steps={self.max_steps} before final answer.",
            steps=self.max_steps,
            observations=observations,
        )
        self._log(
            "agent_error",
            {
                "success": agent_result.success,
                "steps": agent_result.steps,
                "final_message": agent_result.final_message,
            },
        )
        return agent_result

    def _log(self, event: str, data: dict) -> None:
        if self.logger:
            self.logger.log(event, data)
