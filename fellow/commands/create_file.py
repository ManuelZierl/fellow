import os

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class CreateFileInput(CommandInput):
    filepath: str = Field(..., description="The path of the file to create.")


def create_file(args: CreateFileInput, context: CommandContext) -> str:
    """
    Create an empty file at the given path. If the file already exists, it will not be modified.
    """
    if os.path.exists(args.filepath):
        return f"[INFO] File already exists: {args.filepath}"

    try:
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(args.filepath) or ".", exist_ok=True)

        # Create the file
        with open(args.filepath, "x", encoding="utf-8") as f:
            pass

        return f"[OK] Created file: {args.filepath}"

    except Exception as e:
        return f"[ERROR] Could not create file: {e}"
