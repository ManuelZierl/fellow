import os
import tempfile
import pytest
from fellow.commands.edit_file import edit_file, EditFileInput


@pytest.fixture
def sample_file():
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        f.flush()
        yield f.name
    os.remove(f.name)


def test_insert_line(sample_file):
    args = EditFileInput(
        filepath=sample_file,
        from_line=3,
        to_line=3,
        new_text="Inserted Line"
    )
    result = edit_file(args)
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        lines = f.readlines()
    assert lines[2] == "Inserted Line\n"
    assert lines[3] == "Line 3\n"


def test_replace_lines(sample_file):
    args = EditFileInput(
        filepath=sample_file,
        from_line=2,
        to_line=4,
        new_text="New Line A\nNew Line B"
    )
    result = edit_file(args)
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        lines = f.readlines()
    assert lines[1] == "New Line A\n"
    assert lines[2] == "New Line B\n"
    assert lines[3] == "Line 4\n"  # Should remain


def test_delete_lines(sample_file):
    args = EditFileInput(
        filepath=sample_file,
        from_line=2,
        to_line=4,
        new_text=""
    )
    result = edit_file(args)
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        lines = f.readlines()
    assert lines == ["Line 1\n", "Line 4\n", "Line 5\n"]


def test_append_line(sample_file):
    args = EditFileInput(
        filepath=sample_file,
        from_line=6,
        to_line=6,
        new_text="Appended Line"
    )
    result = edit_file(args)
    assert result.startswith("[OK]")

    with open(sample_file) as f:
        lines = f.readlines()
    assert lines[-1] == "Appended Line\n"


def test_invalid_line_range(sample_file):
    args = EditFileInput(
        filepath=sample_file,
        from_line=5,
        to_line=2,
        new_text="Should fail"
    )
    result = edit_file(args)
    assert "[ERROR] Invalid line range" in result


def test_nonexistent_file():
    args = EditFileInput(
        filepath="/nonexistent/path.txt",
        from_line=1,
        to_line=1,
        new_text="test"
    )
    result = edit_file(args)
    assert result.startswith("[ERROR] File not found")
