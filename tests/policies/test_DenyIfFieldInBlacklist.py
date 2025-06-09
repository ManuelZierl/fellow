import json
import os
import tempfile
from types import SimpleNamespace

import pytest

from fellow.commands import CreateFileInput, ListFilesInput, create_file, list_files
from fellow.commands.Command import Command
from fellow.policies import DenyIfFieldInBlacklist, DenyIfFieldInBlacklistConfig


@pytest.fixture
def policy():
    config = DenyIfFieldInBlacklistConfig(
        fields=["filepath"], blacklist=["*.secret", "*/do_not_edit/*"]
    )
    return DenyIfFieldInBlacklist(config)


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("main.py", "[OK] Created file"),
        ("notes/plan.secret", "Denied by pattern '*.secret'"),
        ("project/do_not_edit/config.yml", "Denied by pattern '*/do_not_edit/*'"),
        ("safe/file.txt", "[OK] Created file"),
    ],
)
def test_deny_if_field_in_blacklist_check(policy, filename, expected):
    with tempfile.TemporaryDirectory() as tmpdir:
        command = Command(CreateFileInput, create_file, [policy])
        result = command.run(
            json.dumps({"filepath": os.path.join(tmpdir, filename)}), None
        )
    assert expected in result


def test_policy_deny_if_field_in_blacklist_check_invalid_field(policy):
    command = Command(ListFilesInput, list_files, [policy])
    result = command.run(json.dumps({"max_depth": 1}), None)
    assert "Denied" not in result
