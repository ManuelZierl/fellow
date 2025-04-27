import json
from typing import Optional

from pydantic import ValidationError

from fellow.clients.Client import Client
from fellow.clients.OpenAIClient import FunctionResult
from fellow.commands.Command import CommandContext
from fellow.utils.init_client import init_client
from fellow.utils.init_command import init_command
from fellow.utils.load_client import load_client
from fellow.utils.load_commands import load_commands
from fellow.utils.load_config import Config, load_config
from fellow.utils.log_message import clear_log, log_message
from fellow.utils.parse_args import parse_args


def main() -> None:
    args = parse_args()
    config: Config = load_config(args)

    if args.command == "init-command":
        init_command(args.name, config.custom_commands_paths[0])
        return

    if args.command == "init-client":
        init_client(args.name, config.custom_commands_paths[0])
        return

    if config.task is None:
        raise ValidationError("[ERROR] Task is not defined in the configuration.")

    # Init commands
    commands = load_commands(config)

    # Build prompt
    introduction_prompt = config.introduction_prompt
    introduction_prompt = introduction_prompt.replace("{{TASK}}", config.task)
    first_message = (
        config.planning.prompt if config.planning.active else config.first_message
    )

    # Logging
    clear_log(config)
    log_message(config, name="Instruction", color=0, content=introduction_prompt)
    log_message(config, name="Instruction", color=0, content=first_message)

    # Init AI client
    client: Client = load_client(system_content=introduction_prompt, config=config)
    context: CommandContext = {"ai_client": client, "config": config}

    # Prepare OpenAI functions
    functions_schema = [client.get_function_schema(cmd) for cmd in commands.values()]

    # === Start Loop ===
    message = first_message
    function_result: Optional[FunctionResult] = None

    steps = 0
    while True:
        # 1. Call OpenAI
        chat_result = client.chat(
            message=message, function_result=function_result, functions=functions_schema
        )
        reasoning, func_name, func_args = (
            chat_result["message"],
            chat_result["function_name"],
            chat_result["function_args"],
        )

        # 2. Log assistant reasoning (if any)
        if reasoning and reasoning.strip():
            print("AI:", reasoning.strip())
            log_message(config, name="AI", color=1, content=reasoning)

        if config.log.active and func_name and func_args:
            print("AI:", func_name, func_args)
            log_message(
                config,
                name="AI",
                color=1,
                content=json.dumps(
                    {"function_name": func_name, "arguments": json.loads(func_args)}
                ),
                language="json",
            )

        if reasoning and (
            reasoning.strip() == "END" or reasoning.strip().endswith("END")
        ):
            client.store_memory("memory.json")
            break

        # 3. If a function is called, run it and prepare result
        if func_name is not None and func_args:
            if func_name not in commands:
                # Give error feedback to AI
                message = f"[ERROR] Unknown function: {func_name}"
                log_message(config, name="Output", color=2, content=message)
            else:
                command_output = commands[func_name].run(func_args, context)

                # Log output of the command
                log_message(
                    config,
                    name="Output",
                    color=2,
                    content=command_output,
                    language="txt",
                )

                # Prepare for next loop
                message = ""
                function_result = {"name": func_name, "output": command_output}
        else:
            # No function call, continue reasoning
            message = ""
            function_result = None

        steps += 1
        if config.steps_limit and steps >= config.steps_limit:
            log_message(
                config,
                name="SYSTEM",
                color=1,
                content="[END] Maximum number of steps reached.",
            )
            break


if __name__ == "__main__":
    main()
