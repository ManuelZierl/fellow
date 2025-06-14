from pathlib import Path

import pytest

from fellow.utils.init_policy import init_policy


def test_init_policy_creates_expected_file(tmp_path: Path):
    # Arrange
    policy_name = "deny_large_file"
    target_dir = tmp_path / "policies"

    # Act
    result_path = init_policy(policy_name, target_dir)

    # Assert: File created
    assert result_path.exists()
    assert result_path.name == "deny_large_file.py"

    content = result_path.read_text()

    # Assert: Generated config and policy classes are present
    assert "class DenyLargeFileConfig(PolicyConfig):" in content
    assert "class DenyLargeFile(Policy[DenyLargeFileConfig]):" in content
    assert "def check(" in content

    # Assert: Duplicate file raises error
    with pytest.raises(FileExistsError):
        init_policy(policy_name, target_dir)
