from pathlib import Path

import pytest

from fellow.utils.init_command import init_command


def test_init_command_creates_expected_file(tmp_path: Path):
    # Arrange
    command_name = "say_hello"
    target_dir = tmp_path / "commands"

    # Act
    result_path = init_command(command_name, str(target_dir))

    # Assert: File created
    assert result_path.exists()
    assert result_path.name == "say_hello.py"

    content = result_path.read_text()

    # Assert: Content includes generated class and function
    assert "class SayHelloInput(CommandInput)" in content
    assert "def say_hello(args: SayHelloInput, context: CommandContext)" in content

    # Assert: Raises on duplicate creation
    with pytest.raises(FileExistsError):
        init_command(command_name, str(target_dir))
