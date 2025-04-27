import json
from typing import Protocol, Type, TypedDict, TypeVar

from pydantic import BaseModel, ValidationError

from fellow.clients.Client import Client
from fellow.utils.load_config import Config


class CommandContext(TypedDict):
    ai_client: Client
    config: Config


class CommandInput(BaseModel): ...


T = TypeVar("T", bound=CommandInput, contravariant=True)


class CommandHandler(Protocol[T]):
    def __call__(self, args: T, context: CommandContext) -> str: ...


class Command:
    def __init__(self, input_type: Type[CommandInput], command_handler: CommandHandler):
        self.input_type = input_type
        self.command_handler = command_handler

    def run(self, command_input_str: str, context: CommandContext) -> str:
        try:
            command_input = self.input_type(**json.loads(command_input_str))
        except ValidationError as e:
            if not hasattr(self.command_handler, "__name__"):
                raise ValueError(
                    "[ERROR] Command handler is not callable with __name__."
                )
            return (
                f"[ERROR] Invalid command input [{self.command_handler.__name__}]: "
                + str(e)
            )

        try:
            return self.command_handler(command_input, context=context)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"
