import argparse
from typing import Dict, Tuple, Type

from fellow.clients.CommandClient import CommandClient
from fellow.clients.OpenAIClient import OpenAIClient
from fellow.commands import ALL_COMMANDS, CommandInput, CommandHandler, generate_commands_description, MakePlanInput, \
    make_plan
from fellow.commands.command import CommandContext
from fellow.utils.extract_commands import extract_commands
from fellow.utils.format_message import format_output_message
from fellow.utils.load_config import load_config
from fellow.utils.log_message import log_message, clear_log


def main():
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")

    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--log", help="Path to the .md file where the memory should be stored")
    parser.add_argument("--commands", nargs="*", help="List of commands to be used")
    # introduction_prompt
    # openai_config .memory_max_tokens .summary_memory_max_tokens .model
    # additional_commands -> additional commands to be added

    args = parser.parse_args()
    config = load_config(args)
    first_message = "Starting now. First command?"

    commands: Dict[str, Tuple[Type[CommandInput], CommandHandler]] = {
        command_name: command for command_name, command in ALL_COMMANDS.items()
        if command_name in config["commands"]
    }
    if config.get("planning") and config.get("planning", {}).get("active", False):
        commands.update({
            "make_plan": (MakePlanInput, make_plan)
        })
        first_message = config["planning"]["prompt"]
    commands_description = generate_commands_description(commands)

    introduction_prompt = config["introduction_prompt"]
    introduction_prompt = introduction_prompt.replace("{{TASK}}", config["task"])
    introduction_prompt = introduction_prompt.replace("{{COMMANDS}}", commands_description)

    # Clear the log file
    clear_log(config)
    log_message(config, name="Instruction", color=0, content=introduction_prompt)

    openai_client = OpenAIClient(
        system_content=introduction_prompt,
        memory_max_tokens=config["openai_config"]["memory_max_tokens"],
        summary_memory_max_tokens=config["openai_config"]["summary_memory_max_tokens"],
        model=config["openai_config"]["model"],
    )

    context = CommandContext(
        ai_client=openai_client
    )
    command_client = CommandClient(context)

    log_message(config, name="Instruction", color=0, content=first_message)
    ai_response = openai_client.chat(first_message)
    log_message(config, name="AI", color=1, content=ai_response)

    while True:
        extracted_commands = extract_commands(ai_response, commands)

        if isinstance(extracted_commands, str):
            prompt_response = extracted_commands
        else:
            responses = []
            for cmd_input, handler in extracted_commands:
                try:
                    # result = handler(cmd_input, context=command_client.context)
                    result = command_client.run(cmd_input, handler)
                except Exception as e:
                    result = f"[ERROR] Command execution failed: {e}"
                responses.append(result)
            prompt_response = "\n\n".join(responses)
        print("PROMPT:", prompt_response.split("\n")[0] + "...")
        log_message(config, name="Output", color=2, content=prompt_response, formatter=format_output_message)

        ai_response = openai_client.chat(prompt_response)
        print("AI:", ai_response)
        log_message(config, name="AI", color=1, content=ai_response)

        if ai_response.endswith("END"):
            openai_client.store_memory("memory.json")
            break


if __name__ == "__main__":
    main()
