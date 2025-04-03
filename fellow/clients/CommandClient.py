import json
from typing import Dict, Tuple, Type

from fellow.commands.command import CommandInput, CommandHandler, CommandContext


class CommandClient:
    def __init__(self, commands: Dict[str, Tuple[Type[CommandInput], CommandHandler]], context: CommandContext):
        """
        Initializes the CommandClient with a dictionary of commands.
        :param commands: A dictionary mapping command names to their input models and handler functions.
        :param context: The context in which the command will be executed, typically containing the AI client.
        """
        self.commands = commands
        self.context = context

    def run(self, command: dict) -> str:
        """
        Run a structured command given as a JSON string with one top-level key.
        """
        if not isinstance(command, dict) or len(command) != 1:
            return "[ERROR] Command must be a JSON object with exactly one top-level command key."

        cmd_name, cmd_args = next(iter(command.items()))

        if cmd_name not in self.commands:
            return f"[ERROR] Unknown command: {cmd_name}"

        input_model_cls, handler_fn = self.commands[cmd_name]

        if not isinstance(cmd_args, dict):
            return "[ERROR] Command arguments must be an object."

        try:
            args_obj: CommandInput = input_model_cls(**cmd_args)
        except Exception as e:
            return f"[ERROR] Invalid command arguments: {e}"

        try:
            return handler_fn(args_obj, context=self.context)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"
