import os
import tempfile
from pathlib import Path

import pytest

from fellow.utils.secrets import (
    add_secret,
    clear_secrets,
    ensure_fellow_gitignore,
    load_secrets,
    remove_secret,
)


@pytest.fixture
def secrets_file_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / ".secrets"
        yield path


def test_add_and_load_secret(monkeypatch, secrets_file_tmpdir):
    key = "MY_SECRET"
    value = "supersecret"
    add_secret(value, key, secrets_file_tmpdir)
    monkeypatch.delenv(key, raising=False)
    load_secrets(secrets_file_tmpdir)
    assert os.environ[key] == value


def test_add_secret_preserves_comments(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("# comment\nEXISTING=old\n")
    add_secret("newval", "NEWKEY", secrets_file_tmpdir)
    content = secrets_file_tmpdir.read_text()
    assert content == "# comment\nEXISTING=old\nNEWKEY=newval\n"


def test_add_secret_updates_existing(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("OTHER=other\nEXISTING=old\n")
    add_secret("updated", "EXISTING", secrets_file_tmpdir)
    content = secrets_file_tmpdir.read_text()
    assert "EXISTING=updated" in content


def test_remove_secret(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("ONE=1\nTWO=2\nTHREE=3\n")
    remove_secret("TWO", secrets_file_tmpdir)
    content = secrets_file_tmpdir.read_text()
    assert "TWO=2" not in content
    assert "ONE=1" in content
    assert "THREE=3" in content


def test_clear_secrets(secrets_file_tmpdir):
    secrets_file_tmpdir.write_text("A=1\nB=2\n")
    clear_secrets(secrets_file_tmpdir)
    assert secrets_file_tmpdir.read_text() == ""


def test_load_secrets_missing_file(tmp_path, monkeypatch):
    secrets_path = tmp_path / ".secrets"
    monkeypatch.delenv("FOO", raising=False)
    load_secrets(secrets_path)


def test_load_secrets_ignores_comments_and_blank_lines(
    monkeypatch, secrets_file_tmpdir
):
    secrets_file_tmpdir.write_text("\n# This is a comment\nMY_SECRET=value\n\n")
    monkeypatch.delenv("MY_SECRET", raising=False)
    load_secrets(secrets_file_tmpdir)
    assert os.environ["MY_SECRET"] == "value"


def test_load_secrets_does_not_override_existing_env(secrets_file_tmpdir, monkeypatch):
    os.environ["MY_KEY"] = "existing"
    secrets_file_tmpdir.write_text("MY_KEY=newval\n")
    load_secrets(secrets_file_tmpdir)
    assert os.environ["MY_KEY"] == "existing"


def test_invalid_secrets_doesnt_fail(secrets_file_tmpdir, monkeypatch):
    secrets_file_tmpdir.write_text("INVALID_LINE\nANOTHER_INVALID_LINE\n")
    monkeypatch.delenv("MY_KEY", raising=False)
    load_secrets(secrets_file_tmpdir)
    assert "MY_KEY" not in os.environ


def test_remove_secret_path_not_found(secrets_file_tmpdir):
    non_existent_path = secrets_file_tmpdir.parent / "non_existent_secrets"
    remove_secret("NON_EXISTENT_KEY", non_existent_path)
    assert not non_existent_path.exists()


def test_add_secret_creates_file_and_gitignore(tmp_path):
    # Setup: simulate a project root
    project_root = tmp_path
    fellow_dir = project_root / ".fellow"
    secrets_path = fellow_dir / ".secrets"
    gitignore_path = fellow_dir / ".gitignore"

    # Change to the temporary directory for test isolation
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        # 1. Add a secret
        add_secret("my-value", "MY_KEY", secrets_path)

        # 2. Assert secret is stored correctly
        contents = secrets_path.read_text(encoding="utf-8")
        assert "MY_KEY=my-value\n" in contents

        # 3. Assert .gitignore is created
        assert gitignore_path.exists()
        gitignore_contents = gitignore_path.read_text(encoding="utf-8")
        assert ".secrets" in gitignore_contents

    finally:
        os.chdir(original_cwd)


def test_ensure_fellow_gitignore_creates_file(tmp_path):
    # Simulate `.fellow/.secrets` path
    secrets_path = tmp_path / ".fellow" / ".secrets"
    secrets_path.parent.mkdir(parents=True, exist_ok=True)

    # Run the function (creates .gitignore)
    ensure_fellow_gitignore(secrets_path)

    gitignore_path = secrets_path.parent / ".gitignore"
    assert gitignore_path.exists()

    contents = gitignore_path.read_text()
    assert ".secrets" in contents


def test_ensure_fellow_gitignore_appends_if_missing(tmp_path):
    # Setup .gitignore with another entry
    fellow_dir = tmp_path / ".fellow"
    fellow_dir.mkdir(parents=True, exist_ok=True)
    gitignore_path = fellow_dir / ".gitignore"
    gitignore_path.write_text("other-entry\n")

    secrets_path = fellow_dir / ".secrets"

    ensure_fellow_gitignore(secrets_path)

    contents = gitignore_path.read_text()
    assert ".secrets" in contents
    assert "other-entry" in contents


def test_ensure_fellow_gitignore_skips_if_already_present(tmp_path):
    fellow_dir = tmp_path / ".fellow"
    fellow_dir.mkdir(parents=True, exist_ok=True)
    gitignore_path = fellow_dir / ".gitignore"
    gitignore_path.write_text(".secrets\n")

    secrets_path = fellow_dir / ".secrets"

    # Record file state before
    before = gitignore_path.read_text()

    ensure_fellow_gitignore(secrets_path)

    after = gitignore_path.read_text()
    assert after == before  # No duplication or change
