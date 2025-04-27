import inspect
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional, Tuple

from fellow.commands import ALL_COMMANDS
from fellow.commands.Command import Command, CommandInput
from fellow.utils.load_config import Config
from fellow.utils.load_python_module import load_python_module


def load_commands(config: Config) -> Dict[str, Command]:
    """
    Loads all commands for Fellow:
    - Built-in commands from ALL_COMMANDS
    - Custom commands from .fellow/commands or paths defined in config
    Custom commands override built-in ones if name matches.
    """
    commands_map: Dict[str, Command] = ALL_COMMANDS.copy()

    for path_str in config.custom_commands_paths:
        path = Path(path_str).resolve()
        if not path.exists() or not path.is_dir():
            print(f"[WARNING] Skipping {path_str}: not a valid directory.")
            continue

        for file in path.glob("*.py"):
            try:
                command_name, command = load_command_from_file(file)
            except Exception as e:
                print(f"[ERROR] Failed to load {file}: {e}")
                continue

            if not isinstance(command, Command):
                print(
                    f"[WARNING] Skipping {file.name}: `command` is not a valid Command instance."
                )
                continue

            # Optional: warn on override
            if command_name in commands_map:
                print(f"[INFO] Overriding built-in command: {command_name}")

            commands_map[command_name] = command

    # Filter only the ones listed in config.commands
    final_commands: Dict[str, Command] = {}
    for name in config.commands:
        if name in commands_map:
            final_commands[name] = commands_map[name]
        else:
            raise ValueError(
                f"Command '{name}' not found in built-in or custom commands."
            )

    # Optionally add planning command
    if config.planning.active and "make_plan" in ALL_COMMANDS:
        final_commands["make_plan"] = ALL_COMMANDS["make_plan"]

    return final_commands


def load_command_from_file(file_path: Path) -> Tuple[str, Command]:
    """
    Load a command from a file, inferring CommandInput and handler by convention:
    - File must define one subclass of CommandInput
    - File must define a function with the same name as the file (e.g. echo.py → def echo)
    - Function must have 2 args and a docstring
    """
    module = load_python_module(file_path)

    input_type = _find_command_input_class(module)
    expected_fn_name = file_path.stem
    handler = getattr(module, expected_fn_name, None)

    if input_type is None:
        raise ValueError(
            f"[ERROR] No subclass of CommandInput found in {file_path.name}"
        )

    if handler is None or not callable(handler):
        raise ValueError(
            f"[ERROR] No function named '{expected_fn_name}' found in {file_path.name}"
        )

    # Basic validation
    sig = inspect.signature(handler)
    if len(sig.parameters) != 2:
        raise ValueError(
            f"[ERROR] Function '{expected_fn_name}' must take two arguments: (args, context)"
        )
    if not handler.__doc__:
        raise ValueError(
            f"[ERROR] Function '{expected_fn_name}' must have a docstring."
        )

    command = Command(input_type, handler)
    return expected_fn_name, command


def _find_command_input_class(module: ModuleType) -> Optional[type[CommandInput]]:
    for obj in vars(module).values():
        if (
            inspect.isclass(obj)
            and issubclass(obj, CommandInput)
            and obj is not CommandInput
        ):
            return obj
    return None
