import json
import os
import tempfile
import pytest

from fellow.clients.CommandClient import CommandClient


@pytest.fixture
def client():
    return CommandClient()


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
        result_create = client.run(json.dumps(create_cmd))
        assert "[OK]" in result_create
        assert os.path.isfile(file_path)

        # Run view
        result_view = client.run(json.dumps(view_cmd))
        assert result_view.strip() == ""  # Empty file


def test_invalid_json(client):
    command = "{ this is not valid json }"
    result = client.run(command)
    assert "[ERROR] Invalid JSON" in result


def test_multiple_top_level_keys(client):
    command = json.dumps({
        "create_file": {"filepath": "a.txt"},
        "view_file": {"filepath": "a.txt"}
    })
    result = client.run(command)
    assert "exactly one top-level" in result


def test_unknown_command(client):
    command = json.dumps({
        "not_a_real_command": {"foo": "bar"}
    })
    result = client.run(command)
    assert "Unknown command" in result


def test_non_dict_args(client):
    command = json.dumps({
        "create_file": "this should be an object"
    })
    result = client.run(command)
    assert "arguments must be an object" in result


def test_invalid_args_validation(client):
    command = json.dumps({
        "view_file": {"filepath": 123}  # should be str
    })
    result = client.run(command)
    assert "Invalid command arguments" in result


def test_runtime_error(client, monkeypatch):
    # Force the handler to raise an error
    from fellow.commands.view_file import view_file

    def broken_handler(args):
        raise RuntimeError("Something went wrong")

    from fellow import commands
    commands.COMMANDS["view_file"] = (commands.COMMANDS["view_file"][0], broken_handler)

    command = json.dumps({
        "view_file": {"filepath": "test.txt"}
    })

    result = client.run(command)
    assert "Command execution failed" in result
