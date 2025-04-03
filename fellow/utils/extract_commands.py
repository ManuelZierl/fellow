import json
from typing import Any, List, Tuple, Dict, Type, Union
from fellow.commands import CommandInput, CommandHandler


def extract_json_objects(text: str) -> List[Any]:
    """Extract all JSON blocks from messy text."""
    json_blocks = []
    brace_stack = []
    start_idx = None

    for i, char in enumerate(text):
        if char == '{':
            if not brace_stack:
                start_idx = i
            brace_stack.append('{')
        elif char == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    try:
                        block = text[start_idx:i + 1]
                        parsed = json.loads(block)
                        json_blocks.append(parsed)
                    except json.JSONDecodeError:
                        pass
                    start_idx = None
    return json_blocks


def flatten_command_dicts(blocks: List[Any]) -> List[dict]:
    commands = []
    for block in blocks:
        if isinstance(block, dict):
            if "commands" in block:
                if isinstance(block["commands"], list):
                    for sub in block["commands"]:
                        if isinstance(sub, dict):
                            commands.append(sub)
                else:
                    continue  # skip malformed 'commands' block
            else:
                commands.append(block)
        elif isinstance(block, list):
            for item in block:
                if isinstance(item, dict):
                    commands.append(item)
    return commands


def extract_commands(
    response: str,
    commands: Dict[str, Tuple[Type[CommandInput], CommandHandler]]
) -> Union[List[Tuple[CommandInput, CommandHandler]], str]:
    """
    Parses commands from AI response, validates them, and returns command inputs with handlers.
    """
    blocks = extract_json_objects(response)
    raw_cmds = flatten_command_dicts(blocks)
    results: List[Tuple[CommandInput, CommandHandler]] = []

    for cmd_dict in raw_cmds:
        if not isinstance(cmd_dict, dict) or len(cmd_dict) != 1:
            continue  # or collect as error

        cmd_name, cmd_args = next(iter(cmd_dict.items()))

        if cmd_name not in commands:
            return f"[ERROR] Unknown command: {cmd_name}"

        input_model_cls, handler_fn = commands[cmd_name]

        if not isinstance(cmd_args, dict):
            return "[ERROR] Command arguments must be an object."

        try:
            args_obj = input_model_cls(**cmd_args)
        except Exception as e:
            return f"[ERROR] Invalid command arguments for '{cmd_name}': {e}"

        results.append((args_obj, handler_fn))

    return results
