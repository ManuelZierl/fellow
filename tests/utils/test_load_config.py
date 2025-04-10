import importlib.resources as pkg_resources
import os
import tempfile
from argparse import Namespace

import pytest
import yaml

import fellow
from fellow.utils.load_config import load_config


@pytest.fixture
def default_config():
    with (
        pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f
    ):
        return yaml.safe_load(f)


def test_loads_default_config(default_config):
    args = Namespace(
        config=None,
        task="a valid task",
        **{
            key: None
            for key in [
                "introduction_prompt",
                "first_message",
                "log.filepath",
                "log.active",
                "log.spoiler",
                "openai_config.memory_max_tokens",
                "openai_config.summary_memory_max_tokens",
                "openai_config.model",
                "planning.active",
                "planning.prompt",
                "commands",
            ]
        },
    )
    config = load_config(args)
    assert config.task == "a valid task"
    assert config.log.filepath.endswith(".md")
    assert config.openai_config.model == default_config["openai_config"]["model"]


def test_cli_override():
    args = Namespace(
        config=None,
        task="CLI Task",
        introduction_prompt="Intro: {{TASK}}",
        first_message="Ignore",
        **{
            "log.filepath": "custom.md",
            "openai_config.model": "gpt-super",
            "log.active": True,
            "log.spoiler": False,
            "planning.active": True,
            "planning.prompt": "CLI plan",
            "commands": ["list", "run"],
        },
    )
    config = load_config(args)
    assert config.task == "CLI Task"
    assert config.introduction_prompt == "Intro: {{TASK}}"
    assert config.first_message == "Ignore"
    assert config.log.filepath == "custom.md"
    assert config.openai_config.model == "gpt-super"
    assert config.log.active is True
    assert config.log.spoiler is False
    assert config.planning.active is True
    assert config.planning.prompt == "CLI plan"
    assert config.commands == ["list", "run"]


def test_user_config_override():
    user_config = {"task": "Overridden"}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yml", mode="w") as tmp:
        yaml.dump(user_config, tmp)
        tmp_path = tmp.name

    args = Namespace(
        config=tmp_path,
        **{
            key: None
            for key in [
                "task",
                "introduction_prompt",
                "first_message",
                "log.filepath",
                "log.active",
                "log.spoiler",
                "openai_config.memory_max_tokens",
                "openai_config.summary_memory_max_tokens",
                "openai_config.model",
                "planning.active",
                "planning.prompt",
                "commands",
            ]
        },
    )
    config = load_config(args)
    assert config.task == "Overridden"
    os.unlink(tmp_path)
