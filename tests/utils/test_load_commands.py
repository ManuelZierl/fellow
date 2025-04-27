import textwrap
from pathlib import Path
from types import FunctionType
from unittest.mock import MagicMock

import pytest

from fellow.commands.Command import Command, CommandInput
from fellow.utils.load_commands import load_command_from_file, load_commands


def test_load_module_from_file(tmp_path: Path):
    # Arrange: create a valid Python file with a command object
    file_content = textwrap.dedent(
        """
        from fellow.commands.Command import Command, CommandContext, CommandInput
        from pydantic import Field

        class EchoInput(CommandInput):
            text: str = Field(..., description="Text to echo")

        def echo(args: EchoInput, context: CommandContext) -> str:
            \"""Echo the input text.\"""
            return args.text

        command = Command(EchoInput, echo) # todo: this should to be necessary
    """
    )

    file_path = tmp_path / "echo.py"
    file_path.write_text(file_content)

    module_name, module_command = load_command_from_file(file_path)

    assert module_name == "echo"
    assert isinstance(module_command.command_handler, FunctionType)
    assert module_command.command_handler.__name__ == "echo"
    assert module_command.command_handler.__doc__ == "Echo the input text."
    assert module_command.input_type.__name__ == "EchoInput"
    assert issubclass(module_command.input_type, CommandInput)

    assert (
        module_command.run('{"text": "Hello, World!"}', MagicMock()) == "Hello, World!"
    )


def test_load_command_from_file_raises_on_name_mismatch(tmp_path: Path):
    # Arrange: file is named 'echo.py', but defines function 'greet'
    file_content = textwrap.dedent(
        """
        from fellow.commands.Command import CommandInput, CommandContext
        from pydantic import Field

        class EchoInput(CommandInput):
            text: str = Field(..., description="Text to echo")

        def greet(args: EchoInput, context: CommandContext) -> str:
            \"""Echo the input text.\"""
            return args.text
    """
    )

    file_path = tmp_path / "echo.py"
    file_path.write_text(file_content)

    # Act + Assert
    with pytest.raises(ValueError, match=r"No function named 'echo' found in echo.py"):
        load_command_from_file(file_path)


def test_load_command_from_file_raises_on_wrong_signature(tmp_path: Path):
    file_content = textwrap.dedent(
        """
        from fellow.commands.Command import CommandInput, CommandContext
        from pydantic import Field

        class EchoInput(CommandInput):
            text: str = Field(..., description="Text to echo")

        def echo(args):  # Missing context
            \"""Echo the input text.\"""
            return args.text
    """
    )

    file_path = tmp_path / "echo.py"
    file_path.write_text(file_content)

    with pytest.raises(ValueError, match=r"must take two arguments: \(args, context\)"):
        load_command_from_file(file_path)


def test_load_commands_with_custom_command(tmp_path: Path):
    # Arrange: create a valid command file in custom command path
    commands_dir = tmp_path / ".fellow" / "commands"
    commands_dir.mkdir(parents=True)

    file_content = textwrap.dedent(
        """
        from fellow.commands.Command import CommandInput, CommandContext
        from pydantic import Field

        class EchoInput(CommandInput):
            text: str = Field(..., description="Text to echo")

        def echo(args: EchoInput, context: CommandContext) -> str:
            \"""Echo the input text.\"""
            return args.text
    """
    )

    command_file = commands_dir / "echo.py"
    command_file.write_text(file_content)

    # Create fake config
    config = MagicMock()
    config.custom_commands_paths = [str(commands_dir)]
    config.commands = ["echo", "view_file"]
    config.planning.active = True

    # Act
    commands = load_commands(config)

    # Assert
    assert len(commands) == 3
    assert "echo" in commands
    assert "view_file" in commands
    assert "make_plan" in commands
    echo_command = commands["echo"]

    assert isinstance(echo_command, Command)
    assert isinstance(echo_command.input_type, type)
    assert issubclass(echo_command.input_type, CommandInput)
    assert isinstance(echo_command.command_handler, FunctionType)

    result = echo_command.run('{"text": "Hello"}', MagicMock())
    assert result == "Hello"
