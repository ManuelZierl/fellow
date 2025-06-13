import json
import uuid
from typing import Optional

from pydantic import ValidationError

from fellow.clients.Client import Client
from fellow.clients.OpenAIClient import FunctionResult
from fellow.commands.Command import CommandContext
from fellow.utils.init_client import init_client
from fellow.utils.init_command import init_command
from fellow.utils.init_policy import init_policy
from fellow.utils.load_client import load_client
from fellow.utils.load_commands import load_commands
from fellow.utils.load_config import Config, load_config
from fellow.utils.log_message import clear_log, log_message
from fellow.utils.parse_args import parse_args
from fellow.utils.secrets import add_secret, clear_secrets, load_secrets, remove_secret


def main() -> None:
    args = parse_args()
    config: Config = load_config(args)

    # Handle special commands
    dispatch_map = {
        "init-command": lambda: init_command(
            args.name, config.custom_commands_paths[0]
        ),
        "init-client": lambda: init_client(args.name, config.custom_commands_paths[0]),
        "init-policy": lambda: init_policy(args.name, config.custom_policies_paths[0]),
        "add-secret": lambda: add_secret(args.value, args.key, config.secrets_path),
        "remove-secret": lambda: remove_secret(args.key, config.secrets_path),
        "clear-secrets": lambda: clear_secrets(config.secrets_path),
    }
    if args.command in dispatch_map:
        dispatch_map[args.command]()
        return

    # Task must be defined now!
    if config.task is None:
        raise ValidationError("[ERROR] Task is not defined in the configuration.")

    # Generate a new task ID if not provided
    if config.task_id is None:
        config.task_id = uuid.uuid4()

    # Replace placeholders in paths
    if config.log.filepath is not None:
        config.log.filepath = config.log.filepath.replace(
            str(config.log.filepath).replace("{{task_id}}", config.task_id.hex)
        )

    if config.memory.filepath is not None:
        config.memory.filepath = config.memory.filepath.replace(
            str(config.memory.filepath).replace("{{task_id}}", config.task_id.hex)
        )

    if config.metadata.filepath is not None:
        config.metadata.filepath = config.metadata.filepath.replace(
            str(config.metadata.filepath).replace("{{task_id}}", config.task_id.hex)
        )

    # Load secrets
    load_secrets(config.secrets_path)

    # Init commands
    commands = load_commands(config)

    # Build prompt
    config.introduction_prompt = config.introduction_prompt.replace(
        "{{TASK}}", config.task
    )
    first_message = (
        config.planning.prompt if config.planning.active else config.first_message
    )

    # store metadata
    if config.metadata.log and config.metadata.filepath:
        with open(config.metadata.filepath, "w") as f:
            f.write(config.model_dump_json(indent=2))

    # Logging
    clear_log(config)
    log_message(config, name="Instruction", color=0, content=config.introduction_prompt)
    log_message(config, name="Instruction", color=0, content=first_message)

    # Init AI client
    client: Client = load_client(
        system_content=config.introduction_prompt, config=config
    )
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

        if func_name and func_args:
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
            if config.memory.log:
                client.store_memory(str(config.memory.filepath))
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
