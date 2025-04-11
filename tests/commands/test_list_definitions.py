from unittest.mock import MagicMock

import pytest

from fellow.commands.list_definitions import ListDefinitionsInput, list_definitions


def write_file(path, content):
    path.write_text(content, encoding="utf-8")


def test_lists_top_level_functions(tmp_path):
    code = """
def foo(a: int) -> str:
    \"\"\"Does foo.\"\"\"
    return str(a)
"""
    file = tmp_path / "sample.py"
    write_file(file, code)

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[INFO] Found 1 top-level function(s):" in result
    assert "- foo(a: int) -> str" in result
    assert '"""Does foo."""' in result


def test_lists_classes_and_methods(tmp_path):
    code = """
class Greeter:
    \"\"\"Greeter class.\"\"\"

    def greet(self, name: str) -> str:
        \"\"\"Say hello.\"\"\"
        return f"Hello, {name}"
"""
    file = tmp_path / "class_test.py"
    write_file(file, code)

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[INFO] Found 1 class(es):" in result
    assert "- Greeter" in result
    assert '"""Greeter class."""' in result
    assert "- greet(self, name: str) -> str" in result
    assert '"""Say hello."""' in result


def test_combined_top_level_and_classes(tmp_path):
    code = """
def top(): pass

class A:
    def method(self): pass
"""
    file = tmp_path / "combo.py"
    write_file(file, code)

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[INFO] Found 1 top-level function(s):" in result
    assert "[INFO] Found 1 class(es):" in result
    assert "- top()" in result
    assert "- A" in result
    assert "- method(self)" in result


def test_empty_file(tmp_path):
    file = tmp_path / "empty.py"
    write_file(file, "")

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[INFO] No functions or classes found" in result


def test_syntax_error(tmp_path):
    code = "def broken(:"
    file = tmp_path / "broken.py"
    write_file(file, code)

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[ERROR] Could not parse file due to syntax error" in result


def test_non_py_file(tmp_path):
    file = tmp_path / "not_python.txt"
    write_file(file, "def foo(): pass")

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[ERROR] Not a Python file" in result


def test_file_not_found():
    args = ListDefinitionsInput(filepath="this/file/does_not_exist.py")
    result = list_definitions(args, MagicMock())

    assert "[ERROR] File not found" in result


def test_read_failed(tmp_path):
    code = """
def foo():
    return "Hello, World!"
"""
    file = tmp_path / "read_failed.py"
    write_file(file, code)
    # Simulate a read failure by removing permissions
    file.chmod(0o000)

    args = ListDefinitionsInput(filepath=str(file))
    result = list_definitions(args, MagicMock())

    assert "[ERROR] Failed to read or parse the file" in result
