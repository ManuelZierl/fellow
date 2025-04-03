import pytest
import os
import tempfile

from fellow.clients.CommandClient import CommandClient
from fellow.commands import CreateFileInput, ViewFileInput, create_file, view_file


@pytest.fixture
def client():
    return CommandClient(None)


def test_valid_create_and_view(client):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.txt")

        create_cmd = CreateFileInput(filepath=file_path)
        view_cmd = ViewFileInput(filepath=file_path)

        # Run create
        result_create = client.run(create_cmd, create_file)
        assert "[OK]" in result_create
        assert os.path.isfile(file_path)

        # Run view
        result_view = client.run(view_cmd, view_file)
        assert result_view.strip() == '[INFO] The file is empty or the specified range contains no lines.'


def test_runtime_error(client):
    def broken_handler(args):
        raise RuntimeError("Something went wrong")

    command = ViewFileInput(filepath="test.txt", from_line=1, to_line=10)

    result = client.run(command, broken_handler)
    assert "Command execution failed" in result
