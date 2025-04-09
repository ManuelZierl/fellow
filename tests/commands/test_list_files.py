import os
import tempfile
from unittest.mock import MagicMock

from fellow.commands.list_files import ListFilesInput, list_files


def create_nested_test_structure(base_dir):
    os.makedirs(os.path.join(base_dir, "subdir1", "subsub"))
    os.makedirs(os.path.join(base_dir, "subdir2"))

    with open(os.path.join(base_dir, "file1.txt"), "w") as f:
        f.write("root file")

    with open(os.path.join(base_dir, "file2.py"), "w") as f:
        f.write("python file")

    with open(os.path.join(base_dir, "subdir1", "inner1.txt"), "w") as f:
        f.write("inner file")

    with open(os.path.join(base_dir, "subdir1", "subsub", "deep.py"), "w") as f:
        f.write("deep python file")


def test_flat_listing():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_nested_test_structure(tmpdir)

        args = ListFilesInput(directory=tmpdir, max_depth=1)
        result = list_files(args, MagicMock())

        assert "file1.txt" in result
        assert "file2.py" in result
        assert "subdir1/" in result
        assert "inner1.txt" not in result  # too deep
        assert "deep.py" not in result


def test_recursive_depth_2():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_nested_test_structure(tmpdir)

        args = ListFilesInput(directory=tmpdir, max_depth=2)
        result = list_files(args, MagicMock())

        assert (
            result
            == """file1.txt
file2.py
subdir1/
  inner1.txt
  subsub/
subdir2/"""
        )


def test_recursive_depth_3():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_nested_test_structure(tmpdir)

        args = ListFilesInput(directory=tmpdir, max_depth=3)
        result = list_files(args, MagicMock())

        assert "deep.py" in result


def test_filter_pattern():
    with tempfile.TemporaryDirectory() as tmpdir:
        create_nested_test_structure(tmpdir)

        args = ListFilesInput(directory=tmpdir, max_depth=3, pattern=".py")
        result = list_files(args, MagicMock())

        assert "file2.py" in result
        assert "deep.py" in result
        assert "file1.txt" not in result
        assert "inner1.txt" not in result


def test_invalid_directory():
    args = ListFilesInput(directory="/nonexistent", max_depth=1)
    result = list_files(args, MagicMock())
    assert result.startswith("[ERROR]")


def test_depth_zero_invalid():
    with tempfile.TemporaryDirectory() as tmpdir:
        args = ListFilesInput(directory=tmpdir, max_depth=0)
        result = list_files(args, MagicMock())
        assert "[ERROR] max_depth must be >= 1" in result
