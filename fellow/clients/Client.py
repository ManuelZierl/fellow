from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Protocol,
    Type,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

from openai import BaseModel
from typing_extensions import Required, Self

if TYPE_CHECKING:
    from fellow.commands.Command import Command


class ChatResult(TypedDict):
    message: Optional[str]
    """
    The assistant's textual response, if available
    """

    function_name: Optional[str]
    """
    The name of a function the assistant wants to call, if applicable.
    """

    function_args: Optional[str]
    """
    The arguments for the function call (as JSON/dict), if any.
    """


class FunctionResult(TypedDict):
    name: Required[str]
    """
    The name of the function that was called.
    """

    output: Required[str]
    """
    The return value of the function as a string.
    """


class Function(TypedDict, total=False):
    name: Required[str]
    """
    The name of the function.
    """

    description: str
    """
    A explanation of what the function does.
    """

    parameters: Dict[str, object]
    """
    JSON schema for the function's expected arguments.
    """


class ClientConfig(BaseModel):
    system_content: str
    """
    The system content that will be used to configure the AI client.
    """


T = TypeVar("T", bound=ClientConfig)


@runtime_checkable
class Client(Protocol[T]):
    """
    Abstract interface for AI backend clients (e.g., OpenAI, Gemini, Claude).

    Implementations of this protocol are responsible for managing memory,
    communicating with the model, and optionally handling function calling.
    """

    config_class: Type[T]

    @classmethod
    def create(cls, config: T) -> Self:
        """
        Creates and returns a configured instance of the AI client.

        :param config: Configuration with model-specific parameters.

        :return: A configured AI client instance.
        """
        ...

    def chat(
        self,
        functions: List[Function],
        message: str = "",
        function_result: Optional[FunctionResult] = None,
    ) -> ChatResult:
        """
        Sends a message to the AI and optionally provides function results.
        Returns a ChatResult that may include a response or function call.

        :param functions: List of function schemas for the model to call.
        :param message: User input message.
        :param function_result: Function result of previous function call, if any.

        :return: ChatResult containing the assistant's response, function name, and arguments.
        """
        ...

    def store_memory(self, filename: str) -> None:
        """
        Writes the entire interaction history to a file.

        :param filename: The name of the file to store memory.
        """
        ...

    def set_plan(self, plan: str) -> None:
        """
        Sets the plan for the AI to follow in future interactions.

        :param plan: The plan to be set.
        """
        ...

    def get_function_schema(self, command: "Command") -> Function:
        """
        Returns the function schema for a given command for this client.

        :param command: The command for which to get the function schema.
        """
        ...
