import importlib.resources as pkg_resources
from argparse import Namespace
from typing import List, Optional, TypedDict

import yaml
from pydantic.v1.utils import deep_update

import fellow


class OpenAIConfig(TypedDict, total=False):
    memory_max_tokens: int
    summary_memory_max_tokens: int
    model: str  # todo: make it literal?


class PlanningConfig(TypedDict, total=False):
    active: bool
    prompt: str


class Config(TypedDict, total=False):
    introduction_prompt: str
    task: Optional[str]
    log: Optional[str]
    openai_config: OpenAIConfig
    commands: List[str]
    planning: PlanningConfig


def load_config(args: Namespace) -> Config:
    with (
        pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f
    ):
        config = yaml.safe_load(f)

    if args.config:
        with open(args.config, "r") as file:
            user_config = yaml.safe_load(file)
            config = deep_update(config, user_config)

    # Override from CLI args
    for key in ["task", "log", "commands"]:
        value = getattr(args, key)
        if value:
            config[key] = value

    if config.get("log") and not config["log"].endswith(".md"):
        raise ValueError("Log file must be a .md extension")

    return config
