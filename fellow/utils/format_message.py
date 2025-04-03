import pytest
import json

from pydantic import ValidationError

from fellow.commands import EditFileInput, MakePlanInput
from fellow.utils.extract_command_block import extract_command_block, find_action_start_and_end

COLORS = ['#000000', '#1f77b4', '#ff7f0e']

def block(text: str, extension: str):
    text = text.replace("\\n", "\n")
    text = text.replace("\n", "\n> > ")
    return f"""> > ````{extension}\n> > {text}\n> > ````"""


def format_ai_message(name: str, color: int, content: str) -> str:
    color_code = COLORS[color % len(COLORS)]
    pretty_text_block = ""

    # data = extract_command_block(content)
    action_start_and_end = find_action_start_and_end(content)
    if not isinstance(action_start_and_end, str):
        start_json, end_json = action_start_and_end
        content1, json_str, content2 = content[:start_json], content[start_json:end_json], content[end_json:]
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            json_data = None
        if json_data:
            # todo: extract new_text or make_plan?
            if "edit_file" in json_data:
                try:
                    edit_file = EditFileInput(**json_data["edit_file"])
                    extension = edit_file.filepath.split(".")[-1]
                    pretty_text_block = block(edit_file.new_text, extension)
                except ValidationError:
                    pass
            json_content_str = json.dumps(json_data, indent=2)
            content = f"""{content1}
```json
{json_content_str}
```
{content2}"""
        else:
            content = f"{content1}\n{json_str}\n{content2}"

    indented = '\n'.join(f"> > {line}" for line in content.strip().splitlines())
    return f"""> <span style=\"color:{color_code}\">**{name}:**</span>
>
{indented}
{pretty_text_block}
---
"""

def format_output_message(name: str, color: int, content: str) -> str:
    color_code = COLORS[color % len(COLORS)]
    indented = '\n'.join(f"> {line}" for line in content.strip().splitlines())
    return f"""> <span style=\"color:{color_code}\">**{name}:**</span>
>
> ```txt
{indented}
> ```
---
"""