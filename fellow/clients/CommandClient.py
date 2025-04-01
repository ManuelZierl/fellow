import json
from typing import Dict, Tuple, Type

from fellow.clients.OpenAIClient import OpenAIClient
from fellow.commands.command import CommandInput, CommandHandler


class CommandClient:
    def __init__(self, commands: Dict[str, Tuple[Type[CommandInput], CommandHandler]], ai_client: OpenAIClient):
        """
        Initializes the CommandClient with a dictionary of commands.
        :param commands: A dictionary mapping command names to their input models and handler functions.
        :param ai_client: An instance of OpenAIClient for AI interactions.
        """
        self.commands = commands
        self.ai_client = ai_client

    def run(self, command: str) -> str:
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
            return handler_fn(args_obj)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"
