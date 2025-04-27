import os
from typing import Optional

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class ViewFileInput(CommandInput):
    filepath: str = Field(..., description="The path to the file to be viewed.")
    from_line: Optional[int] = Field(
        None, description="Optional 1-based starting line number."
    )
    to_line: Optional[int] = Field(
        None, description="Optional 1-based ending line number (inclusive)."
    )


def view_file(args: ViewFileInput, context: CommandContext) -> str:
    """
    View the contents of a file, optionally between specific line numbers.
    """
    if not os.path.isfile(args.filepath):
        return f"[ERROR] File not found: {args.filepath}"

    try:
        with open(args.filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)

        start = args.from_line - 1 if args.from_line else 0
        end = args.to_line if args.to_line else total_lines

        # Cap to file boundaries
        start = max(0, min(start, total_lines))
        end = max(0, min(end, total_lines))
        if end == 0:
            return "[INFO] The file is empty or the specified range contains no lines."

        if start >= end:
            return "[INFO] No lines to display (start >= end)."

        return "".join(lines[start:end])

    except Exception as e:
        return f"[ERROR] Could not read file: {e}"
