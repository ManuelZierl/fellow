import os
import tempfile
from unittest.mock import MagicMock, patch

from fellow.commands.run_python import RunPythonInput, run_python


def test_run_python_success():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        f.write("print('Hello from test')\n")
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath)
        result = run_python(args, MagicMock())
        assert "Hello from test" in result
    finally:
        os.remove(filepath)


def test_run_python_with_args():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        f.write(
            """
import sys
print("ARGS:", sys.argv[1:])
"""
        )
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath, args="--test value")
        result = run_python(args, MagicMock())
        assert "ARGS: ['--test', 'value']" in result
    finally:
        os.remove(filepath)


def test_run_python_script_error():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        f.write("raise ValueError('Something went wrong')\n")
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath)
        result = run_python(args, MagicMock())
        assert "[ERROR]" in result or "Something went wrong" in result
    finally:
        os.remove(filepath)


def test_run_python_file_not_found():
    args = RunPythonInput(filepath="nonexistent_script.py")
    result = run_python(args, MagicMock())
    assert "[ERROR] File not found" in result or "[ERROR]" in result


def test_run_pytest_handles_file_not_found_error():
    args = RunPythonInput(filepath="nonexistent_test.py", args="")

    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = run_python(args, MagicMock())

    assert result == "[ERROR] File not found: nonexistent_test.py"


def test_run_pytest_handles_generic_exception():
    args = RunPythonInput(filepath="test_dummy.py", args="")

    with patch("subprocess.run", side_effect=RuntimeError("Something weird happened")):
        result = run_python(args, MagicMock())

    assert result.startswith("[ERROR] Failed to run script:")
    assert "Something weird happened" in result
