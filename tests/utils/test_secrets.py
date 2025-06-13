import os
import tempfile
from pathlib import Path

import pytest

from fellow.utils.secrets import add_secret, clear_secrets, load_secrets, remove_secret


@pytest.fixture
def secrets_file_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / ".secrets"
        yield path


def test_add_and_load_secret(monkeypatch, secrets_file_tmpdir):
    key = "MY_SECRET"
    value = "supersecret"
    add_secret(value, key, str(secrets_file_tmpdir))
    monkeypatch.delenv(key, raising=False)
    load_secrets(secrets_file_tmpdir)
    assert os.environ[key] == value


def test_add_secret_preserves_comments(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("# comment\nEXISTING=old\n")
    add_secret("newval", "NEWKEY", str(secrets_file_tmpdir))
    content = secrets_file_tmpdir.read_text()
    assert content == "# comment\nEXISTING=old\nNEWKEY=newval\n"


def test_add_secret_updates_existing(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("OTHER=other\nEXISTING=old\n")
    add_secret("updated", "EXISTING", str(secrets_file_tmpdir))
    content = secrets_file_tmpdir.read_text()
    assert "EXISTING=updated" in content


def test_remove_secret(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("ONE=1\nTWO=2\nTHREE=3\n")
    remove_secret("TWO", str(secrets_file_tmpdir))
    content = secrets_file_tmpdir.read_text()
    assert "TWO=2" not in content
    assert "ONE=1" in content
    assert "THREE=3" in content


def test_clear_secrets(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("A=1\nB=2\n")
    clear_secrets(str(secrets_file_tmpdir))
    assert secrets_file_tmpdir.read_text() == ""


def test_load_secrets_missing_file(tmp_path, monkeypatch):
    secrets_path = tmp_path / ".secrets"
    monkeypatch.delenv("FOO", raising=False)
    load_secrets(str(secrets_path))


def test_load_secrets_ignores_comments_and_blank_lines(
    monkeypatch, secrets_file_tmpdir
):
    secrets_file_tmpdir.write_text("\n# This is a comment\nMY_SECRET=value\n\n")
    monkeypatch.delenv("MY_SECRET", raising=False)
    load_secrets(str(secrets_file_tmpdir))
    assert os.environ["MY_SECRET"] == "value"


def test_load_secrets_does_not_override_existing_env(secrets_file_tmpdir, monkeypatch):
    os.environ["MY_KEY"] = "existing"
    secrets_file_tmpdir.write_text("MY_KEY=newval\n")
    load_secrets(str(secrets_file_tmpdir))
    assert os.environ["MY_KEY"] == "existing"


def test_invalid_secrets_doesnt_fail(secrets_file_tmpdir, monkeypatch):
    secrets_file_tmpdir.write_text("INVALID_LINE\nANOTHER_INVALID_LINE\n")
    monkeypatch.delenv("MY_KEY", raising=False)
    load_secrets(str(secrets_file_tmpdir))
    assert "MY_KEY" not in os.environ


def test_remove_secret_path_not_found(secrets_file_tmpdir):
    non_existent_path = secrets_file_tmpdir.parent / "non_existent_secrets"
    remove_secret("NON_EXISTENT_KEY", str(non_existent_path))
    assert not non_existent_path.exists()
