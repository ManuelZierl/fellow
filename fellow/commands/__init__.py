from typing import Dict, Tuple, Type, TypeVar

from fellow.commands.Command import CommandHandler, CommandInput
from fellow.commands.create_file import CreateFileInput, create_file
from fellow.commands.delete_file import DeleteFileInput, delete_file
from fellow.commands.edit_file import EditFileInput, edit_file
from fellow.commands.get_code import GetCodeInput, get_code
from fellow.commands.list_definitions import ListDefinitionsInput, list_definitions
from fellow.commands.list_files import ListFilesInput, list_files
from fellow.commands.make_plan import MakePlanInput, make_plan
from fellow.commands.pip_install import PipInstallInput, pip_install
from fellow.commands.run_pytest import RunPytestInput, run_pytest
from fellow.commands.run_python import RunPythonInput, run_python
from fellow.commands.summarize_file import SummarizeFileInput, summarize_file
from fellow.commands.view_file import ViewFileInput, view_file

T = TypeVar("T", bound=CommandInput)

CommandTuple = Tuple[Type[T], CommandHandler[T]]

ALL_COMMANDS: Dict[str, CommandTuple] = {
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
    "summarize_file": (SummarizeFileInput, summarize_file),
    "pip_install": (PipInstallInput, pip_install),
}
