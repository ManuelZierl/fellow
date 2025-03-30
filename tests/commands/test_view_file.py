import os
import tempfile
import pytest
from fellow.commands.view_file import view_file, ViewFileInput


@pytest.fixture
def sample_file():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        f.flush()
        yield f.name
    os.remove(f.name)


def test_view_entire_file(sample_file):
    args = ViewFileInput(filepath=sample_file)
    output = view_file(args)
    assert output == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"


def test_view_specific_lines(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=2, to_line=4)
    output = view_file(args)
    assert output == "Line 2\nLine 3\nLine 4\n"


def test_view_with_from_only(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=4)
    output = view_file(args)
    assert output == "Line 4\nLine 5\n"


def test_view_with_to_only(sample_file):
    args = ViewFileInput(filepath=sample_file, to_line=3)
    output = view_file(args)
    assert output == "Line 1\nLine 2\nLine 3\n"


def test_out_of_bounds_range(sample_file):
    args = ViewFileInput(filepath=sample_file, from_line=10, to_line=15)
    output = view_file(args)
    assert output == "[INFO] No lines to display (start >= end)."


def test_file_not_found():
    args = ViewFileInput(filepath="nonexistent.txt")
    output = view_file(args)
    assert output.startswith("[ERROR] File not found")

