import subprocess
import sys
from typing import Optional

from pydantic import Field

from fellow.commands import CommandInput
from fellow.commands.Command import CommandContext


class PipInstallInput(CommandInput):
    package_name: str = Field(..., description="Name of the package to install.")
    version: Optional[str] = Field(
        None, description="Version of the package to install in the format 'x.y.z'"
    )


def pip_install(args: PipInstallInput, context: CommandContext) -> str:
    """
    Install a Python package using pip. Optionally, specify a version.
    """
    if args.version:
        package_str = f"{args.package_name}=={args.version}"
    else:
        package_str = args.package_name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_str],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Failed to install {package_str}. Error: {e.stderr}"
    except Exception as ex:
        return f"An unexpected error occurred: {str(ex)}"
