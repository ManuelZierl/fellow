import json
import os
import tempfile
import pytest

from fellow.clients.CommandClient import CommandClient
from fellow.commands import ALL_COMMANDS


@pytest.fixture
def client():
    return CommandClient(ALL_COMMANDS, None)  # todo: Mock OpenAIClient for testing


def test_valid_create_and_view(client):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.txt")

        create_cmd = {
            "create_file": {
                "filepath": file_path
            }
        }

        view_cmd = {
            "view_file": {
                "filepath": file_path
            }
        }

        # Run create
        result_create = client.run(create_cmd)
        assert "[OK]" in result_create
        assert os.path.isfile(file_path)

        # Run view
        result_view = client.run(view_cmd)
        assert result_view.strip() == '[INFO] The file is empty or the specified range contains no lines.'


def test_multiple_top_level_keys(client):
    command = {
        "create_file": {"filepath": "a.txt"},
        "view_file": {"filepath": "a.txt"}
    }
    result = client.run(command)
    assert "exactly one top-level" in result


def test_unknown_command(client):
    command = {
        "not_a_real_command": {"foo": "bar"}
    }
    result = client.run(command)
    assert "Unknown command" in result


def test_non_dict_args(client):
    command = {
        "create_file": "this should be an object"
    }
    result = client.run(command)
    assert "arguments must be an object" in result


def test_invalid_args_validation(client):
    command = {
        "view_file": {"filepath": 123}  # should be str
    }
    result = client.run(command)
    assert "Invalid command arguments" in result


def test_runtime_error(client, monkeypatch):
    # Force the handler to raise an error
    from fellow.commands.view_file import view_file

    def broken_handler(args):
        raise RuntimeError("Something went wrong")

    from fellow import commands
    ALL_COMMANDS["view_file"] = (ALL_COMMANDS["view_file"][0], broken_handler)

    command = {
        "view_file": {"filepath": "test.txt"}
    }

    result = client.run(command)
    assert "Command execution failed" in result
