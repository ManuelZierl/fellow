import os
import tempfile
from fellow.commands.run_python import run_python, RunPythonInput


def test_run_python_success():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write("print('Hello from test')\n")
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath)
        result = run_python(args)
        assert "Hello from test" in result
    finally:
        os.remove(filepath)


def test_run_python_with_args():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write("""
import sys
print("ARGS:", sys.argv[1:])
""")
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath, args="--test value")
        result = run_python(args)
        assert "ARGS: ['--test', 'value']" in result
    finally:
        os.remove(filepath)


def test_run_python_script_error():
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write("raise ValueError('Something went wrong')\n")
        f.flush()
        filepath = f.name

    try:
        args = RunPythonInput(filepath=filepath)
        result = run_python(args)
        assert "[ERROR]" in result or "Something went wrong" in result
    finally:
        os.remove(filepath)


def test_run_python_file_not_found():
    args = RunPythonInput(filepath="nonexistent_script.py")
    result = run_python(args)
    assert "[ERROR] File not found" in result or "[ERROR]" in result
