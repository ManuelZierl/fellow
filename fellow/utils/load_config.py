import importlib.resources as pkg_resources
from argparse import Namespace
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.v1.utils import deep_update

import fellow


class PlanningConfig(BaseModel):
    active: bool
    prompt: str


class LogConfig(BaseModel):
    active: bool
    spoiler: bool
    filepath: str

    @field_validator("filepath")
    def must_be_markdown(cls, v: str) -> str:
        if not v.endswith(".md"):
            raise ValueError("Log file must be a .md extension")
        return v


class ClientConfig(BaseModel):
    client: str
    config: Optional[Dict[str, Any]] = {}


class Config(BaseModel):
    introduction_prompt: str
    first_message: str
    task: Optional[str]
    log: LogConfig
    ai_client: ClientConfig
    commands: List[str]
    planning: PlanningConfig
    steps_limit: Optional[int]
    custom_commands_paths: List[str]
    custom_clients_paths: List[str]

    # todo: model_config = ConfigDict(extra="forbid")


def extract_cli_overrides(args: Namespace) -> Dict[str, Any]:
    """
    Converts CLI args into a nested dict suitable for merging into config.
    """
    overrides: Dict[str, Any] = {}

    for key, value in vars(args).items():
        if value is None:
            continue

        # Support dotted keys like 'log.filepath'
        parts = key.split(".")
        current = overrides
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    return overrides


def load_config(args: Namespace) -> Config:
    """
    Load the configuration from the default config file and merge it with
    any user-provided config file and CLI arguments.
    """
    with (
        pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f
    ):
        config_dict: Dict[str, Any] = yaml.safe_load(f)

    if args.config:
        with open(args.config, "r") as file:
            user_config = yaml.safe_load(file)
            config_dict = deep_update(config_dict, user_config)

    cli_config = extract_cli_overrides(args)
    config_dict = deep_update(config_dict, cli_config)
    return Config.model_validate(config_dict)
