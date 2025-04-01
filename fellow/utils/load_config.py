import yaml
from pydantic.v1.utils import deep_update

import fellow
import importlib.resources as pkg_resources


def load_config(args):
    with pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f:
        config = yaml.safe_load(f)

    if args.config:
        with open(args.config, 'r') as file:
            user_config = yaml.safe_load(file)
            config = deep_update(config, user_config)

    # Override from CLI args
    for key in ["task", "log"]:
        value = getattr(args, key)
        if value:
            config[key] = value

    if config.get("log") and not config["log"].endswith(".md"):
        raise ValueError("Log file must be a .md extension")

    return config
