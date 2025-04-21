import argparse
import json
from argparse import Namespace
from typing import Any, Dict


def str2bool(v: str) -> bool:
    """
    Convert a string to a boolean value.
    """
    return str(v).lower() in ("yes", "true", "t", "1")


def json_string_to_dict(json_string: str) -> Dict[str, Any]:
    """
    Convert a JSON string to a dictionary.
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string provided.")


def parse_args() -> Namespace:
    """
    Parse command line arguments for the Fellow CLI tool.
    """
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    init_command_parser = subparsers.add_parser(
        "init-command", help="Create a new custom command"
    )
    init_command_parser.add_argument(
        "name", help="The name of the new command to create"
    )

    init_client_parser = subparsers.add_parser(
        "init-client", help="Create a new custom client"
    )
    init_client_parser.add_argument("name", help="The name of the new client to create")

    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument(
        "--introduction_prompt", help="The prompt with which the AI will be initialized"
    )
    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--log.filepath", help="Log file path")
    parser.add_argument("--log.active", type=str2bool, help="Enable or disable logging")
    parser.add_argument("--log.spoiler", type=str2bool, help="Wrap logs in spoilers")
    parser.add_argument(
        "--ai_client.client", help="AI provider (e.g. openai, gemini or custom client)"
    )
    parser.add_argument(
        "--ai_client.config",
        type=json_string_to_dict,
        help="Override AI config as JSON string",
    )
    parser.add_argument(
        "--planning.active", type=str2bool, help="Enable or disable planning"
    )
    parser.add_argument("--planning.prompt", help="Define the prompt for planning")
    parser.add_argument("--commands", nargs="*", help="List of commands to be used")
    parser.add_argument("--steps_limit", type=int, help="Limit the number of steps")
    parser.add_argument(
        "--custom_commands_paths", nargs="*", help="Paths to custom commands"
    )
    parser.add_argument(
        "--custom_clients_paths", nargs="*", help="Paths to custom clients"
    )

    return parser.parse_args()
