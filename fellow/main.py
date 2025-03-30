import argparse
import yaml
import importlib.resources as pkg_resources
from pydantic.v1.utils import deep_update
import fellow
from fellow.clients.CommandClient import CommandClient
from fellow.commands import COMMAND_DESCRIPTION

from fellow.clients.OpenAIClient import OpenAIClient
from fellow.clients.PromptClient import PromptClient


def main():
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")

    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument("--log", help="Path to the json file where the memory should be stored")
    args = parser.parse_args()

    with pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f:
        config = yaml.safe_load(f)

    if args.config:
        with open(args.config, 'r') as file:
            user_config = yaml.safe_load(file)
            config = deep_update(config, user_config)

    if args.task:
        config["task"] = args.task

    introduction_prompt = config["introduction_prompt"]
    introduction_prompt = introduction_prompt.replace("{{TASK}}", config["task"])
    introduction_prompt = introduction_prompt.replace("{{COMMANDS}}", COMMAND_DESCRIPTION)

    openai_client = OpenAIClient(
        system_content=introduction_prompt,
        memory_max_tokens=config["openai_config"]["memory_max_tokens"],
        summary_memory_max_tokens=config["openai_config"]["summary_memory_max_tokens"],
        model=config["openai_config"]["model"],
    )

    command_client = CommandClient()

    first_message = "Starting now. First command?"
    ai_response = openai_client.chat(first_message)
    while True:
        print("AI:", ai_response)
        prompt_response = command_client.run(ai_response)
        print("Prompt:", prompt_response)
        ai_response = openai_client.chat(prompt_response)
        if args.log:
            openai_client.store_memory(args.log)
        if ai_response == "END":
            break






if __name__ == "__main__":
    main()

