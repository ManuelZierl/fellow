import subprocess

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class RunPytestInput(CommandInput):
    target: str = Field(
        ..., description="Path to a test file or directory to run pytest on."
    )
    args: str = Field(
        default="",
        description="Optional arguments to pass to pytest (e.g., '-k test_name').",
    )


def run_pytest(args: RunPytestInput, context: CommandContext) -> str:
    """
    Runs pytest on the specified file or directory with optional arguments.
    Returns the captured output or error message.
    """
    cmd = ["pytest", args.target] + args.args.split()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=20  # prevent runaway tests
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return output or "[INFO] Tests ran successfully with no output."
        else:
            return f"[ERROR] Pytest exited with code {result.returncode}:\n{error or output}"

    except FileNotFoundError:
        return f"[ERROR] Test file or directory not found: {args.target}"
    except Exception as e:
        return f"[ERROR] Failed to run pytest: {e}"
