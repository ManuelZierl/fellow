import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def setup_env():
    os.environ["OPENAI_API_KEY"] = "mock-key"
    os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
