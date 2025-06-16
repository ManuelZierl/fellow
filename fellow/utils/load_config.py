import importlib.resources as pkg_resources
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import yaml
from pydantic import BaseModel, model_validator
from pydantic.v1.utils import deep_update

import fellow


class PlanningConfig(BaseModel):
    active: bool
    prompt: str


class LogConfig(BaseModel):
    active: bool
    spoiler: bool
    filepath: Optional[Path]

    @model_validator(mode="after")
    def validate_config(self) -> "LogConfig":
        if self.active:
            if not self.filepath:
                raise ValueError("Log is active but no filepath provided")
            if not self.filepath.suffix == ".md":
                raise ValueError("Log filepath must end with .md")
        return self


class MemoryConfig(BaseModel):
    log: bool
    filepath: Optional[Path]

    @model_validator(mode="after")
    def validate_config(self) -> "MemoryConfig":
        if self.log:
            if not self.filepath:
                raise ValueError("Memory log is active but no filepath provided")
            if not self.filepath.suffix == ".json":
                raise ValueError("Memory filepath must end with '.json'")
        return self


class MetadataConfig(BaseModel):
    log: bool
    filepath: Optional[Path]

    @model_validator(mode="after")
    def validate_config(self) -> "MetadataConfig":
        if self.log:
            if not self.filepath:
                raise ValueError("Metadata log is active but no filepath provided")
            if not self.filepath.suffix == ".json":
                raise ValueError("Metadata filepath must end with '.json'")
        return self


class ClientConfig(BaseModel):
    client: str
    config: Optional[Dict[str, Any]] = {}


class PolicyConfig(BaseModel):
    name: str
    config: Optional[Dict] = {}


class CommandConfig(BaseModel):
    policies: List[PolicyConfig] = []


class Config(BaseModel):
    introduction_prompt: str
    first_message: str
    task: Optional[str]
    task_id: Optional[UUID]
    log: LogConfig
    memory: MemoryConfig
    metadata: MetadataConfig
    ai_client: ClientConfig
    commands: Dict[str, CommandConfig]
    default_policies: List[PolicyConfig]
    planning: PlanningConfig
    steps_limit: Optional[int]
    custom_commands_paths: List[Path]
    custom_clients_paths: List[Path]
    custom_policies_paths: List[Path]
    secrets_path: Path


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
    Loads and merges the full configuration for Fellow from multiple sources.

    The final config is built in this order of precedence:
    1. Default config file shipped with the package (`default_fellow_config.yml`)
    2. Optional user-supplied config file (`--config` argument)
    3. CLI overrides (flattened via `extract_cli_overrides()`)

    Special handling:
    - The `commands` section is excluded from deep merging and completely replaced
      if specified via CLI arguments.

    :param args: Parsed CLI arguments (typically from `argparse.Namespace`)
    :return: A validated `Config` object.
    :raises ValidationError: If the resulting configuration does not match the schema.
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

    for deep_update_excluded_key in ["commands"]:
        if deep_update_excluded_key in cli_config:
            config_dict[deep_update_excluded_key] = cli_config[deep_update_excluded_key]

    return Config.model_validate(config_dict)
