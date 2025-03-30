import os
from pydantic import Field

from fellow.commands.command import CommandInput


class EditFileInput(CommandInput):
    filepath: str = Field(..., description="The path to the file to edit.")
    from_line: int = Field(..., description="1-based start line (inclusive).")
    to_line: int = Field(..., description="1-based end line (exclusive). Equal to from_line for insertion.")
    new_text: str = Field(..., description="Text block to insert or replace.")


def edit_file(args: EditFileInput) -> str:
    """
    Edit a file by replacing lines [from_line, to_line) with new_text.
    If from_line == to_line, new_text is inserted.
    If new_text is empty, lines are deleted.
    """
    if not os.path.isfile(args.filepath):
        return f"[ERROR] File not found: {args.filepath}"

    try:
        with open(args.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)

        start = max(0, min(args.from_line - 1, total_lines))
        end = max(0, min(args.to_line - 1, total_lines))

        if start > end:
            return "[ERROR] Invalid line range: from_line must be <= to_line"

        # Split new_text by lines
        new_lines = []
        if args.new_text.strip():
            new_lines = [
                line if line.endswith("\n") else line + "\n"
                for line in args.new_text.splitlines()
            ]

        # Replace the range
        lines[start:end] = new_lines

        with open(args.filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"[OK] Edited file: {args.filepath}"

    except Exception as e:
        return f"[ERROR] Could not edit file: {e}"
