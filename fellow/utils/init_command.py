from pathlib import Path

COMMAND_TEMPLATE = '''\
from fellow.commands.command import CommandContext, CommandInput
from pydantic import Field


class {class_name}(CommandInput):
    example_field: str = Field(..., description="An example input field.")


def {function_name}(args: {class_name}, context: CommandContext) -> str:
    """Brief description of what this command does."""
    return f"Received: {{args.example_field}}"

'''


def init_command(command_name: str, target: str) -> Path:
    """
    Generates a new boilerplate Python file for a custom Fellow command.
    The generated file contains a CommandInput class and a corresponding handler function
    whose names are derived from `command_name`. For example, `say_hello` becomes:
    - class: SayHelloInput
    - function: say_hello
    The command is written to `<target>/<command_name>.py`, and the directory is created if it doesn't exist.
    """
    target_dir = Path(target)
    function_name = command_name
    class_name = (
        "".join(part.capitalize() for part in command_name.split("_")) + "Input"
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{command_name}.py"

    if file_path.exists():
        raise FileExistsError(f"Command file already exists: {file_path}")

    content = COMMAND_TEMPLATE.format(
        class_name=class_name,
        function_name=function_name,
    )

    file_path.write_text(content)
    return file_path
