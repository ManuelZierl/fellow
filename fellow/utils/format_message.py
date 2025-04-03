import json
from pydantic import ValidationError

from fellow.commands import EditFileInput

COLORS = ['#000000', '#1f77b4', '#ff7f0e']


def block(text: str, extension: str):
    text = text.replace("\\n", "\n")
    text = text.replace("\n", "\n> > ")
    return f"""> > ````{extension}\n> > {text}\n> > ````"""


def format_ai_message(name: str, color: int, content: str) -> str:
    color_code = COLORS[color % len(COLORS)]
    result_lines = []
    pretty_text_block = ""

    i = 0
    while i < len(content):
        action_idx = content.find("Action:", i)
        if action_idx == -1:
            # No more actions; just indent rest and break
            remainder = content[i:].strip()
            if remainder:
                result_lines.append('\n'.join(f"> > {line}" for line in remainder.splitlines()))
            break

        # Add everything before Action:
        before_action = content[i:action_idx].strip()
        if before_action:
            result_lines.append('\n'.join(f"> > {line}" for line in before_action.splitlines()))

        # Find start of JSON block
        json_start = content.find("{", action_idx)
        if json_start == -1:
            # No JSON found after Action:
            result_lines.append("> > Action: [malformed or missing JSON]")
            break

        # Match braces to find end of JSON
        brace_count = 0
        end_json = None
        for j in range(json_start, len(content)):
            if content[j] == "{":
                brace_count += 1
            elif content[j] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_json = j + 1
                    break

        if end_json is None:
            result_lines.append("> > Action: [unmatched braces]")
            break

        raw_json = content[json_start:end_json]
        try:
            parsed = json.loads(raw_json)
            pretty_json = json.dumps(parsed, indent=2)
            json_block = '\n'.join(f"> > {line}" for line in f"```json\n{pretty_json}\n```\n\n".splitlines())

            result_lines.append("> > Action: ")
            result_lines.append(json_block)

            # Handle optional pretty block for edit_file
            if isinstance(parsed, dict) and "edit_file" in parsed:
                try:
                    print("in here")

                    edit_file = EditFileInput(**parsed["edit_file"])
                    print(edit_file)
                    extension = edit_file.filepath.split(".")[-1]
                    pretty_text_block = block(edit_file.new_text, extension)
                except ValidationError:
                    pass
        except json.JSONDecodeError:
            raw = content[action_idx:end_json]
            result_lines.append('\n'.join(f"> > {line}" for line in raw.strip().splitlines()))

        i = end_json

    indented_output = '\n'.join(result_lines)

    return f"""> <span style="color:{color_code}">**{name}:**</span>
>
{indented_output}
{pretty_text_block}
---
"""

def format_output_message(name: str, color: int, content: str) -> str:
    color_code = COLORS[color % len(COLORS)]
    indented = '\n'.join(f"> {line}" for line in content.strip().splitlines())
    return f"""> <span style=\"color:{color_code}\">**{name}:**</span>
>
> ````txt
{indented}
> ````
---
"""