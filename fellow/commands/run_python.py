import subprocess

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class RunPythonInput(CommandInput):
    filepath: str = Field(..., description="Path to the Python script to run.")
    args: str = Field(
        default="", description="Optional arguments passed to the script."
    )


def run_python(args: RunPythonInput, context: CommandContext) -> str:
    """
    Runs a Python script in a subprocess and captures stdout and stderr.
    """
    cmd = ["python", args.filepath] + args.args.split()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,  # optional: prevent runaway processes
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return output or "[INFO] Script ran successfully with no output."
        else:
            return f"[ERROR] Script exited with code {result.returncode}:\n{error or output}"

    except FileNotFoundError:
        return f"[ERROR] File not found: {args.filepath}"
    except Exception as e:
        return f"[ERROR] Failed to run script: {e}"
