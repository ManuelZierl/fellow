import os
import tempfile
from unittest.mock import MagicMock, patch

from fellow.commands.run_pytest import RunPytestInput, run_pytest


def create_test_file(content: str) -> str:
    temp_dir = tempfile.mkdtemp()
    test_path = os.path.join(temp_dir, "test_temp_example.py")
    with open(test_path, "w") as f:
        f.write(content)
    return test_path


def test_run_all_tests_success():
    code = """
def test_pass():
    assert 1 + 1 == 2
"""
    test_file = create_test_file(code)
    args = RunPytestInput(target=test_file)
    output = run_pytest(args, MagicMock())

    assert "1 passed" in output or "collected 1 item" in output


def test_run_specific_test_name():
    code = """
def test_one():
    assert True

def test_two():
    assert False
"""
    test_file = create_test_file(code)
    args = RunPytestInput(target=test_file, args="-k test_one")
    output = run_pytest(args, MagicMock())

    assert "1 passed" in output
    assert "test_two" not in output


def test_run_failing_test():
    code = """
def test_fail():
    assert False
"""
    test_file = create_test_file(code)
    args = RunPytestInput(target=test_file)
    output = run_pytest(args, MagicMock())

    assert "[ERROR]" in output
    assert "1 failed" in output


def test_invalid_test_path():
    args = RunPytestInput(target="nonexistent_test_file.py")
    output = run_pytest(args, MagicMock())

    assert "[ERROR]" in output
    assert "not found" in output or "No such file" in output


def test_run_pytest_handles_file_not_found_error():
    args = RunPytestInput(target="nonexistent_test.py", args="")

    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = run_pytest(args, MagicMock())

    assert result == "[ERROR] Test file or directory not found: nonexistent_test.py"


def test_run_pytest_handles_generic_exception():
    args = RunPytestInput(target="test_dummy.py", args="")

    with patch("subprocess.run", side_effect=RuntimeError("Something weird happened")):
        result = run_pytest(args, MagicMock())

    assert result.startswith("[ERROR] Failed to run pytest:")
    assert "Something weird happened" in result
