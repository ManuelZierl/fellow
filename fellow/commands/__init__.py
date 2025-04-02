from typing import Dict, Tuple, Type
import json
import inspect
from typing import Callable, get_type_hints

from fellow.commands.command import CommandInput, CommandHandler
from fellow.commands.create_file import CreateFileInput, create_file
from fellow.commands.delete_file import DeleteFileInput, delete_file
from fellow.commands.edit_file import EditFileInput, edit_file
from fellow.commands.get_code import GetCodeInput, get_code
from fellow.commands.list_definitions import ListDefinitionsInput, list_definitions
from fellow.commands.list_files import ListFilesInput, list_files
from fellow.commands.make_plan import MakePlanInput, make_plan
from fellow.commands.run_pytest import RunPytestInput, run_pytest
from fellow.commands.run_python import RunPythonInput, run_python
from fellow.commands.summarize_file import SummarizeFileInput, summarize_file
from fellow.commands.view_file import ViewFileInput, view_file


ALL_COMMANDS: Dict[str, Tuple[Type[CommandInput], CommandHandler]] = {
    "create_file": (CreateFileInput, create_file),
    "view_file": (ViewFileInput, view_file),
    "delete_file": (DeleteFileInput, delete_file),
    "edit_file": (EditFileInput, edit_file),
    "list_files": (ListFilesInput, list_files),
    "run_python": (RunPythonInput, run_python),
    "run_pytest": (RunPytestInput, run_pytest),
    "list_definitions": (ListDefinitionsInput, list_definitions),
    "get_code": (GetCodeInput, get_code),
    "make_plan": (MakePlanInput, make_plan),
    "summarize_file": (SummarizeFileInput, summarize_file)
}

def generate_commands_description(commands: Dict[str, Tuple[Type[CommandInput], CommandHandler]]) -> str:
    def extract_description(command_fn: Callable) -> dict:
        sig = inspect.signature(command_fn)
        param = list(sig.parameters.values())[0]
        model_cls = get_type_hints(command_fn).get(param.name)
        return {
            "command": command_fn.__name__,
            "description": (command_fn.__doc__ or "").strip(),
            "args": model_cls.command_schema()
        }

    lines = []

    for name, (input_cls, handler_fn) in commands.items():
        info = extract_description(handler_fn)

        lines.append(f"### {name}")
        if info["description"]:
            lines.append(info["description"])

        # Build JSON example with type placeholders
        args_example = {
            name: {
                arg: desc
                for arg, desc in info["args"].items()
            }
        }
        lines.append(f"{json.dumps(args_example, indent=2)}")
        lines.append("")  # spacer

    return "\n".join(lines)
