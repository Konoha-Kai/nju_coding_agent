import pytest

from agent.tooling import ToolRegistry, ToolResult, ToolSpec


def make_echo_tool() -> ToolSpec:
    return ToolSpec(
        name="echo",
        description="Return the provided text.",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        handler=lambda args: ToolResult(ok=True, content=args["text"]),
    )


def test_tool_spec_exports_deepseek_function_schema() -> None:
    schema = make_echo_tool().to_openai_tool()

    assert schema == {
        "type": "function",
        "function": {
            "name": "echo",
            "description": "Return the provided text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    }


def test_registry_registers_and_runs_tool() -> None:
    registry = ToolRegistry()
    registry.register(make_echo_tool())

    result = registry.run("echo", {"text": "hello"})

    assert result == ToolResult(ok=True, content="hello")


def test_registry_exports_all_tool_schemas_in_registration_order() -> None:
    registry = ToolRegistry()
    registry.register(make_echo_tool())
    registry.register(
        ToolSpec(
            name="noop",
            description="No operation.",
            parameters={"type": "object", "properties": {}},
            handler=lambda args: ToolResult(ok=True, content="done"),
        )
    )

    schemas = registry.to_openai_tools()

    assert [item["function"]["name"] for item in schemas] == ["echo", "noop"]


def test_registry_rejects_duplicate_tool_names() -> None:
    registry = ToolRegistry()
    registry.register(make_echo_tool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(make_echo_tool())


def test_registry_returns_error_for_unknown_tool() -> None:
    result = ToolRegistry().run("missing", {})

    assert not result.ok
    assert "Unknown tool" in result.content


def test_registry_wraps_handler_exceptions_as_tool_errors() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="broken",
            description="Raise an error.",
            parameters={"type": "object", "properties": {}},
            handler=lambda args: (_ for _ in ()).throw(RuntimeError("boom")),
        )
    )

    result = registry.run("broken", {})

    assert not result.ok
    assert "boom" in result.content

