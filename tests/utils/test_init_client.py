from pathlib import Path

import pytest

from fellow.utils.init_client import init_client


def test_init_client_creates_expected_file(tmp_path: Path):
    # Arrange
    client_name = "local"
    target_dir = tmp_path / "clients"

    # Act
    result_path = init_client(client_name, target_dir)

    # Assert: File created
    assert result_path.exists()
    assert result_path.name == "LocalClient.py"

    content = result_path.read_text()

    # Assert: Content includes generated config and client classes
    assert "class LocalClientConfig(ClientConfig):" in content
    assert "class LocalClient(Client[LocalClientConfig]):" in content
    assert "def chat(" in content

    # Assert: Raises on duplicate creation
    with pytest.raises(FileExistsError):
        init_client(client_name, target_dir)
