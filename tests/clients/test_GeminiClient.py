import importlib
import json
import os
from unittest.mock import MagicMock, patch

import pytest

from fellow.clients.Client import ChatResult, FunctionResult
from fellow.clients.GeminiClient import GeminiClient, GeminiClientConfig


@pytest.fixture
def config():
    return GeminiClientConfig(system_content="system", model="gemini-test-model")


@pytest.fixture
def mock_genai_client(monkeypatch):
    gemini_client_module = importlib.import_module("fellow.clients.GeminiClient")

    mock_client_cls = MagicMock()
    monkeypatch.setattr(gemini_client_module, "genai", MagicMock())
    gemini_client_module.genai.Client = mock_client_cls

    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.chats.create.return_value = mock_chat
    yield mock_client, mock_chat


@pytest.fixture(autouse=True)
def set_env():
    old_key = os.environ.get("GEMINI_API_KEY", "")
    os.environ["GEMINI_API_KEY"] = "dummy-key"
    yield
    os.environ["GEMINI_API_KEY"] = old_key


def test_init_raises_without_api_key():
    del os.environ["GEMINI_API_KEY"]
    with pytest.raises(
        ValueError, match="GEMINI_API_KEY environment variable is not set."
    ):
        GeminiClient(GeminiClientConfig(system_content="system", model="model"))


def test_create_returns_instance(config):
    client = GeminiClient.create(config)
    assert isinstance(client, GeminiClient)


def test_chat_without_function_result(config, mock_genai_client):
    mock_client, mock_chat = mock_genai_client
    mock_response = MagicMock(text="Hello!", function_calls=[])
    mock_chat.send_message.return_value = mock_response

    client = GeminiClient(config)
    result = client.chat(functions=[], message="Hi")

    assert result == {"message": "Hello!", "function_name": None, "function_args": None}
    mock_chat.send_message.assert_called_once()


def test_chat_with_function_result(config, mock_genai_client):
    mock_client, mock_chat = mock_genai_client
    mock_response = MagicMock(text="Processed function result!", function_calls=[])
    mock_chat.send_message.return_value = mock_response

    client = GeminiClient(config)
    function_result = {"name": "my_func", "output": {"key": "value"}}
    result = client.chat(functions=[], function_result=function_result)

    assert result == {
        "message": "Processed function result!",
        "function_name": None,
        "function_args": None,
    }


def test_chat_with_function_call_response(config, mock_genai_client):
    mock_client, mock_chat = mock_genai_client
    mock_response = MagicMock(
        text="Calling function!",
        function_calls=[MagicMock(name="do_something", args={"param": 42})],
    )
    mock_response.function_calls[0].name = "do_something"
    mock_response.function_calls[0].args = {"param": 42}
    mock_chat.send_message.return_value = mock_response

    client = GeminiClient(config)
    result = client.chat(functions=[], message="Hi")

    assert result["function_name"] == "do_something"
    assert result["function_args"] == json.dumps({"param": 42})


def test_store_memory(config, mock_genai_client, tmp_path):
    mock_client, mock_chat = mock_genai_client
    mock_history = [MagicMock(model_dump=lambda: {"message": "history item"})]
    mock_chat.get_history.return_value = mock_history

    client = GeminiClient(config)
    filename = tmp_path / "history.json"
    client.store_memory(str(filename))

    with open(filename) as f:
        data = json.load(f)
    assert data == [{"message": "history item"}]


def test_set_plan(config, mock_genai_client):
    mock_client, mock_chat = mock_genai_client
    client = GeminiClient(config)
    client.set_plan("My plan")

    mock_chat.send_message.assert_called_once_with(message="My plan")


@pytest.fixture
def dummy_command():
    mock_handler = MagicMock()
    mock_handler.__name__ = "dummy_func"
    mock_handler.__doc__ = "This is a dummy function."
    mock_command = MagicMock()
    mock_command.command_handler = mock_handler
    mock_command.input_type.model_json_schema.return_value = {
        "title": "Dummy",
        "properties": {"param1": {"type": "string", "title": "Param1"}},
    }
    return mock_command


def test_get_function_schema_success(config, mock_genai_client, dummy_command):
    client = GeminiClient(config)
    schema = client.get_function_schema(dummy_command)

    assert schema["name"] == "dummy_func"
    assert schema["description"] == "This is a dummy function."
    assert "parameters" in schema
    assert "param1" in schema["parameters"]["properties"]
    assert "title" not in schema["parameters"]


def test_get_function_schema_missing_name(config, mock_genai_client):
    client = GeminiClient(config)
    dummy_command = MagicMock()
    dummy_command.command_handler = object()  # No __name__

    with pytest.raises(
        ValueError, match="Command handler is not callable with __name__."
    ):
        client.get_function_schema(dummy_command)


def test_get_function_schema_missing_doc(config, mock_genai_client):
    client = GeminiClient(config)
    mock_handler = MagicMock()
    mock_handler.__name__ = "func"
    mock_handler.__doc__ = None
    dummy_command = MagicMock()
    dummy_command.command_handler = mock_handler

    with pytest.raises(ValueError, match="Command handler is __doc__ is empty"):
        client.get_function_schema(dummy_command)


def test_get_function_schema_unsupported_anyof(config, mock_genai_client):
    client = GeminiClient(config)
    mock_handler = MagicMock()
    mock_handler.__name__ = "func"
    mock_handler.__doc__ = "Test function"
    dummy_command = MagicMock()
    dummy_command.command_handler = mock_handler
    dummy_command.input_type.model_json_schema.return_value = {
        "title": "Schema",
        "properties": {
            "param": {
                "anyOf": [{"type": "string"}, {"type": "integer"}, {"type": "null"}]
            }
        },
    }

    with pytest.raises(ValueError, match="Unsupported anyOf length: 3"):
        client.get_function_schema(dummy_command)
