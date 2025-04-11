import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from fellow.commands.edit_file import EditFileInput, edit_file


@pytest.fixture
def sample_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        f.flush()
        yield f.name
    os.remove(f.name)


def test_edit_file(sample_file):
    args = EditFileInput(filepath=sample_file, new_text="Inserted Line")
    result = edit_file(args, MagicMock())
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert lines[0] == "Inserted Line"


def test_delete_file_content(sample_file):
    args = EditFileInput(filepath=sample_file, new_text="")
    result = edit_file(args, MagicMock())
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        content = f.read()
    assert content == ""


def test_nonexistent_file():
    args = EditFileInput(filepath="/nonexistent/path.txt", new_text="test")
    result = edit_file(args, MagicMock())
    assert result.startswith("[ERROR] File not found")


def test_edit_file_failed():
    input_data = EditFileInput(filepath="dummy.txt", new_text="Some new content")

    # Pretend the file exists
    with patch("os.path.isfile", return_value=True):
        # Patch open to raise an IOError
        with patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.side_effect = IOError("disk full")

            result = edit_file(input_data, MagicMock())

    assert result.startswith("[ERROR] Could not edit file: disk full")
