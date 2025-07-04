import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Union

import pytest
import requests

from e2e.mock_openai_server.server import FIXTURE_PATH

REPO_ROOT = Path(__file__).parent.parent.resolve()
CURRENT_FIXTURE_DEFAULT_CONTENT = (
    "// Do not edit this file manually, it is generated by the test suite.\n"
)


@pytest.fixture()
def mock_openai_server():
    os.environ["OPENAI_BASE_URL"] = "http://localhost:8000/v1"
    os.environ["OPENAI_API_KEY"] = "test_key"

    server_path = REPO_ROOT / "e2e" / "mock_openai_server" / "server.py"

    proc = subprocess.Popen(
        ["python", str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to become ready
    timeout = 15
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get("http://localhost:8000/ping")
            if r.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Mock OpenAI server failed to start within timeout")

    # Run the Test
    yield proc

    # Teardown
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # Print stderr output for debugging if anything went wrong
    if proc.stderr:
        try:
            err_output = proc.stderr.read().decode().strip()
            if err_output:
                print("\n[MockOpenAI Server STDERR]", file=sys.stderr)
                print(err_output, file=sys.stderr)
        except Exception as e:
            print(f"[MockOpenAI Server] Failed to read stderr: {e}", file=sys.stderr)


def _ensure_fixture_file_exists(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(CURRENT_FIXTURE_DEFAULT_CONTENT)


def _copy_fixture(from_path: Path, to_path: Path):
    if not from_path.exists():
        raise FileNotFoundError(f"Fixture not found: {from_path}")
    shutil.copyfile(from_path, to_path)


@pytest.fixture()
def use_fixture():
    def _use_fixture(path: Union[str, Path]):
        if isinstance(path, str):
            path = Path(path)
        path = (REPO_ROOT / path).resolve()
        _ensure_fixture_file_exists(FIXTURE_PATH)
        _copy_fixture(path, FIXTURE_PATH)

    yield _use_fixture
    FIXTURE_PATH.write_text(CURRENT_FIXTURE_DEFAULT_CONTENT)
