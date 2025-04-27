import os

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class DeleteFileInput(CommandInput):
    filepath: str = Field(..., description="Path to the file to delete.")


def delete_file(args: DeleteFileInput, context: CommandContext) -> str:
    """
    Deletes a file from the filesystem. Fails if it's a directory or doesn't exist.
    """
    if not os.path.exists(args.filepath):
        return f"[ERROR] File not found: {args.filepath}"

    if os.path.isdir(args.filepath):
        return f"[ERROR] {args.filepath} is a directory. Only files can be deleted."

    try:
        os.remove(args.filepath)
        return f"[OK] Deleted file: {args.filepath}"
    except Exception as e:
        return f"[ERROR] Failed to delete file: {e}"
