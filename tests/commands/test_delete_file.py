import os
import tempfile
import pytest
from fellow.commands.delete_file import delete_file, DeleteFileInput


def test_delete_existing_file():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        filepath = f.name

    assert os.path.exists(filepath)

    args = DeleteFileInput(filepath=filepath)
    result = delete_file(args)

    assert "[OK]" in result
