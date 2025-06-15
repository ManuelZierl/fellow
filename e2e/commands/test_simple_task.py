import json
import os
import re
from pathlib import Path
from uuid import UUID

from e2e.utils import run_command


def test_simple_hello_world_task(use_fixture, mock_openai_server, tmp_path):
    use_fixture("e2e/fixtures/mock_openai_server.json")
    os.chdir(tmp_path)

    commands = {
        command_name: {"policies": []}
        for command_name in [
            "create_file",
            "view_file",
            "edit_file",
            "list_files",
            "run_python",
        ]
    }
    result = run_command(
        f"fellow --task \"Write a hello world python script\" --commands '{json.dumps(commands)}'"
    )
    task_id = UUID(
        re.search(r"Starting task with id: ([0-9a-fA-F-]{36})", result).group(1)
    )
    assert task_id is not None
    assert "hello_world.py" in result

    assert os.path.exists(Path(f".fellow/runs/{task_id.hex}/memory.json"))
    assert os.path.exists(Path(f".fellow/runs/{task_id.hex}/log.md"))
    assert os.path.exists(Path(f".fellow/runs/{task_id.hex}/metadata.json"))

    assert os.path.exists(Path("hello_world.py"))
    with open(Path("hello_world.py")) as f:
        content = f.read()
    assert content == "print('Hello, World!')"
