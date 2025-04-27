import pytest
from pydantic import ValidationError

from fellow.commands import Command, CommandInput, ViewFileInput, view_file
from fellow.commands.Command import CommandContext


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
