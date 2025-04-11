import os
import tempfile
from textwrap import dedent
from unittest.mock import MagicMock

from fellow.commands.get_code import GetCodeInput, get_code


def write_temp_py(content: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(dedent(content))
        return f.name


def test_top_level_function():
    code = """
    def greet(name):
        return f"Hello, {name}"
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="greet"), MagicMock())
    assert "def greet" in result
    assert "return f" in result


def test_class_definition():
    code = """
    class Greeter:
        def greet(self, name):
            return f"Hi, {name}"
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="Greeter"), MagicMock())
    assert "class Greeter" in result
    assert "def greet" in result


def test_class_method():
    code = """
    class Greeter:
        def greet(self, name):
            return f"Hi, {name}"
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="Greeter.greet"), MagicMock())
    assert "def greet" in result
    assert "return f" in result
    assert "class Greeter" not in result  # Only the method should be returned


def test_function_not_found():
    code = """
    def foo():
        pass
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="bar"), MagicMock())
    assert "[INFO] Element 'bar' not found" in result


def test_method_not_found():
    code = """
    class Greeter:
        def greet(self, name):
            return f"Hi, {name}"
    """
    path = write_temp_py(code)
    result = get_code(
        GetCodeInput(filepath=path, element="Greeter.say_hello"), MagicMock()
    )
    assert "[INFO] Method 'Greeter.say_hello' not found" in result


def test_invalid_element_format():
    code = """
    def foo(): pass
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="a.b.c"), MagicMock())
    assert "[ERROR] Invalid element format" in result


def test_syntax_error():
    code = """
    def foo(
        print("Hello, World!")
    """
    path = write_temp_py(code)
    result = get_code(GetCodeInput(filepath=path, element="foo"), MagicMock())
    assert "[ERROR] Could not parse file due to syntax error:" in result


def test_read_failed():
    code = """
    def foo():
        return "Hello, World!"
    """

    # Simulate a read failure
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(dedent(code))
        f.close()
        os.chmod(f.name, 0o000)  # Remove all permissions
        result = get_code(GetCodeInput(filepath=f.name, element="foo"), MagicMock())
        assert "[ERROR] Failed to read or parse the file:" in result


def test_file_not_found():
    result = get_code(
        GetCodeInput(filepath="non_existent_file.py", element="foo"), MagicMock()
    )
    assert result == "[ERROR] File not found: non_existent_file.py"


def test_not_a_python_file():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("This is not a Python file.")
        f.close()
        result = get_code(GetCodeInput(filepath=f.name, element="foo"), MagicMock())
        assert result.startswith("[ERROR] Not a Python file:")
        os.remove(f.name)  # Clean up the temporary file
