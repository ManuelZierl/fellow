import json
import os
from typing import List, Optional

# todo: todo: follow: https://github.com/googleapis/python-genai/issues/61
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from typing_extensions import Self

from fellow.clients.Client import (
    ChatResult,
    Client,
    ClientConfig,
    Function,
    FunctionResult,
)


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
            msg = function_result["output"]
        else:
            msg = message

        # response = self.chat_session.send_message(msg)
        response = self.client_chat.send_message(
            message=msg,
            config=config,
        )

        function_name: Optional[str] = response.function_calls[0].name
        function_args: Optional[str] = None
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
