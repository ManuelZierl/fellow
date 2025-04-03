import pytest
from pathlib import Path
from fellow.utils.log_message import log_message


@pytest.fixture(autouse=True)
def patch_format_message(monkeypatch):
    monkeypatch.setattr("fellow.utils.log_message.format_ai_message",
                        lambda **kwargs: f"{kwargs['name']}: {kwargs['content']}\n")


def test_log_message_writes_to_file(tmp_path):
    log_file: Path = tmp_path / "test_log.md"
    config = {"log": str(log_file)}

    log_message(config, name="AI", color=1, content="Hello world")

    content = log_file.read_text(encoding="utf-8")
    assert content == """> <span style="color:#1f77b4">**AI:**</span>
>
> > Hello world

---
"""


def test_log_message_skips_if_no_log():
    config = {}
    # Should not raise, should do nothing
    log_message(config, name="System", color=0, content="Should not be written")
