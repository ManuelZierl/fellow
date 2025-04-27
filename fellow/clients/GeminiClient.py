import json
import os
from typing import TYPE_CHECKING, List, Optional, Union

# todo: todo: follow: https://github.com/googleapis/python-genai/issues/61
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from google.genai.types import Part  # type: ignore
from typing_extensions import Self

from fellow.clients.Client import (
    ChatResult,
    Client,
    ClientConfig,
    Function,
    FunctionResult,
)

if TYPE_CHECKING:
    from fellow.commands.Command import Command


class GeminiClientConfig(ClientConfig):
    system_content: str
    model: str  # = "gemini-1.5-flash"


class GeminiClient(Client[GeminiClientConfig]):
    config_class = GeminiClientConfig

    # todo: implement summarization for token optimization
    def __init__(self, config: GeminiClientConfig):
        if os.environ.get("GEMINI_API_KEY") is None:
            raise ValueError("[ERROR] GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.client_chat = self.client.chats.create(model=config.model)

    @classmethod
    def create(cls, config: GeminiClientConfig) -> Self:
        return cls(config)

    def chat(
        self,
        functions: List[Function],
        message: str = "",
        function_result: Optional[FunctionResult] = None,
    ) -> ChatResult:
        tools = types.Tool(function_declarations=functions)
        config = types.GenerateContentConfig(tools=[tools])

        if function_result:
            msg: Union[Part, str] = Part.model_validate(
                {
                    "function_response": {
                        "name": function_result["name"],
                        "response": {"output": function_result["output"]},
                    }
                }
            )
        else:
            msg = message

        response = self.client_chat.send_message(
            message=msg,
            config=config,
        )
        function_args: Optional[str] = None
        function_name: Optional[str] = None
        if response.function_calls:
            if response.function_calls[0].name:
                function_name = response.function_calls[0].name
            if response.function_calls[0].args:
                function_args = json.dumps(response.function_calls[0].args)

        return ChatResult(
            message=response.text,
            function_name=function_name,
            function_args=function_args,
        )

    def store_memory(self, filename: str) -> None:
        history: List[types.Content] = self.client_chat.get_history()
        history_dicts = [item.model_dump() for item in history]
        with open(filename, "w") as f:  # noinspection PyTypeChecker
            json.dump(history_dicts, f, indent=2)

    def set_plan(self, plan: str) -> None:
        # todo. this can be optimized with summarization implementation
        # todo: test
        self.client_chat.send_message(
            message=plan,
        )

    def get_function_schema(self, command: "Command") -> Function:
        if not hasattr(command.command_handler, "__name__"):
            raise ValueError("[ERROR] Command handler is not callable with __name__.")
        if command.command_handler.__doc__ is None:
            raise ValueError("[ERROR] Command handler is __doc__ is empty")
        name = command.command_handler.__name__
        description = command.command_handler.__doc__.strip()
        parameters = command.input_type.model_json_schema()
        del parameters["title"]
        for param_name, param in parameters["properties"].items():
            if "title" in param:
                del param["title"]
            if "default" in param:
                del param["default"]
            any_of = param.get("anyOf")
            if any_of:
                if len(any_of) == 1:
                    param["type"] = any_of[0]["type"]
                elif len(any_of) == 2:
                    # Handle type: ["integer", "null"] → Gemini doesn't support it
                    if any_of[0]["type"] == "null":
                        param["type"] = any_of[1]["type"]
                    elif any_of[1]["type"] == "null":
                        param["type"] = any_of[0]["type"]
                    else:
                        param["anyOf"] = any_of
                else:
                    raise ValueError(
                        f"Unsupported anyOf length: {len(any_of)} for parameter {param_name}, Gemini does not support it."
                    )
                del param["anyOf"]
        return {
            "name": name,
            "description": description,
            "parameters": parameters,
        }
