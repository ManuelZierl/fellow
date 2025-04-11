from unittest.mock import MagicMock, patch

import pytest

from fellow.commands.search_files import SearchFilesInput, search_files


def create_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_search_finds_matches_case_insensitive(tmp_path):
    # Create a test file
    file_path = tmp_path / "example.txt"
    create_file(file_path, "Hello World\nhello again\nNothing here\n")

    args = SearchFilesInput(
        directory=str(tmp_path),
        search="hello",
    )

    result = search_files(args, MagicMock())
    assert "example.txt:1: Hello World" in result
    assert "example.txt:2: hello again" in result


def test_search_filters_by_extension(tmp_path):
    create_file(tmp_path / "keep.py", "search me\n")
    create_file(tmp_path / "ignore.txt", "search me\n")

    args = SearchFilesInput(directory=str(tmp_path), search="search", extension=".py")

    result = search_files(args, MagicMock())
    assert "keep.py" in result
    assert "ignore.txt" not in result


def test_search_no_matches(tmp_path):
    create_file(tmp_path / "a.txt", "foo\nbar\nbaz")

    args = SearchFilesInput(
        directory=str(tmp_path),
        search="notfound",
    )

    result = search_files(args, MagicMock())
    assert "[INFO] No matches found" in result


def test_directory_not_found(tmp_path):
    args = SearchFilesInput(directory="nonexistent_dir", search="hello")

    result = search_files(args, MagicMock())
    assert "[ERROR] Directory not found" in result


def test_search_files_handles_file_read_exception(tmp_path):
    # Create a file that would match the extension
    faulty_file = tmp_path / "test.txt"
    faulty_file.write_text("This line will not be read", encoding="utf-8")

    args = SearchFilesInput(directory=str(tmp_path), search="will", extension=".txt")

    # Patch open only when trying to read the faulty_file
    original_open = open

    def mock_open(path, *args, **kwargs):
        if str(path) == str(faulty_file):
            raise IOError("Mocked read error")
        return original_open(path, *args, **kwargs)

    with patch("builtins.open", side_effect=mock_open):
        result = search_files(args, MagicMock())

    assert result.startswith("[ERROR] Could not read")
    assert "Mocked read error" in result
    assert "test.txt" in result
