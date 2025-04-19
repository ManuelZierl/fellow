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
    todo: doc
    todo: test
    """
    target_dir = Path(target)
    function_name = command_name
    class_name = (
        "".join(part.capitalize() for part in command_name.split("_")) + "Input"
    )
    print(target_dir)
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
