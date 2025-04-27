import os

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class EditFileInput(CommandInput):
    filepath: str = Field(..., description="The path to the file to edit.")
    new_text: str = Field(..., description="Text block to insert or replace.")


def edit_file(args: EditFileInput, context: CommandContext) -> str:
    """
    Edit a file by replacing the content with new text.
    """
    if not os.path.isfile(args.filepath):
        return f"[ERROR] File not found: {args.filepath}"

    try:
        with open(args.filepath, "w", encoding="utf-8") as f:
            f.write(args.new_text)
    except Exception as e:
        return f"[ERROR] Could not edit file: {e}"

    return f"[OK] Edited file: {args.filepath}"
