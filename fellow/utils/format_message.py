import json

from pydantic import ValidationError

from fellow.commands import EditFileInput, MakePlanInput


def block(text: str, extension: str):
    text = text.replace("\\n", "\n")
    text = text.replace("\n", "\n> ")
    return f"""> ```{extension}
> {text}
> ```"""


def format_message(name: str, color: int, content: str) -> str:
    colors = ['#000000', '#1f77b4', '#ff7f0e']
    color_code = colors[color % len(colors)]
    pretty_text_block = ""
    try:
        data = json.loads(content)
        content_str = json.dumps(data, indent=2)
        lang = "json"
        if "edit_file" in data:
            try:
                edit_file = EditFileInput(**data["edit_file"])
                extension = edit_file.filepath.split(".")[-1]
                pretty_text_block = block(edit_file.new_text, extension)
            except ValidationError as e:
                pass
        if "make_plan" in data:
            try:
                make_plan = MakePlanInput(**data["make_plan"])
                pretty_text_block = block(make_plan.plan, "txt")
            except ValidationError:
                pass
    except Exception:
        content_str = content.strip()
        lang = "txt"

    indented = '\n'.join(f"> {line}" for line in content_str.splitlines())
    return f"""> <span style="color:{color_code}">**{name}:**</span>
>
> ```{lang}
{indented}
> ```
{pretty_text_block}
---
"""
