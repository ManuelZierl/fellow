import json
import os
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Tuple, TypedDict

import openai
import tiktoken
from openai import NOT_GIVEN
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
)
from openai.types.chat.chat_completion_assistant_message_param import FunctionCall
from typing_extensions import Required, Self

from fellow.clients.Client import (
    ChatResult,
    Client,
    ClientConfig,
    Function,
    FunctionResult,
)

if TYPE_CHECKING:
    from fellow.commands.Command import Command


class OpenAIClientMessage(TypedDict, total=False):
    role: Required[Literal["user", "assistant", "function", "system"]]
    tokens: Required[int]
    content: str
    name: str
    function_call: FunctionCall


class OpenAIClientConfig(ClientConfig):
    """
    Configuration for OpenAIClient.
    """

    system_content: str
    memory_max_tokens: int
    summary_memory_max_tokens: int
    model: str


class OpenAIClient(Client[OpenAIClientConfig]):
    config_class = OpenAIClientConfig

    def __init__(self, config: OpenAIClientConfig):
        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError("[ERROR] OPENAI_API_KEY environment variable is not set.")
        self.memory_max_tokens = config.memory_max_tokens
        self.summary_memory_max_tokens = config.summary_memory_max_tokens
        self.model = config.model
        self.system_content: List[OpenAIClientMessage] = [
            {
                "role": "system",
                "content": config.system_content,
                "tokens": self._count_tokens(
                    {"role": "system", "content": config.system_content}
                ),
            }
        ]
        self.summary_memory: List[OpenAIClientMessage] = []
        self.memory: List[OpenAIClientMessage] = []

    @classmethod
    def create(cls, config: OpenAIClientConfig) -> Self:
        return cls(config)

    def message_to_params(self) -> List[ChatCompletionMessageParam]:
        """
        Converts internal message history into OpenAI-compatible ChatCompletionMessageParams.
        Handles 'user', 'assistant', and 'function' roles with the appropriate fields.

        :return: A list of ChatCompletionMessageParam dicts for API input.
        """
        messages = self.messages()
        output: List[ChatCompletionMessageParam] = []

        for message in messages:
            if message["role"] == "function":
                output.append(
                    {
                        "role": message["role"],
                        "name": message["name"],
                        "content": message["content"],
                    }
                )
            if message["role"] == "user":
                output.append({"role": message["role"], "content": message["content"]})
            if message["role"] == "assistant":
                assistant_message: ChatCompletionAssistantMessageParam = {
                    "role": "assistant",
                }
                if "content" in message:
                    assistant_message["content"] = message["content"]
                if "function_call" in message:
                    assistant_message["function_call"] = message["function_call"]
                output.append(assistant_message)
            if message["role"] == "system":
                system_message: ChatCompletionMessageParam = {
                    "role": message["role"],
                    "content": message["content"],
                }
                output.append(system_message)
        return output

    def messages(self) -> List[OpenAIClientMessage]:
        """
        Returns the full message history, optionally without token count.

        :return: List of message OpenAIClientMessages.
        """
        return self.system_content + self.summary_memory + self.memory

    def chat(
        self,
        functions: List[Function],
        message: str = "",
        function_result: Optional[FunctionResult] = None,
    ) -> ChatResult:
        """
        Sends a message or a function result to the model, can also handle function calls.
        Updates memory, and handles summarization if token limits are exceeded.

        :param message: User input message.
        :param function_result: Tuple of function name and output if a function was called.
        :param functions: List of function schemas for the model to call.

        :return: Tuple containing the assistant's response, function name, and function arguments.
        """
        new_msg: OpenAIClientMessage
        if function_result:
            fn_name, fn_output = function_result["name"], function_result["output"]
            new_msg = {
                "role": "function",
                "name": fn_name,
                "content": fn_output,
                "tokens": self._count_tokens(
                    {"role": "function", "content": fn_output}
                ),
            }
            self.memory.append(new_msg)
        else:
            if message.strip():
                new_msg = {
                    "role": "user",
                    "content": message,
                    "tokens": self._count_tokens({"role": "user", "content": message}),
                }
                self.memory.append(new_msg)

        response = openai.chat.completions.create(
            model=self.model,
            messages=self.message_to_params(),
            functions=functions,
            function_call="auto" if functions else NOT_GIVEN,
        )

        msg = response.choices[0].message
        function_call: Optional[FunctionCall] = (
            {"name": msg.function_call.name, "arguments": msg.function_call.arguments}
            if msg.function_call
            else None
        )
        self._append_input_to_memory(msg.content, function_call)

        # Perform summarization if needed
        self._maybe_summarize_memory()

        if msg.function_call:
            return {
                "message": msg.content,
                "function_name": msg.function_call.name,
                "function_args": msg.function_call.arguments,
            }
        else:
            return {
                "message": msg.content,
                "function_name": None,
                "function_args": None,
            }

    def store_memory(self, filename: str):
        """
        Saves the full message history (including token counts) to a JSON file.

        :param filename: Path to the file where the memory will be stored.
        """
        with open(filename, "w") as f:  # noinspection PyTypeChecker
            json.dump(self.messages(), f, indent=2)

    def set_plan(self, plan: str) -> None:
        """
        Adds a system message to the memory with the specified plan.

        :param plan: The plan to be set.
        """
        self.system_content.append(
            {
                "role": "system",
                "content": plan,
                "tokens": self._count_tokens({"role": "system", "content": plan}),
            }
        )

    def get_function_schema(self, command: "Command") -> Function:
        if not hasattr(command.command_handler, "__name__"):
            raise ValueError("[ERROR] Command handler is not callable with __name__.")
        if command.command_handler.__doc__ is None:
            raise ValueError("[ERROR] Command handler is __doc__ is empty")
        return {
            "name": command.command_handler.__name__,
            "description": command.command_handler.__doc__.strip(),
            "parameters": command.input_type.model_json_schema(),
        }

    def _count_tokens(self, message: Dict) -> int:
        """
        Estimates the number of tokens a single message will consume when sent to the OpenAI API.

        This method uses the tiktoken encoder for the specified model to calculate the token count of the message's content.
        It also includes a fixed overhead to account for message formatting according to the ChatML format used by OpenAI.

        Token accounting:
        - 4 tokens are added for structural elements: role, name, delimiters.
        - The actual content tokens are computed using the tokenizer.
        - 2 additional tokens are added to account for priming tokens (<|start|> and <|end|>) commonly applied in ChatML.

        :param message: A dictionary representing a chat message with at least a 'content' field.
        :return: Estimated total number of tokens used by the message.

        # todo: do model aware priming
        """
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 4
        num_tokens += len(encoding.encode(message.get("content", "")))
        return num_tokens + 2

    def _append_input_to_memory(
        self,
        message: Optional[str] = None,
        function_call: Optional[FunctionCall] = None,
    ):
        """
        Appends an assistant message or function call to the memory with token count.

        - If `message` is provided, it is stored as an assistant's textual response.
        - If `function_call` is provided, it is stored as an assistant function invocation.

        This ensures that all assistant outputs, whether text or tool calls, are tracked
        and contribute to token-based summarization logic.
        """
        # Handle assistant reasoning
        if message:
            self.memory.append(
                {
                    "role": "assistant",
                    "content": message,
                    "tokens": self._count_tokens(
                        {"role": "assistant", "content": message}
                    ),
                }
            )

        # Handle function call
        if function_call:
            arguments = function_call["arguments"]
            self.memory.append(
                {
                    "role": "assistant",
                    "function_call": {
                        "name": function_call["name"],
                        "arguments": arguments,
                    },
                    "tokens": self._count_tokens(
                        {
                            "role": "assistant",
                            "content": f"[Function call] {function_call['name']}({arguments})",
                        }
                    ),
                }
            )

    def _maybe_summarize_memory(self):
        """
        Summarizes memory or summary memory if their token limits are exceeded.

        If `self.memory` exceeds `memory_max_tokens`, it is split and the older part summarized.
        The resulting summary is appended to `summary_memory`.

        If `summary_memory` exceeds `summary_memory_max_tokens`, it too is summarized recursively
        """
        memory_tokens = sum([message["tokens"] for message in self.memory])
        if memory_tokens > self.memory_max_tokens:
            old_memory, self.memory = self._split_on_token_limit(
                self.memory, self.memory_max_tokens
            )
            summary = self._summarize_memory(old_memory)
            summary_content = "Summary of previous conversation: " + summary
            self.summary_memory.append(
                {
                    "role": "system",
                    "content": summary_content,
                    "tokens": self._count_tokens(
                        {"role": "system", "content": summary_content}
                    ),
                }
            )

        summary_memory_tokens = sum(
            [message["tokens"] for message in self.summary_memory]
        )
        if summary_memory_tokens > self.summary_memory_max_tokens:
            old_summary_memory, self.summary_memory = self._split_on_token_limit(
                self.summary_memory, self.summary_memory_max_tokens
            )
            summary = self._summarize_memory(old_summary_memory)
            summary_content = "Summary of previous conversation: " + summary
            self.summary_memory.append(
                {
                    "role": "system",
                    "content": summary_content,
                    "tokens": self._count_tokens(
                        {"role": "system", "content": summary_content}
                    ),
                }
            )

    def _summarize_memory(self, messages: List[OpenAIClientMessage]) -> str:
        """
        Uses the OpenAI API to summarize a list of chat messages for context compression.

        :param messages: List of messages to summarize.
        :return: Summary string generated by the model.
        """

        def stringify(msg: OpenAIClientMessage) -> str:
            role = msg["role"].capitalize()
            parts = []

            if msg.get("content"):
                parts.append(msg["content"])

            if "function_call" in msg:
                fc = msg["function_call"]
                parts.append(f"[Function call] {fc['name']}({fc['arguments']})")

            return f"{role}: {' | '.join(parts) if parts else '[No content]'}"

        summary_prompt: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "Summarize the following conversation for context retention.",
            },
            {"role": "user", "content": "\n".join(stringify(m) for m in messages)},
        ]

        response = openai.chat.completions.create(
            model=self.model,
            messages=summary_prompt,
            # todo: this could optionally use a different less expensive model, because summarization is not as difficult
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _split_on_token_limit(
        messages: List[Dict], token_limit: int
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Splits the messages into two lists based on the token limit. `second` will contain the *last* messages
        that fit into the token limit. `first` will contain all earlier messages.

        :param messages: List of messages to split
        :param token_limit: token limit for the split
        :return: (first, second)
        """
        token_count = 0
        for i in range(len(messages) - 1, -1, -1):
            token_count += messages[i]["tokens"]
            if token_count > token_limit:
                return messages[: i + 1], messages[i + 1 :]
        return [], messages
