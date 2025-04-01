import json

from fellow.commands import COMMANDS
from fellow.commands.command import CommandInput


class CommandClient:
    @staticmethod
    def run(command: str) -> str:
        """
        Run a structured command given as a JSON string with one top-level key.
        """
        try:
            parsed = json.loads(command)
        except json.JSONDecodeError as e:
            return f"[ERROR] Invalid JSON: {e}"

        if not isinstance(parsed, dict) or len(parsed) != 1:
            return "[ERROR] Command must be a JSON object with exactly one top-level command key."

        cmd_name, cmd_args = next(iter(parsed.items()))

        if cmd_name not in COMMANDS:
            return f"[ERROR] Unknown command: {cmd_name}"

        input_model_cls, handler_fn = COMMANDS[cmd_name]

        if not isinstance(cmd_args, dict):
            return "[ERROR] Command arguments must be an object."

        try:
            args_obj: CommandInput = input_model_cls(**cmd_args)
        except Exception as e:
            return f"[ERROR] Invalid command arguments: {e}"

        try:
            return handler_fn(args_obj)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"
