import textwrap
from pathlib import Path
from types import FunctionType, SimpleNamespace
from unittest.mock import MagicMock

import pytest

from fellow.commands.Command import Command, CommandInput
from fellow.policies import PolicyConfig, RequireUserConfirmation
from fellow.utils.load_commands import (
    load_command_from_file,
    load_commands,
    load_policy_from_file,
)


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
    """
    )

    file_path = tmp_path / "echo.py"
    file_path.write_text(file_content)

    module_name, command_input, command_handler = load_command_from_file(file_path)

    assert module_name == "echo"
    assert isinstance(command_handler, FunctionType)
    assert command_handler.__name__ == "echo"
    assert command_handler.__doc__ == "Echo the input text."
    assert command_input.__name__ == "EchoInput"
    assert issubclass(command_input, CommandInput)

    command = Command(command_input, command_handler, [])

    assert command.run('{"text": "Hello, World!"}', MagicMock()) == "Hello, World!"


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
    config.commands = {
        "echo": MagicMock(policies=[]),
        "view_file": MagicMock(policies=[]),
    }
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


def test_load_policy_from_file_success(tmp_path: Path):
    file_path = tmp_path / "test_policy.py"
    file_path.write_text(
        textwrap.dedent(
            """
        from pydantic import BaseModel
        from fellow.policies.Policy import Policy, PolicyConfig

        class MyPolicyConfig(PolicyConfig):
            pass

        class MyPolicy(Policy[MyPolicyConfig]):
            def __init__(self, config):
                self.config = config
            def check(self, command_name, command_handler, args, context):
                return True
    """
        )
    )

    policy_name, policy_type, policy_config_type = load_policy_from_file(file_path)

    assert policy_name == "my_policy"
    assert issubclass(policy_type, object)
    assert issubclass(policy_config_type, PolicyConfig)


def test_load_policy_missing_config_class(tmp_path: Path):
    file_path = tmp_path / "bad_policy.py"
    file_path.write_text(
        textwrap.dedent(
            """
        class NotAPolicy:
            pass
    """
        )
    )

    with pytest.raises(ValueError, match="No subclass of PolicyConfig found"):
        load_policy_from_file(file_path)


def test_load_policy_missing_policy_class(tmp_path: Path):
    file_path = tmp_path / "incomplete_policy.py"
    file_path.write_text(
        textwrap.dedent(
            """
        from fellow.policies.Policy import PolicyConfig

        class IncompleteConfig(PolicyConfig):
            pass
    """
        )
    )

    with pytest.raises(
        ValueError, match="No class found matching PolicyConfig 'IncompleteConfig'"
    ):
        load_policy_from_file(file_path)


def test_load_commands_with_custom_policy(tmp_path):
    # --- Arrange ---

    # 1. Create a custom policy file
    policies_dir = tmp_path / ".fellow" / "policies"
    policies_dir.mkdir(parents=True)
    policy_file = policies_dir / "block_all.py"
    policy_file.write_text(
        textwrap.dedent(
            """
        from fellow.policies.Policy import Policy, PolicyConfig

        class BlockAllConfig(PolicyConfig):
            reason: str

        class BlockAll(Policy[BlockAllConfig]):
            def __init__(self, config):
                self.config = config
            def check(self, command_name, command_handler, args, context):
                return self.config.reason
    """
        )
    )

    # 2. Create a custom command file
    commands_dir = tmp_path / ".fellow" / "commands"
    commands_dir.mkdir(parents=True)
    command_file = commands_dir / "noop.py"
    command_file.write_text(
        textwrap.dedent(
            """
        from fellow.commands.Command import CommandInput, CommandContext
        from pydantic import Field

        class NoopInput(CommandInput):
            pass

        def noop(args: NoopInput, context: CommandContext) -> str:
            \"""
            A no-operation command that does nothing and returns 'OK'.
            \"""
            return "OK"
    """
        )
    )

    # 3. Create a config with policy and command
    config = SimpleNamespace(
        custom_policies_paths=[str(policies_dir)],
        custom_commands_paths=[str(commands_dir)],
        planning=SimpleNamespace(active=False),
        commands={
            "noop": SimpleNamespace(
                policies=[
                    SimpleNamespace(
                        name="block_all", config={"reason": "Access denied"}
                    )
                ]
            )
        },
        default_policies=[],
    )

    # --- Act ---
    commands = load_commands(config)

    # --- Assert ---
    assert "noop" in commands
    cmd = commands["noop"]
    assert len(cmd.policies) == 1
    denial_reason = cmd.policies[0].check("noop", None, SimpleNamespace(), None)
    assert denial_reason == "Access denied"


def test_load_commands_edge_cases(tmp_path, capsys):
    from types import SimpleNamespace

    from fellow.utils.load_commands import load_commands

    # --- Arrange ---
    # 1. Add an invalid custom policy file that raises import error
    bad_policies_dir = tmp_path / "bad_policies"
    bad_policies_dir.mkdir()
    (bad_policies_dir / "broken.py").write_text("this is not python")

    # 2. Add a valid policy file (BlockAll), which will be overridden
    good_policies_dir = tmp_path / "good_policies"
    good_policies_dir.mkdir()
    (good_policies_dir / "block_all.py").write_text(
        textwrap.dedent(
            """
        from fellow.policies.Policy import Policy, PolicyConfig

        class BlockAllConfig(PolicyConfig):
            reason: str

        class BlockAll(Policy[BlockAllConfig]):
            def __init__(self, config):
                self.config = config
            def check(self, command_name, command_handler, args, context):
                return self.config.reason
    """
        )
    )

    # 3. Add an overriding policy with the same name
    override_policy_file = good_policies_dir / "block_all_override.py"
    override_policy_file.write_text(
        textwrap.dedent(
            """
        from fellow.policies.Policy import Policy, PolicyConfig

        class BlockAllConfig(PolicyConfig):
            reason: str

        class BlockAll(Policy[BlockAllConfig]):
            def __init__(self, config):
                self.config = config
            def check(self, command_name, command_handler, args, context):
                return "overridden"
    """
        )
    )

    # 4. Add a overriding command with the same name
    command_dir = tmp_path / "commands"
    command_dir.mkdir()
    (command_dir / "view_file.py").write_text(
        textwrap.dedent(
            """
        from fellow.commands.Command import CommandInput, CommandContext
        from pydantic import Field

        class ViewFileInput(CommandInput):
            text: str = Field(...)

        def view_file(args: ViewFileInput, context: CommandContext):
            \"""
            Echo the input text.
            \"""
            return args.text
    """
        )
    )

    # 6. Add a policy with invalid config to trigger ValidationError
    invalid_config = {"wrong_field": True}

    config = SimpleNamespace(
        custom_policies_paths=[str(bad_policies_dir), str(good_policies_dir)],
        custom_commands_paths=[
            str(command_dir),
            str(tmp_path / "not_existing"),
        ],  # non-existing
        planning=SimpleNamespace(active=False),
        commands={
            "view_file": SimpleNamespace(
                policies=[SimpleNamespace(name="block_all", config=invalid_config)]
            ),
            "missing_command": SimpleNamespace(
                policies=[]
            ),  # not in ALL_COMMANDS or loaded
        },
        default_policies=[],
    )

    # --- Act + Assert ---
    with pytest.raises(ValueError) as e:
        load_commands(config)

    output = capsys.readouterr().out

    # Warnings and errors
    assert "[WARNING] Skipping" in output
    assert "[ERROR] Failed to load" in output
    assert "[INFO] Overriding built-in policy" in output
    print(output)
    assert "[INFO] Overriding built-in command" in output
    assert "Invalid configuration for policy 'block_all'" in str(
        e.value
    ) or "Command 'missing_command' not found" in str(e.value)


def test_load_command_with_default_policies(tmp_path: Path):
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
    config.commands = {
        "echo": MagicMock(policies=[]),
        "view_file": MagicMock(policies=[]),
    }
    config.default_policies = [
        SimpleNamespace(
            name="require_user_confirmation", config={"message": "Dont do that!"}
        )
    ]
    config.planning.active = True

    # Act
    commands = load_commands(config)

    # Assert
    assert isinstance(commands["echo"].policies[0], RequireUserConfirmation)
    assert commands["echo"].policies[0].config.message == "Dont do that!"
    assert isinstance(commands["view_file"].policies[0], RequireUserConfirmation)
    assert commands["view_file"].policies[0].config.message == "Dont do that!"
    assert isinstance(commands["make_plan"].policies[0], RequireUserConfirmation)
    assert commands["make_plan"].policies[0].config.message == "Dont do that!"
