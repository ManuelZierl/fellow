import json
from typing import List, Protocol, Type, TypedDict, TypeVar

from pydantic import BaseModel, ValidationError

from fellow.clients.Client import Client
from fellow.policies.Policy import Policy
from fellow.utils.load_config import Config


class CommandContext(TypedDict):
    ai_client: Client
    config: Config


class CommandInput(BaseModel): ...


T = TypeVar("T", bound=CommandInput, contravariant=True)


class CommandHandler(Protocol[T]):
    def __call__(self, args: T, context: CommandContext) -> str: ...


class Command:
    def __init__(
        self,
        input_type: Type[CommandInput],
        command_handler: CommandHandler,
        policies: List[Policy],
    ):
        self.input_type = input_type
        self.command_handler = command_handler
        self.policies = policies

    def run(self, command_input_str: str, context: CommandContext) -> str:
        """
        Executes the command with validated input and enforced policies.

        Steps:
        1. Parses and validates the input JSON string against the command's `input_type`.
        2. Ensures the command handler is a named function (not a lambda).
        3. Runs all attached policies; if any return a denial reason, the command is aborted.
        4. If all policies pass, invokes the command handler.
        5. Returns the handler's output or an error message if execution fails.

        :param command_input_str: JSON string representing command input fields.
        :param context: Runtime context for the command (e.g. environment, memory, etc.).
        :return: Result of the command execution as a string, or an error message.
        """
        try:
            command_input = self.input_type(**json.loads(command_input_str))
            if (
                not hasattr(self.command_handler, "__name__")
                or getattr(self.command_handler, "__name__") == "<lambda>"
            ):
                raise ValueError(
                    "[ERROR] Command handler cannot be anonymous function or lambda."
                )
        except ValidationError as e:
            return (
                f"[ERROR] Invalid command input [{getattr(self.command_handler, '__name__', '<anonymous>')}]: "
                + str(e)
            )

        for policy in self.policies:
            result = policy.check(
                self.command_handler.__name__,
                self.command_handler,
                command_input,
                context,
            )
            if isinstance(result, str):
                return f"[ERROR] {policy.__class__.__name__} denied command: {result}"
            if result is not True:
                raise ValueError(
                    "[ERROR] Policy check did not return True but did not give a denial reason."
                )

        try:
            return self.command_handler(command_input, context=context)
        except Exception as e:
            return f"[ERROR] Command execution failed: {e}"
