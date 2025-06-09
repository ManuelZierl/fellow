import os
import tempfile
from unittest.mock import MagicMock

from fellow.commands.create_file import CreateFileInput, create_file


def test_create_new_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "newfile.txt")
        args = CreateFileInput(filepath=filepath)
        result = create_file(args, MagicMock())

        assert result == f"[OK] Created file: {filepath}"
        assert os.path.isfile(filepath)


def test_create_file_already_exists():
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        filepath = tmpfile.name

    try:
        args = CreateFileInput(filepath=filepath)
        result = create_file(args, MagicMock())
        assert result == f"[INFO] File already exists: {filepath}"
    finally:
        os.remove(filepath)


def test_create_file_in_new_subdirectory():
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "nested")
        filepath = os.path.join(subdir, "newfile.txt")

        args = CreateFileInput(filepath=filepath)
        result = create_file(args, MagicMock())

        assert result == f"[OK] Created file: {filepath}"
        assert os.path.isfile(filepath)
        assert os.path.isdir(subdir)


def test_create_file_invalid_path(monkeypatch):
    # Simulate os.makedirs raising an exception
    def raise_oserror(*args, **kwargs):
        raise OSError("Simulated permission error")

    monkeypatch.setattr(os, "makedirs", raise_oserror)

    args = CreateFileInput(filepath="/invalid/path/file.txt")
    result = create_file(args, MagicMock())

    assert result.startswith("[ERROR] Could not create file:")
