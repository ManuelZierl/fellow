import textwrap
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from fellow.clients import ALL_CLIENTS
from fellow.utils.load_client import load_client


def test_load_custom_client_from_file(tmp_path):
    # Arrange
    client_file = tmp_path / "MyClient.py"
    client_file.write_text(
        textwrap.dedent(
            """
        from fellow.clients.Client import Client, ClientConfig

        class MyClientConfig(ClientConfig):
            pass

        class MyClient(Client[MyClientConfig]):
            config_class = MyClientConfig

            @classmethod
            def create(cls, config):
                instance = cls()
                instance.config = config
                return instance
    """
        )
    )

    config = SimpleNamespace(
        ai_client=SimpleNamespace(client="my", config={}),
        custom_clients_paths=[str(tmp_path)],
    )

    client = load_client(system_content="hello", config=config)

    assert isinstance(client, object)
    assert hasattr(client, "config")
    assert client.config.system_content == "hello"


def test_load_client_skips_invalid_dir(capsys):
    config = SimpleNamespace(
        ai_client=SimpleNamespace(client="nonexistent", config={}),
        custom_clients_paths=["/path/does/not/exist"],
    )

    with patch.dict(ALL_CLIENTS, {}):  # No fallback
        with pytest.raises(ValueError, match="Client 'nonexistent' not found"):
            load_client(system_content="irrelevant", config=config)

    captured = capsys.readouterr()
    assert "Skipping /path/does/not/exist: not a valid directory" in captured.out


def test_load_client_fallback_to_builtin():
    dummy_config_class = MagicMock()
    dummy_config_class.return_value = SimpleNamespace(system_content="fallback")

    dummy_client_class = MagicMock()
    dummy_client_class.config_class = dummy_config_class
    dummy_client_class.create.return_value = "dummy-client"

    with patch.dict(ALL_CLIENTS, {"dummy": dummy_client_class}):
        config = SimpleNamespace(
            ai_client=SimpleNamespace(client="dummy", config={}),
            custom_clients_paths=[],
        )
        result = load_client(system_content="fallback", config=config)
        assert result == "dummy-client"
        dummy_client_class.create.assert_called_once()


def test_load_client_raises_if_not_found():
    config = SimpleNamespace(
        ai_client=SimpleNamespace(client="ghost", config={}),
        custom_clients_paths=[],
    )

    with patch.dict(ALL_CLIENTS, {}):
        with pytest.raises(ValueError, match="Client 'ghost' not found"):
            load_client(system_content="missing", config=config)
