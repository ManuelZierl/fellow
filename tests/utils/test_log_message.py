import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from fellow.commands.list_definitions import format_function
from fellow.utils.log_message import log_message


def test_format_function_with_doc_and_defaults():
    source = '''
def greet(name: str = "World") -> str:
    """Return a greeting."""
    return f"Hello, {name}!"
'''
    tree = ast.parse(source)
    func_node = next(node for node in tree.body if isinstance(node, ast.FunctionDef))

    formatted = format_function(func_node)
    assert formatted.startswith("  - greet(name: str = ")
    assert "-> str" in formatted
    assert '"""Return a greeting."""' in formatted


def test_log_message_writes_to_file(tmp_path):
    log_file: Path = tmp_path / "test_log.md"
    config = MagicMock(
        log=MagicMock(active=True, filepath=str(log_file), spoiler=False)
    )

    log_message(config, name="AI", color=1, content="Hello world")

    content = log_file.read_text(encoding="utf-8")
    assert (
        content
        == """<span style="color:#1f77b4">**AI:**</span>

Hello world

---

"""
    )
