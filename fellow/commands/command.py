import json
from typing import Protocol, Type, TypeVar

from openai.types.chat.completion_create_params import Function
from pydantic import BaseModel, ConfigDict, ValidationError

from fellow.clients.OpenAIClient import OpenAIClient


class CommandContext(
    BaseModel
):  # todo: Typed dict might be better becuase we do no validation
    ai_client: OpenAIClient

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CommandInput(BaseModel): ...


T = TypeVar("T", bound=CommandInput, contravariant=True)


class CommandHandler(Protocol[T]):
    def __call__(self, args: T, context: CommandContext) -> str: ...


class Command:
    def __init__(self, input_type: Type[CommandInput], command_handler: CommandHandler):
        self.input_type = input_type
        self.command_handler = command_handler

    def openai_schema(self) -> Function:
        if not hasattr(self.command_handler, "__name__"):
            raise ValueError("[ERROR] Command handler is not callable with __name__.")
        if self.command_handler.__doc__ is None:
            raise ValueError("[ERROR] Command handler is __doc__ is empty")
        return {
            "name": self.command_handler.__name__,
            "description": self.command_handler.__doc__,
            "parameters": self.input_type.model_json_schema(),
        }

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
