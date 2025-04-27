import os
from typing import Optional

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class ListFilesInput(CommandInput):
    directory: str = Field(default=".", description="Directory to list.")
    max_depth: int = Field(
        ..., description="Maximum depth for recursion. 1 means only top-level files."
    )
    pattern: Optional[str] = Field(
        None, description="Optional substring to filter file names."
    )


def list_files(args: ListFilesInput, context: CommandContext) -> str:
    """
    List files in a directory up to a certain depth. Depth 1 = non-recursive. Optional name filter.
    """
    if not os.path.isdir(args.directory):
        return f"[ERROR] Not a directory: {args.directory}"

    if args.max_depth < 1:
        return "[ERROR] max_depth must be >= 1"

    try:
        output = []

        def walk(dir_path, depth):
            assert (
                depth <= args.max_depth
            ), f"Internal error: walk called with depth={depth} > max={args.max_depth}"

            entries = sorted(os.listdir(dir_path))
            for entry in entries:
                full_path = os.path.join(dir_path, entry)
                is_dir = os.path.isdir(full_path)

                indent = "  " * (depth - 1)

                # Always show directories so we can descend
                if is_dir:
                    output.append(f"{indent}{entry}/")
                    if depth < args.max_depth:
                        walk(full_path, depth + 1)
                else:
                    if args.pattern and args.pattern not in entry:
                        continue
                    output.append(f"{indent}{entry}")

        walk(args.directory, 1)
        return "\n".join(output) or "[INFO] No matching files found."

    except Exception as e:
        return f"[ERROR] Could not list files: {e}"
