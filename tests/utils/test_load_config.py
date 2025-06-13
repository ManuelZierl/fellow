import importlib.resources as pkg_resources
import os
import re
import tempfile
from argparse import Namespace
from pathlib import Path

import pytest
import yaml

import fellow
from fellow.utils.load_config import Config, load_config


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
        default_policies=[],
        **{
            key: None
            for key in [
                "introduction_prompt",
                "first_message",
                "log.filepath",
                "log.active",
                "log.spoiler",
                "planning.active",
                "planning.prompt",
                "commands",
                "steps_limit",
            ]
        },
    )
    config = load_config(args)
    assert config.task == "a valid task"
    assert config.log.filepath.endswith(".md")
    assert (
        config.ai_client.config["model"]
        == default_config["ai_client"]["config"]["model"]
    )


def test_cli_override():
    args = Namespace(
        config=None,
        task="CLI Task",
        introduction_prompt="Intro: {{TASK}}",
        first_message="Ignore",
        default_policies=[],
        **{
            "log.filepath": "custom.md",
            "ai_client.config": {"model": "gpt-super"},
            "log.active": True,
            "log.spoiler": False,
            "planning.active": True,
            "planning.prompt": "CLI plan",
            "commands": {"list": {}, "run": {}},
        },
    )
    config = load_config(args)
    assert config.task == "CLI Task"
    assert config.introduction_prompt == "Intro: {{TASK}}"
    assert config.first_message == "Ignore"
    assert config.log.filepath == "custom.md"
    assert config.ai_client.config["model"] == "gpt-super"
    assert config.log.active is True
    assert config.log.spoiler is False
    assert config.planning.active is True
    assert config.planning.prompt == "CLI plan"
    assert set(config.commands.keys()) == {"list", "run"}


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
                "ai_client.client",
                "ai_client.config",
                "planning.active",
                "planning.prompt",
                "commands",
            ]
        },
    )
    config = load_config(args)
    assert config.task == "Overridden"
    os.unlink(tmp_path)


def test_config_fields_are_documented():
    repo_root = Path(__file__).resolve().parent.parent.parent
    doc_path = repo_root / "docs" / "configuration" / "index.md"
    assert doc_path.exists(), "Documentation file not found"

    # 1. Extract field names from the Config model
    config_fields = set(Config.model_fields.keys())

    # 2. Extract documented fields from markdown headers like: ### `field_name`
    content = doc_path.read_text(encoding="utf-8")
    documented_fields = {
        match.group(1)
        for match in re.finditer(r"^###\s+`([a-zA-Z0-9_]+)`", content, re.MULTILINE)
    }

    # 3. Compare sets
    undocumented = config_fields - documented_fields
    extra = documented_fields - config_fields

    error = ""
    if undocumented:
        error += "\nUndocumented fields:\n" + "\n".join(
            f"- {f}" for f in sorted(undocumented)
        )
    if extra:
        error += "\nDocumented but not in Config:\n" + "\n".join(
            f"- {f}" for f in sorted(extra)
        )

    if error:
        raise AssertionError(error)
