import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from fellow.commands.view_file import ViewFileInput, view_file


@pytest.fixture
def sample_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        f.flush()
        yield f.name
    os.remove(f.name)


def test_view_entire_file(sample_file):
    args = ViewFileInput(filepath=sample_file)
    output = view_file(args, MagicMock())
    assert output == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"


def test_view_empty_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        file_path = f.name
    args = ViewFileInput(filepath=file_path)
    output = view_file(args, MagicMock())
    assert (
        output == "[INFO] The file is empty or the specified range contains no lines."
    )
    os.remove(file_path)


def test_view_specific_lines(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=2, to_line=4)
    output = view_file(args, MagicMock())
    assert output == "Line 2\nLine 3\nLine 4\n"


def test_view_with_from_only(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=4)
    output = view_file(args, MagicMock())
    assert output == "Line 4\nLine 5\n"


def test_view_with_to_only(sample_file):
    args = ViewFileInput(filepath=sample_file, to_line=3)
    output = view_file(args, MagicMock())
    assert output == "Line 1\nLine 2\nLine 3\n"


def test_out_of_bounds_range(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=10, to_line=15)
    output = view_file(args, MagicMock())
    assert output == "[INFO] No lines to display (start >= end)."


def test_file_not_found():
    args = ViewFileInput(filepath="nonexistent.txt")
    output = view_file(args, MagicMock())
    assert output.startswith("[ERROR] File not found")


def test_view_file_handles_read_exception(tmp_path):
    file_path = tmp_path / "faulty.txt"
    file_path.write_text("Line 1\nLine 2\n")

    args = ViewFileInput(filepath=str(file_path))

    with patch("builtins.open", side_effect=OSError("Mocked read failure")):
        result = view_file(args, MagicMock())

    assert result.startswith("[ERROR] Could not read file:")
    assert "Mocked read failure" in result
