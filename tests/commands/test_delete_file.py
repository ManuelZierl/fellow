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
