import pytest
from pathlib import Path
from fellow.utils.log_message import log_message


def test_log_message_writes_to_file(tmp_path):
    log_file: Path = tmp_path / "test_log.md"
    config = {"log": str(log_file)}

    log_message(config, name="AI", color=1, content="Hello world")

    content = log_file.read_text(encoding="utf-8")
    assert content == """<span style="color:#1f77b4">**AI:**</span>

Hello world

---

"""
