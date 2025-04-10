import json
from typing import Optional

from pydantic import ValidationError

from fellow.commands import EditFileInput, MakePlanInput

COLORS = ["#000000", "#1f77b4", "#ff7f0e"]


def format_message(
    name: str,
    color: int,
    content: str,
    spoiler: bool = False,
    language: Optional[str] = None,
) -> str:
    color_code = COLORS[color % len(COLORS)]
    output = f'<span style="color:{color_code}">**{name}:**</span>\n\n'
    if spoiler:
        output += """<details>
  <summary></summary>

"""
    addition = ""

    if language:
        output += f"```{language}\n"
        try:
            # Attempt to parse the content as JSON
            parsed_content = json.loads(content)
            content = json.dumps(parsed_content, indent=2)
            try:
                if parsed_content.get("function_name") == "edit_file":
                    edit_file = EditFileInput(**parsed_content["arguments"])
                    lang = edit_file.filepath.split(".")[-1]
                    addition = f"\n```{lang}\n{edit_file.new_text}\n```\n"
                if parsed_content.get("function_name") == "make_plan":
                    make_plan = MakePlanInput(**parsed_content["arguments"])
                    addition = f"\n```txt\n{make_plan.plan}\n```\n"
            except ValidationError:
                pass
            except KeyError:
                pass
        except json.JSONDecodeError:
            pass

    output += content

    if language:
        output += f"\n````\n{addition}"
    if spoiler:
        output += "\n\n</details>"
    return output + "\n\n---\n\n"
