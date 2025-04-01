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

    result = search_files(args)
    assert "example.txt:1: Hello World" in result
    assert "example.txt:2: hello again" in result


def test_search_filters_by_extension(tmp_path):
    create_file(tmp_path / "keep.py", "search me\n")
    create_file(tmp_path / "ignore.txt", "search me\n")

    args = SearchFilesInput(
        directory=str(tmp_path),
        search="search",
        extension=".py"
    )

    result = search_files(args)
    assert "keep.py" in result
    assert "ignore.txt" not in result


def test_search_no_matches(tmp_path):
    create_file(tmp_path / "a.txt", "foo\nbar\nbaz")

    args = SearchFilesInput(
        directory=str(tmp_path),
        search="notfound",
    )

    result = search_files(args)
    assert "[INFO] No matches found" in result


def test_directory_not_found(tmp_path):
    args = SearchFilesInput(
        directory="nonexistent_dir",
        search="hello"
    )

    result = search_files(args)
    assert "[ERROR] Directory not found" in result
