import json
from typing import Optional

def format_message(name: str, color: int, content: str, language: Optional[str] = None) -> str:
    colors = ['#000000', '#1f77b4', '#ff7f0e']
    color_code = colors[color%len(colors)]

    python_code_block = ""

    try:
        data = json.loads(content)
        content_str = json.dumps(data, indent=2)
        lang = "json"

        # If edit_file.new_text exists and is a string with escaped newlines, extract it
        new_text = (
            data.get("edit_file", {}).get("new_text")
            if isinstance(data, dict) else None
        )
        if isinstance(new_text, str):
            python_code = new_text.replace("\\n", "\n").strip()
            python_code = python_code.replace("\n", "\n> ")
            python_code_block = f"""\n>
> ```python
> {python_code}
> ```"""
    except Exception:
        content_str = content.strip()
        lang = "txt"

    indented = '\n'.join(f"> {line}" for line in content_str.splitlines())

    return f"""> <span style="color:{color_code}">**{name}:**</span>
>
> ```{lang}
{indented}
> ```{python_code_block}
---
"""
