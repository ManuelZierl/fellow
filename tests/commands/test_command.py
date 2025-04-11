import pytest
from pydantic import ValidationError

from fellow.commands import Command, CommandInput, ViewFileInput, view_file
from fellow.commands.command import CommandContext


def test_command_openai_schema():
    command = Command(ViewFileInput, view_file)
    assert command.openai_schema() == {
        "name": "view_file",
        "description": "View the contents of a file, optionally between specific line numbers.",
        "parameters": {
            "properties": {
                "filepath": {
                    "description": "The path to the file to be viewed.",
                    "title": "Filepath",
                    "type": "string",
                },
                "from_line": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "Optional 1-based starting line number.",
                    "title": "From Line",
                },
                "to_line": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "Optional 1-based ending line number (inclusive).",
                    "title": "To Line",
                },
            },
            "required": ["filepath"],
            "title": "ViewFileInput",
            "type": "object",
        },
    }

    with pytest.raises(ValueError) as err:
        Command(ViewFileInput, lambda x, y: None).openai_schema()
    assert str(err.value) == "[ERROR] Command handler is __doc__ is empty"

    with pytest.raises(ValueError) as err:
        Command(ViewFileInput, "no-name").openai_schema()
    assert str(err.value) == "[ERROR] Command handler is not callable with __name__."


def test_command_run():
    class CommandInputMock(CommandInput):
        a: str
        b: int

    def mock_command_handler(args: CommandInputMock, context: CommandContext) -> str:
        return f"Received {args.a} and {args.b} context: {context['ai_client']}"

    command = Command(CommandInputMock, mock_command_handler)
    context = {"ai_client": "context-mock"}  # Mocked context

    result = command.run('{"a": "abc", "b": 12}', context)
    assert result == "Received abc and 12 context: context-mock"

    result = command.run('{"a": "abc"}', context)
    assert "validation error" in result

    def mock_command_handler_fails(
        args: CommandInputMock, context: CommandContext
    ) -> str:
        raise ValueError("Mock error")

    # test with a command handler that raises an exception
    command = Command(CommandInputMock, mock_command_handler_fails)
    result = command.run('{"a": "abc", "b": 12}', context)
    assert result == "[ERROR] Command execution failed: Mock error"

    command = Command(CommandInputMock, "no-name")
    with pytest.raises(ValueError) as err:
        command.run('{"a": "abc"}', context)
    assert str(err.value) == "[ERROR] Command handler is not callable with __name__."
