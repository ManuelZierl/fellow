import argparse
import yaml
import importlib.resources as pkg_resources
from pydantic.v1.utils import deep_update
import fellow
from fellow.clients.CommandClient import CommandClient
from fellow.clients.OpenAIClient import OpenAIClient
from fellow.commands import COMMAND_DESCRIPTION
from fellow.utils.format_message import format_message


def main():
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")

    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument("--log", help="Path to the .md file where the memory should be stored")
    args = parser.parse_args()

    with pkg_resources.files(fellow).joinpath("default_fellow_config.yml").open("r") as f:
        config = yaml.safe_load(f)

    if args.config:
        with open(args.config, 'r') as file:
            user_config = yaml.safe_load(file)
            config = deep_update(config, user_config)

    if args.task:
        config["task"] = args.task

    if args.log and not args.log.endswith(".md"):
        raise ValueError("Log file must be a .md extension")

    introduction_prompt = config["introduction_prompt"]
    introduction_prompt = introduction_prompt.replace("{{TASK}}", config["task"])
    introduction_prompt = introduction_prompt.replace("{{COMMANDS}}", COMMAND_DESCRIPTION)

    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            f.write(
                format_message(
                    name="Instruction",
                    color=0,
                    content=introduction_prompt,
                    language="txt",
                )
            )

    openai_client = OpenAIClient(
        system_content=introduction_prompt,
        memory_max_tokens=config["openai_config"]["memory_max_tokens"],
        summary_memory_max_tokens=config["openai_config"]["summary_memory_max_tokens"],
        model=config["openai_config"]["model"],
    )

    command_client = CommandClient()

    first_message = "Starting now. First command?"
    if args.log:
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(
                format_message(
                    name="Instruction",
                    color=0,
                    content=first_message,
                    language="txt",
                )
            )
    ai_response = openai_client.chat(first_message)
    if args.log:
        with open(args.log, "a", encoding="utf-8") as f:
            f.write(
                format_message(
                    name="AI",
                    color=1,
                    content=ai_response,
                    language="json",
                )
            )

    while True:
        prompt_response = command_client.run(ai_response)
        print("AI:", prompt_response)
        if args.log:
            with open(args.log, "a", encoding="utf-8") as f:
                f.write(
                    format_message(
                        name="Output",
                        color=2,
                        content=prompt_response,
                        language="txt",
                    )
                )
        ai_response = openai_client.chat(prompt_response)
        print("Prompt:", ai_response)
        if args.log:
            with open(args.log, "a", encoding="utf-8") as f:
                f.write(
                    format_message(
                        name="AI",
                        color=1,
                        content=ai_response,
                        language="json",
                    )
                )

        if ai_response == "END":
            break






if __name__ == "__main__":
    main()

