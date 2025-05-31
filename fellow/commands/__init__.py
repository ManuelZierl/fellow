from typing import Dict

from fellow.commands.Command import Command, CommandHandler, CommandInput
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

ALL_COMMANDS: Dict[str, Command] = {
    "create_file": Command(CreateFileInput, create_file),
    "view_file": Command(ViewFileInput, view_file),
    "delete_file": Command(DeleteFileInput, delete_file),
    "edit_file": Command(EditFileInput, edit_file),
    "list_files": Command(ListFilesInput, list_files),
    "run_python": Command(RunPythonInput, run_python),
    "run_pytest": Command(RunPytestInput, run_pytest),
    "list_definitions": Command(ListDefinitionsInput, list_definitions),
    "get_code": Command(GetCodeInput, get_code),
    "make_plan": Command(MakePlanInput, make_plan),
    "summarize_file": Command(SummarizeFileInput, summarize_file),
    "pip_install": Command(PipInstallInput, pip_install),
}
