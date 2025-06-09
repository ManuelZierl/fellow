import inspect
import re
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional, Tuple, Type, TypeVar, cast

from pydantic import ValidationError

from fellow.commands import ALL_COMMANDS
from fellow.commands.Command import Command, CommandHandler, CommandInput
from fellow.policies import ALL_POLICIES
from fellow.policies.Policy import Policy, PolicyConfig
from fellow.utils.load_config import CommandConfig, Config
from fellow.utils.load_python_module import load_python_module

T = TypeVar("T", bound=CommandInput)
U = TypeVar("U")
CommandTuple = Tuple[Type[T], CommandHandler[T]]


def load_commands(config: Config) -> Dict[str, Command]:
    """
    Loads all commands for Fellow, including built-in and custom ones,
    and attaches configured policies.

    Custom commands and policies from configured paths override built-ins.
    Commands not listed in the config are excluded. If planning is enabled,
    a default planning command is added.

    :param config: Configuration object containing paths and command definitions.
    :return: A dictionary mapping command names to Command objects.
    """
    custom_policies_map: Dict[str, Tuple[Type[Policy], Type[PolicyConfig]]] = (
        ALL_POLICIES.copy()
    )

    for path_str in config.custom_policies_paths:
        path = Path(path_str).resolve()
        if not path.exists() or not path.is_dir():
            print(f"[WARNING] Skipping {path_str}: not a valid directory.")
            continue

        for file in path.glob("*.py"):
            try:
                policy_name, policy_type, policy_config_type = load_policy_from_file(
                    file
                )
            except Exception as e:
                print(f"[ERROR] Failed to load {file}: {e}")
                continue

            # warn on override
            if policy_name in custom_policies_map:
                print(f"[INFO] Overriding built-in policy: {policy_name}")

            custom_policies_map[policy_name] = (policy_type, policy_config_type)

    custom_commands_map: Dict[str, CommandTuple] = ALL_COMMANDS.copy()

    for path_str in config.custom_commands_paths:
        path = Path(path_str).resolve()
        if not path.exists() or not path.is_dir():
            print(f"[WARNING] Skipping {path_str}: not a valid directory.")
            continue

        for file in path.glob("*.py"):
            try:
                command_name, command_input, command_handler = load_command_from_file(
                    file
                )
            except Exception as e:
                print(f"[ERROR] Failed to load {file}: {e}")
                continue

            # warn on override
            if command_name in custom_commands_map:
                print(f"[INFO] Overriding built-in command: {command_name}")

            custom_commands_map[command_name] = (command_input, command_handler)

    final_commands: Dict[str, Command] = {}

    # Add make_plan command if planning is active
    if (
        config.planning.active
        and "make_plan" in ALL_COMMANDS
        and "make_plan" not in config.commands
    ):
        make_plan_input, make_plan_handler = ALL_COMMANDS["make_plan"]
        config.commands["make_plan"] = CommandConfig()

    # Filter only the ones listed in config.commands
    for command_name, command_config in config.commands.items():
        policies = []
        for p in command_config.policies + config.default_policies:
            policy_name = p.name
            policy_config_dict = p.config
            custom_policy_type, custom_policy_config_type = custom_policies_map[
                policy_name
            ]
            try:
                policy_config = custom_policy_config_type.model_validate(
                    policy_config_dict
                )
            except ValidationError as e:
                raise ValueError(
                    f"Invalid configuration for policy '{policy_name}': {e}"
                ) from e
            policy = custom_policy_type(policy_config)
            policies.append(policy)

        if command_name in custom_commands_map:
            command_input, command_handler = custom_commands_map[command_name]
            final_commands[command_name] = Command(
                input_type=command_input,
                command_handler=command_handler,
                policies=policies,
            )
        else:
            raise ValueError(
                f"Command '{command_name}' not found in built-in or custom commands."
            )
    return final_commands


def load_command_from_file(
    file_path: Path,
) -> Tuple[str, Type[CommandInput], CommandHandler[CommandInput]]:
    """
    Load a command from a file, inferring CommandInput and handler by convention:
    - File must define one subclass of CommandInput
    - File must define a function with the same name as the file (e.g. echo.py → def echo)
    - Function must have 2 args and a docstring

    :param file_path: Path to the command file.
    :return: A tuple containing the command name, input type, and handler function.
    """
    module = load_python_module(file_path)

    input_type = _find_class_in_module(module, CommandInput)
    expected_fn_name = file_path.stem
    handler: CommandHandler[CommandInput] = cast(
        CommandHandler[CommandInput], getattr(module, expected_fn_name, None)
    )

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
    return expected_fn_name, input_type, handler


def load_policy_from_file(
    file_path: Path,
) -> Tuple[str, Type[Policy], Type[PolicyConfig]]:
    """
    Loads a policy and its corresponding config class from a Python file.

    The file must define:
    - A subclass of `PolicyConfig` (e.g., `MyPolicyConfig`)
    - A `Policy` class with the same name as the config, minus the "Config" suffix (e.g., `MyPolicy`)

    The policy name is inferred from the class name and converted to snake_case.

    :param file_path: Path to the .py file containing the policy definition.
    :return: A tuple of (policy_name, policy class, policy config class).
    """
    module = load_python_module(file_path)

    policy_config_type = _find_class_in_module(module, PolicyConfig)
    if policy_config_type is None:
        raise ValueError(
            f"[ERROR] No subclass of PolicyConfig found in {file_path.name}"
        )
    policy_type = getattr(module, policy_config_type.__name__.rstrip("Config"), None)
    if policy_type is None:
        raise ValueError(
            f"[ERROR] No class found matching PolicyConfig '{policy_config_type.__name__}' in {file_path.name}"
        )

    policy_name = re.sub(r"(?<!^)(?=[A-Z])", "_", policy_type.__name__).lower()
    return policy_name, policy_type, policy_config_type


def _find_class_in_module(module: ModuleType, class_type: Type[U]) -> Optional[Type[U]]:
    for obj in vars(module).values():
        if (
            inspect.isclass(obj)
            and issubclass(obj, class_type)
            and obj is not class_type
        ):
            return obj
    return None
