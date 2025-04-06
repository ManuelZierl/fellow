import json
from typing import Dict, List, Tuple, Optional

import openai
import tiktoken
from openai import NOT_GIVEN, NotGiven
from openai.types.chat import ChatCompletionMessage


class OpenAIClient:
    def __init__(
            self,
            system_content: str,
            memory_max_tokens: int=15000,
            summary_memory_max_tokens: int=15000,
            model:str ="gpt-4o"
    ):
        """
        Initializes the OpenAIClient with system content prompt, token limits, and model configuration.

        :param system_content: Initial system message to guide the assistant's behavior.
        :param memory_max_tokens: Max tokens allowed in message memory before summarization.
        :param summary_memory_max_tokens: Max tokens allowed in summarized memory before re-summarizing.
        :param model: OpenAI model name to use for completions.
        """
        self.memory_max_tokens = memory_max_tokens
        self.summary_memory_max_tokens = summary_memory_max_tokens
        self.model = model
        self.system_content = [
            {
                "role": "system",
                "content": system_content,
                "tokens": self.count_tokens({"role": "system", "content": system_content})
            }
        ]
        self.summary_memory = []
        self.memory = []

    def messages(self, remove_tokens: bool) -> List[Dict]:
        """
        Returns the full message history, optionally without token count.

        :param remove_tokens: If True, strips 'tokens' field from each message.
        :return: List of message dicts.
        """
        messages = self.system_content + self.summary_memory + self.memory
        if remove_tokens:
            return [
                {
                    "role": message["role"],
                    "content": message["content"]
                } for message in messages
            ]
        return messages

    def chat(
            self,
            message: str = "",
            function_result: Optional[Tuple[str, str]] = None,
            functions: Optional[List[Dict]] = None
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Sends a message or a function result to the model, can also handle function calls.
        Updates memory, and handles summarization if token limits are exceeded.

        :param message: User input message.
        :param function_result: Tuple of function name and output if a function was called.
        :param functions: List of function schemas for the model to call.

        :return: Tuple containing the assistant's response, function name, and function arguments.
        """

        if function_result:
            fn_name, fn_output = function_result
            new_msg = {
                "role": "function",
                "name": fn_name,
                "content": fn_output,
                "tokens": self.count_tokens({"role": "function", "content": fn_output})
            }
            self.memory.append(new_msg)
        else:
            if message.strip() == "":
                new_msg = {
                    "role": "user",
                    "content": message,
                    "tokens": self.count_tokens({"role": "user", "content": message})
                }
                self.memory.append(new_msg)


        response = openai.chat.completions.create(
            model=self.model,
            messages=self.messages(remove_tokens=True),
            functions=functions,
            function_call="auto" if functions else None
        )

        choice = response.choices[0]
        msg = choice.message

        # Handle assistant reasoning
        if msg.content:
            self.memory.append({
                "role": "assistant",
                "content": msg.content,
                "tokens": self.count_tokens({"role": "assistant", "content": msg.content})
            })

        # Handle function call
        if msg.function_call:
            function_call = msg.function_call
            arguments = function_call.arguments
            self.memory.append({
                "role": "assistant",
                "function_call": {
                    "name": function_call.name,
                    "arguments": arguments
                },
                "tokens": self.count_tokens({
                    "role": "assistant",
                    "content": f"[Function call] {function_call.name}({arguments})"
                })
            })

        # Perform summarization if needed
        self._maybe_summarize_memory()

        return msg.content, msg.function_call.name, msg.function_call.arguments


    def _maybe_summarize_memory(self):
        memory_tokens = sum([message["tokens"] for message in self.memory])
        if memory_tokens > self.memory_max_tokens:
            old_memory, self.memory = self._split_on_token_limit(self.memory, self.memory_max_tokens)
            summary = self._summarize_memory(old_memory)
            summary_content = "Summary of previous conversation: " + summary
            self.summary_memory.append(
                {
                    "role": "system",
                    "content": summary_content,
                    "tokens": self.count_tokens({"role": "system", "content": summary_content})
                }
            )


        summary_memory_tokens = sum([message["tokens"] for message in self.summary_memory])
        if summary_memory_tokens > self.summary_memory_max_tokens:
            old_summary_memory, self.summary_memory = self._split_on_token_limit(self.summary_memory, self.summary_memory_max_tokens)
            summary = self._summarize_memory(old_summary_memory)
            summary_content = "Summary of previous conversation: " + summary
            self.summary_memory.append(
                {
                    "role": "system",
                    "content": summary_content,
                    "tokens": self.count_tokens({"role": "system", "content": summary_content})
                }
            )

    def store_memory(self, filename: str):
        """
        Saves the full message history (including token counts) to a JSON file.

        :param filename: Path to the file where the memory will be stored.
        """
        with open(filename, "w") as f: # noinspection PyTypeChecker
            json.dump(self.messages(remove_tokens=False), f, indent=2)

    def _summarize_memory(self, messages: List[Dict]) -> str:
        """
        Uses the OpenAI API to summarize a list of chat messages for context compression.

        :param messages: List of messages to summarize.
        :return: Summary string generated by the model.
        """
        summary_prompt = [
            {"role": "system", "content": "Summarize the following conversation for context retention."},
            {"role": "user", "content": "\n".join(
                [f"{m['role'].capitalize()}: {m['content']}" for m in messages]
            )}
        ]
        response = openai.chat.completions.create(
            model=self.model,
            messages=summary_prompt,
        )
        return response.choices[0].message.content

    def count_tokens(self, message: Dict) -> int:
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
        """
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 4
        num_tokens += len(encoding.encode(message.get("content", "")))
        return num_tokens + 2

    @staticmethod
    def _split_on_token_limit(messages: List[Dict], token_limit: int) -> Tuple[List[Dict], List[Dict]]:
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
                return messages[:i + 1], messages[i + 1:]
        return [], messages
