import json

import pytest

from fellow.utils.format_message import format_message  # adjust path if needed


def test_plain_text_no_language():
    result = format_message("Alice", 0, "Hello, world!")
    expected = (
        '<span style="color:#000000">**Alice:**</span>\n\nHello, world!\n\n---\n\n'
    )
    assert result == expected


def test_markdown_with_language_and_valid_json():
    content = '{"key": "value"}'
    result = format_message("Bob", 1, content, language="json")
    assert (
        result
        == """<span style="color:#1f77b4">**Bob:**</span>

```json
{
  "key": "value"
}
````


---

"""
    )


def test_color_wrapping():
    result = format_message("Dan", 5, "Hi")
    expected_color = "#1f77b4"  # 5 % 3 = 2 → COLORS[2] = "#ff7f0e"
    assert f'style="color:{expected_color}"' not in result
    expected_color = "#ff7f0e"
    assert f'style="color:{expected_color}"' in result


def test_edit_file_log():
    result = format_message(
        name="AI",
        color=1,
        content=json.dumps(
            {
                "function_name": "edit_file",
                "arguments": {
                    "filepath": "test.py",
                    "new_text": "import os\n\nprint('Hello, world!')",
                },
            }
        ),
        language="json",
    )

    assert (
        result
        == """<span style="color:#1f77b4">**AI:**</span>

```json
{
  "function_name": "edit_file",
  "arguments": {
    "filepath": "test.py",
    "new_text": "import os\\n\\nprint('Hello, world!')"
  }
}
````

```py
import os

print('Hello, world!')
```


---

"""
    )


def test_make_plan_log():
    result = format_message(
        name="AI",
        color=1,
        content=json.dumps(
            {
                "function_name": "make_plan",
                "arguments": {
                    "plan": "1. Do this\n2. Do that",
                },
            }
        ),
        language="json",
    )
    assert (
        result
        == """<span style="color:#1f77b4">**AI:**</span>

```json
{
  "function_name": "make_plan",
  "arguments": {
    "plan": "1. Do this\\n2. Do that"
  }
}
````

```txt
1. Do this
2. Do that
```


---

"""
    )
