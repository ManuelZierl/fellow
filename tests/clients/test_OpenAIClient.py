import os

import pytest
from unittest.mock import MagicMock, patch
from tempfile import NamedTemporaryFile
import json

from fellow.clients.OpenAIClient import OpenAIClient


@pytest.fixture
def client():
    return OpenAIClient(system_content="You are a helpful assistant.")

@pytest.fixture
def mock_openai_api_key():
    old_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "mock_api_key"
    yield
    if old_key is not None:
        os.environ["OPENAI_API_KEY"] = old_key


@patch("openai.chat.completions.create")
def test_messages(client):
    client.memory = [{"role": "user", "content": "Hi", "tokens": 5}]
    client.summary_memory = [{"role": "system", "content": "Summary", "tokens": 3}]
    result = client.messages(remove_tokens=True)
    assert all("tokens" not in msg for msg in result)

    client.memory = [{"role": "user", "content": "Hi", "tokens": 5}]
    client.summary_memory = [{"role": "system", "content": "Summary", "tokens": 3}]
    result = client.messages(remove_tokens=False)
    assert all("tokens" in msg for msg in result)

@patch("openai.chat.completions.create")
def test_chat(mock_create, client, mock_openai_api_key):
    mock_choice = MagicMock()
    mock_choice.message = MagicMock(content="Hello!", function_call=None)
    mock_create.return_value = MagicMock(choices=[mock_choice])

    response = client.chat("Hi there")
    assert response == ("Hello!", None, None)  # Updated to match the new expected tuple
    assert len(client.memory) == 2
    assert client.memory[-1]["content"] == "Hello!"
    assert "tokens" in client.memory[-1]

@patch.object(OpenAIClient, "_summarize_memory")
def test_memory_summarization_triggered(mock_summarize, client):
    mock_summarize.return_value = "summarized content"

    # Add 5 messages of 300 tokens each = 1500 total → over the 1000 limit
    client.memory = [
        {"role": "user", "content": f"msg{i}", "tokens": 300}
        for i in range(5)
    ]
    client.summary_memory = []
    client.count_tokens = lambda _: 300
    client.memory_max_tokens = 1000
    client.summary_memory_max_tokens = 1000

    # Simulate a response
    mock_create = MagicMock()
    mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Hello!"))])

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
    with NamedTemporaryFile(delete=False, mode='r+') as tmpfile:
        client.store_memory(tmpfile.name)
        tmpfile.seek(0)
        data = json.load(tmpfile)
    assert isinstance(data, list)
    assert any("content" in msg for msg in data)

def test_split_on_token_limit():
    messages = [{"role": "user", "content": f"msg{i}", "tokens": i} for i in range(1, 6)]
    first, second = OpenAIClient._split_on_token_limit(messages, 6)
    assert sum(m["tokens"] for m in second) <= 6
    assert len(first) + len(second) == len(messages)


def test__summarize_memory(client):
    messages = [
        {"role": "system", "content": "You are a bot."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "Can you summarize that?"},
        {"role": "assistant", "content": "Sure. It's a language for building software."}
    ]

    # Patch the OpenAI API call
    with patch("openai.chat.completions.create") as mock_create:
        mock_response = MagicMock()
        mock_response.choices[
            0].message.content = "The user asked about Python. Assistant explained it's a programming language."
        mock_create.return_value = mock_response

        summary = client._summarize_memory(messages)

        # Verify the OpenAI call was constructed correctly
        called_args = mock_create.call_args[1]["messages"]
        # The user message content passed to OpenAI should not include "system" roles
        assert called_args[0]["content"] == "Summarize the following conversation for context retention."
        assert called_args[1]["content"]== """System: You are a bot.
User: What is Python?
Assistant: Python is a programming language.
User: Can you summarize that?
Assistant: Sure. It's a language for building software."""

        # The result should match the mocked return
        assert summary == "The user asked about Python. Assistant explained it's a programming language."
