import os
from typing import List, Optional

from pydantic import Field

from fellow.commands.Command import CommandContext, CommandInput


class SearchFilesInput(CommandInput):
    directory: str = Field(..., description="The relative directory to search in.")
    search: str = Field(..., description="The string to search for (case-insensitive).")
    extension: Optional[str] = Field(
        None, description="Only include files with this extension (e.g., .py)."
    )


def search_files(args: SearchFilesInput, context: CommandContext) -> str:
    """
    Recursively search for a string (case-insensitive) in all files under a given directory.
    Optionally restrict to files with a given extension. Its essentially a grep command.
    """
    base_dir = os.path.abspath(os.path.join(os.getcwd(), args.directory))

    if not os.path.isdir(base_dir):
        return f"[ERROR] Directory not found: {args.directory}"

    matches: List[str] = []
    needle = args.search.lower()

    for root, _, files in os.walk(base_dir):
        for file in files:
            if args.extension and not file.endswith(args.extension):
                continue

            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if needle in line.lower():
                            rel_path = os.path.relpath(path, start=os.getcwd())
                            matches.append(f"{rel_path}:{i}: {line.strip()}")
            except Exception as e:
                matches.append(f"[ERROR] Could not read {path}: {e}")

    if not matches:
        return f"[INFO] No matches found for '{args.search}' in {args.directory}"

    return "\n".join(matches)
