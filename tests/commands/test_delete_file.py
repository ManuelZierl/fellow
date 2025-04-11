import os
import tempfile
from unittest.mock import MagicMock

import pytest

from fellow.commands.delete_file import DeleteFileInput, delete_file


def test_delete_existing_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name

    assert os.path.exists(filepath)

    args = DeleteFileInput(filepath=filepath)
    result = delete_file(args, MagicMock())

    assert "[OK]" in result


def test_try_delete_non_existent_file():
    args = DeleteFileInput(filepath="non_existent_file.txt")
    result = delete_file(args, MagicMock())

    assert result == "[ERROR] File not found: non_existent_file.txt"


def test_try_delete_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = DeleteFileInput(filepath=tmpdir)
        result = delete_file(args, MagicMock())

        assert result == f"[ERROR] {tmpdir} is a directory. Only files can be deleted."


def test_delete_failed():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name

    # Mock os.remove to raise an OSError
    def mock_remove(filepath):
        raise OSError("Simulated permission error")

    # Replace os.remove with the mock
    original_remove = os.remove
    os.remove = mock_remove

    try:
        args = DeleteFileInput(filepath=filepath)
        result = delete_file(args, MagicMock())

        assert result.startswith("[ERROR] Failed to delete file:")
    finally:
        # Restore the original os.remove
        os.remove = original_remove

        # Clean up the temporary file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
