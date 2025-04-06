import argparse
from typing import Dict

from fellow.clients.OpenAIClient import OpenAIClient
from fellow.commands import ALL_COMMANDS
from fellow.commands.command import CommandContext, Command
from fellow.utils.format_message import format_output_message
from fellow.utils.load_config import load_config
from fellow.utils.log_message import log_message, clear_log


def main():
    parser = argparse.ArgumentParser(description="Fellow CLI Tool")
    parser.add_argument("--config", help="Path to the optional yml config file")
    parser.add_argument("--task", help="The task fellow should perform")
    parser.add_argument("--log", help="Path to the .md file where the memory should be stored")
    parser.add_argument("--commands", nargs="*", help="List of commands to be used")
    args = parser.parse_args()

    config = load_config(args)

    # Init commands
    commands: Dict[str, Command] = {
        name: command for name, command in ALL_COMMANDS.items()
        if name in config["commands"]
    }

    if config.get("planning", {}).get("active"):
        commands["make_plan"] = ALL_COMMANDS["make_plan"]

    # Build prompt
    introduction_prompt = config["introduction_prompt"]
    introduction_prompt = introduction_prompt.replace("{{TASK}}", config["task"])
    first_message = config["planning"]["prompt"] if config.get("planning", {}).get(
        "active") else "Starting now. First command?"

    # Logging
    clear_log(config)
    log_message(config, name="Instruction", color=0, content=introduction_prompt, formatter=format_output_message)
    log_message(config, name="Instruction", color=0, content=first_message, formatter=format_output_message)

    # Init AI client
    openai_client = OpenAIClient(
        system_content=introduction_prompt,
        memory_max_tokens=config["openai_config"]["memory_max_tokens"],
        summary_memory_max_tokens=config["openai_config"]["summary_memory_max_tokens"],
        model=config["openai_config"]["model"],
    )
    context = CommandContext(ai_client=openai_client)

    # Prepare OpenAI functions
    functions_schema = [cmd.openai_schema() for cmd in commands.values()]

    # === Start Loop ===
    message = first_message
    function_result = None

    while True:
        # 1. Call OpenAI
        reasoning, func_name, func_args = openai_client.chat(
            message=message,
            function_result=function_result,
            functions=functions_schema
        )

        # 2. Log assistant reasoning (if any)
        if reasoning and reasoning.strip():
            print("AI:", reasoning.strip())
            log_message(config, name="AI", color=1, content=reasoning)

        if func_name and func_args:
            print("FUNCTION CALL:", func_name, func_args)
            log_message(config, name="Function Call", color=3, content=f"Calling {func_name} with args: {func_args}")

        if reasoning and (reasoning.strip() == "END" or reasoning.endswith("END")):
            openai_client.store_memory("memory.json")
            break

        # 3. If a function is called, run it and prepare result
        if func_name:
            if func_name not in commands:
                # Give error feedback to ai
                message = f"[ERROR] Unknown function: {func_name}"
                log_message(config, name="Output", color=2, content=message, formatter=format_output_message)
            else:
                # todo: not logging the function call
                command_output = commands[func_name].run(func_args, context)

                # Log output of the command
                print("PROMPT:", command_output.splitlines()[0] + "...")
                log_message(config, name="Output", color=2, content=command_output, formatter=format_output_message)

                # Prepare for next loop
                message = ""
                function_result = (func_name, command_output)
        else:
            # No function call, continue reasoning
            message = ""
            function_result = None



if __name__ == "__main__":
    main()
