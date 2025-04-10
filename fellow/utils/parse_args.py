import argparse
from argparse import Namespace


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")
    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument(
        "--introduction_prompt", help="The prompt with which the AI will be initialized"
    )
    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--log.filepath", help="Log file path")
    parser.add_argument("--log.active", type=str2bool, help="Enable or disable logging")
    parser.add_argument("--log.spoiler", type=str2bool, help="Wrap logs in spoilers")
    parser.add_argument(
        "--openai_config.memory_max_tokens", type=int, help="Max tokens for memory"
    )
    parser.add_argument(
        "--openai_config.summary_memory_max_tokens",
        type=int,
        help="Max tokens for summary memory",
    )
    parser.add_argument("--openai_config.model", type=str, help="OpenAI model to use")
    parser.add_argument(
        "--planning.active", type=str2bool, help="Enable or disable planning"
    )
    parser.add_argument("--planning.prompt", help="Define the prompt for planning")
    parser.add_argument("--commands", nargs="*", help="List of commands to be used")
    return parser.parse_args()
