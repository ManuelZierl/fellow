from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from fellow.utils.load_config import load_config


def write_yaml_file(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f)


# Sample config fixtures
default_config = {
    "task": "default",
    "log": "log.md",
    "openai_config": {},
    "commands": [],
}
user_config = {"task": "user", "openai_config": {"model": "gpt-4"}}


@patch("fellow.utils.load_config.pkg_resources.files")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="task: default\nlog: log.md\nopenai_config: {}",
)
def test_loads_default_config(mock_open_builtin, mock_files):
    mock_file = MagicMock()
    mock_file.open.return_value = mock_open_builtin.return_value
    mock_files.return_value.joinpath.return_value = mock_file

    args = SimpleNamespace(config=None, task=None, log=None, commands=None)
    config = load_config(args)

    assert config["task"] == "default"
    assert config["log"] == "log.md"
    assert isinstance(config["openai_config"], dict)


def test_merges_user_config(tmp_path):
    # Write default config to temp file in package path simulation
    default_config = {"task": "default", "log": "log.md", "openai_config": {}}
    default_config_path = tmp_path / "default_fellow_config.yml"
    write_yaml_file(default_config_path, default_config)

    # Write user config file
    user_config = {"task": "user", "openai_config": {"model": "gpt-4"}}
    user_config_path = tmp_path / "custom.yml"
    write_yaml_file(user_config_path, user_config)

    # Patch pkg_resources to return our temp file
    import fellow.utils.load_config as config_mod

    config_mod.pkg_resources.files = lambda _: tmp_path
    config_mod.pkg_resources.files.return_value = tmp_path  # just in case

    args = SimpleNamespace(
        config=str(user_config_path), task=None, log=None, commands=None
    )
    config = load_config(args)

    assert config["task"] == "user"
    assert config["openai_config"]["model"] == "gpt-4"


@patch("fellow.utils.load_config.pkg_resources.files")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="task: default\nlog: log.md\nopenai_config: {}",
)
def test_cli_overrides_all(mock_open_builtin, mock_files):
    mock_file = MagicMock()
    mock_file.open.return_value = mock_open_builtin.return_value
    mock_files.return_value.joinpath.return_value = mock_file

    args = SimpleNamespace(config=None, task="cli-task", log="cli.md", commands=None)
    config = load_config(args)

    assert config["task"] == "cli-task"
    assert config["log"] == "cli.md"


@patch("fellow.utils.load_config.pkg_resources.files")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="task: default\nlog: log.md\nopenai_config: {}",
)
def test_invalid_log_extension_raises(mock_open_builtin, mock_files):
    mock_file = MagicMock()
    mock_file.open.return_value = mock_open_builtin.return_value
    mock_files.return_value.joinpath.return_value = mock_file

    args = SimpleNamespace(config=None, task=None, log="log.txt", commands=None)

    with pytest.raises(ValueError, match="Log file must be a .md extension"):
        load_config(args)
