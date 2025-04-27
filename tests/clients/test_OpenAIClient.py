import json
import os
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

import pytest

from fellow.clients.OpenAIClient import OpenAIClient, OpenAIClientConfig
from fellow.commands import Command, ViewFileInput, view_file


@pytest.fixture
def client():
    return OpenAIClient.create(
        OpenAIClientConfig(
            system_content="You are a helpful assistant.",
            memory_max_tokens=1000,
            summary_memory_max_tokens=1000,
            model="gpt-3.5-turbo",
        )
    )


@pytest.fixture
def mock_openai_api_key():
    old_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "mock_api_key"
    yield
    if old_key is not None:
        os.environ["OPENAI_API_KEY"] = old_key


@patch("openai.chat.completions.create")
def test_messages(client, mock_openai_api_key):
    client.memory = [{"role": "user", "content": "Hi", "tokens": 5}]
    client.summary_memory = [{"role": "system", "content": "Summary", "tokens": 3}]
    result = client.messages(remove_tokens=True)
    assert all("tokens" not in msg for msg in result)

    client.memory = [{"role": "user", "content": "Hi", "tokens": 5}]
    client.summary_memory = [{"role": "system", "content": "Summary", "tokens": 3}]
    result = client.messages(remove_tokens=False)
    assert all("tokens" in msg for msg in result)


def test_message_to_params(client, mock_openai_api_key):
    client.memory = [
        {"role": "system", "content": "You are a helpful assistant.", "tokens": 5},
        {"role": "user", "content": "What's the weather?", "tokens": 5},
        {
            "role": "assistant",
            "content": "I will call the `get_weather` function",
            "tokens": 2,
        },
        {
            "role": "assistant",
            "function_call": {"name": "get_weather", "arguments": "now"},
        },
        {
            "role": "function",
            "content": "It's sunny.",
            "tokens": 2,
            "name": "get_weather",
        },
    ]

    assert client.message_to_params() == [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather?"},
        {"role": "assistant", "content": "I will call the `get_weather` function"},
        {
            "role": "assistant",
            "function_call": {"name": "get_weather", "arguments": "now"},
        },
        {"role": "function", "name": "get_weather", "content": "It's sunny."},
    ]


@patch("openai.chat.completions.create")
def test_chat(mock_create, client, mock_openai_api_key):
    mock_choice = MagicMock()
    mock_choice.message = MagicMock(content="Hello!", function_call=None)
    mock_create.return_value = MagicMock(choices=[mock_choice])

    functions = [
        {"name": "func", "description": "func1 description", "parameters": {"arg": 1}}
    ]

    response = client.chat(
        functions=functions, message="Hi there", function_result=None
    )
    assert response == {
        "message": "Hello!",
        "function_name": None,
        "function_args": None,
    }
    assert len(client.memory) == 2
    assert client.memory[-1]["content"] == "Hello!"
    assert "tokens" in client.memory[-1]
    mock_create.assert_called_once()
    assert mock_create.call_args[1]["functions"] == functions

    mock_choice = MagicMock()
    mock_function_call = MagicMock(arguments="{}")
    mock_function_call.name = "get_code"
    mock_choice.message = MagicMock(content=None, function_call=mock_function_call)
    mock_create.return_value = MagicMock(choices=[mock_choice])
    response = client.chat(
        "", function_result={"name": "get_code", "output": "import os"}
    )
    assert response == {
        "message": None,
        "function_name": "get_code",
        "function_args": "{}",
    }


@patch.object(OpenAIClient, "_summarize_memory")
def test_memory_summarization_triggered(mock_summarize, client):
    mock_summarize.return_value = "summarized content"

    # Add 5 messages of 300 tokens each = 1500 total → over the 1000 limit
    client.memory = [
        {"role": "user", "content": f"msg{i}", "tokens": 300} for i in range(5)
    ]
    client.summary_memory = []
    client._count_tokens = lambda _: 300
    client.memory_max_tokens = 1000
    client.summary_memory_max_tokens = 1000

    # Simulate a response
    mock_create = MagicMock()
    mock_create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Hello!"))]
    )

    with patch("openai.chat.completions.create", mock_create):
        client.chat("Trigger summarization")

    # 1500 old tokens + new user + assistant message (~600 total) → memory must be trimmed
    assert len(client.summary_memory) == 1
    summary_message = client.summary_memory[0]
    assert "summarized content" in summary_message["content"]

    # Verify memory was split: only ~1000 tokens allowed to remain
    remaining_token_sum = sum(m["tokens"] for m in client.memory)
    assert remaining_token_sum <= client.memory_max_tokens

    # only 3 messages can remain
    assert len(client.memory) == 3


def test_store_memory(client):
    client.memory = [{"role": "user", "content": "Hi", "tokens": 5}]
    with NamedTemporaryFile(delete=False, mode="r+") as tmpfile:
        client.store_memory(tmpfile.name)
        tmpfile.seek(0)
        data = json.load(tmpfile)
    assert isinstance(data, list)
    assert any("content" in msg for msg in data)


def test_split_on_token_limit():
    messages = [
        {"role": "user", "content": f"msg{i}", "tokens": i} for i in range(1, 6)
    ]
    first, second = OpenAIClient._split_on_token_limit(messages, 6)
    assert sum(m["tokens"] for m in second) <= 6
    assert len(first) + len(second) == len(messages)
    assert OpenAIClient._split_on_token_limit(messages, 100) == ([], messages)


def test__summarize_memory(client):
    messages = [
        {"role": "system", "content": "You are a bot."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "Can you summarize that?"},
        {
            "role": "assistant",
            "content": "Sure. It's a language for building software.",
        },
        {
            "role": "assistant",
            "function_call": {"name": "get_code", "arguments": "main.py"},
        },
    ]

    # Patch the OpenAI API call
    with patch("openai.chat.completions.create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            "The user asked about Python. Assistant explained it's a programming language."
        )
        mock_create.return_value = mock_response

        summary = client._summarize_memory(messages)

        # Verify the OpenAI call was constructed correctly
        called_args = mock_create.call_args[1]["messages"]
        # The user message content passed to OpenAI should not include "system" roles
        assert (
            called_args[0]["content"]
            == "Summarize the following conversation for context retention."
        )
        assert (
            called_args[1]["content"]
            == """System: You are a bot.
User: What is Python?
Assistant: Python is a programming language.
User: Can you summarize that?
Assistant: Sure. It's a language for building software.
Assistant: [Function call] get_code(main.py)"""
        )

        # The result should match the mocked return
        assert (
            summary
            == "The user asked about Python. Assistant explained it's a programming language."
        )


def test__maybe_summarize_memory(client):
    # Prepare client
    client.memory_max_tokens = 100
    client.summary_memory_max_tokens = 100

    # Provide mock summary
    mock_summarize = MagicMock()
    client._summarize_memory = mock_summarize
    mock_summarize.return_value = "Summary A"

    # Fill memory to exceed threshold
    client.memory = [
        {"role": "user", "content": "msg", "tokens": 60}
    ] * 3  # 180 tokens total

    # Patch count_tokens to return fixed value for simplicity
    client._count_tokens = lambda msg: 10

    # Trigger summarization
    client._maybe_summarize_memory()

    # Should summarize part of memory
    assert len(client.memory) == 1
    assert len(client.summary_memory) == 1
    summary_msg = client.summary_memory[0]
    assert summary_msg["role"] == "system"
    assert "Summary of previous conversation: Summary A" in summary_msg["content"]
    assert len(mock_summarize.call_args[0][0]) == 2

    # Now test recursive summarization on summary_memory
    mock_summarize.return_value = "Summary B"
    # Force summary memory to exceed again
    client.summary_memory = [
        {"role": "system", "content": "summary", "tokens": 60}
    ] * 3  # 180 tokens

    client._maybe_summarize_memory()

    assert len(client.summary_memory) == 2
    assert (
        "Summary of previous conversation: Summary B"
        in client.summary_memory[1]["content"]
    )
    assert len(mock_summarize.call_args[0][0]) == 2


def test_set_plan():
    # todo: ...
    pass


def test_command_get_function_schema(client):
    command = Command(ViewFileInput, view_file)
    assert client.get_function_schema(command) == {
        "name": "view_file",
        "description": "View the contents of a file, optionally between specific line numbers.",
        "parameters": {
            "properties": {
                "filepath": {
                    "description": "The path to the file to be viewed.",
                    "title": "Filepath",
                    "type": "string",
                },
                "from_line": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "Optional 1-based starting line number.",
                    "title": "From Line",
                },
                "to_line": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "Optional 1-based ending line number (inclusive).",
                    "title": "To Line",
                },
            },
            "required": ["filepath"],
            "title": "ViewFileInput",
            "type": "object",
        },
    }

    with pytest.raises(ValueError) as err:
        client.get_function_schema(Command(ViewFileInput, lambda x, y: None))
    assert str(err.value) == "[ERROR] Command handler is __doc__ is empty"

    with pytest.raises(ValueError) as err:
        client.get_function_schema(Command(ViewFileInput, "no-name"))
    assert str(err.value) == "[ERROR] Command handler is not callable with __name__."
