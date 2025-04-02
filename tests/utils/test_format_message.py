from fellow.utils.format_message import format_message


def test_plain_text_content():
    result = format_message("Bob", 2, "Hello, how are you?")
    assert "**Bob:**" in result
    assert "```txt" in result
    assert "Hello, how are you?" in result


def test_valid_json_no_new_text():
    json_str = '''
    {
        "message": "Hi",
        "number": 42
    }
    '''
    result = format_message("Alice", 1, json_str)
    assert "**Alice:**" in result
    assert "```json" in result
    assert '"message": "Hi"' in result
    assert "```python" not in result


def test_valid_json_with_new_text():
    json_str = '''
    {
        "edit_file": {
            "filepath": "test.py",
            "from_line": 1,
            "to_line": 1,
            "new_text": "import os\\\\nprint('hi')"
        }
    }
    '''
    result = format_message("Alice", 1, json_str)
    assert result == """> <span style="color:#1f77b4">**Alice:**</span>
>
> ```json
> {
>   "edit_file": {
>     "filepath": "test.py",
>     "from_line": 1,
>     "to_line": 1,
>     "new_text": "import os\\\\nprint(\'hi\')"
>   }
> }
> ```
> ```py
> import os
> print('hi')
> ```
---
"""


def test_invalid_json_falls_back_to_text():
    result = format_message("Alice", 1, "{not valid json}")
    assert "```json" not in result
    assert "```txt" in result
    assert "{not valid json}" in result


def test_color_wraparound():
    result = format_message("Charlie", 5, "Plain text")
    # Should wrap around to colors[5 % 3] = colors[2] = "#ff7f0e"
    assert '#ff7f0e' in result


def test_new_text_already_split_list_is_ignored():
    # Should not crash; the list is ignored, no python block shown
    json_str = '''
    {
        "edit_file": {
            "filepath": "test.py",
            "new_text": ["import os", "print('hi')"]
        }
    }
    '''
    result = format_message("Eve", 0, json_str)
    assert "```json" in result
    assert "```python" not in result

def test_correct_extension():
    json_str = '''
        {
            "edit_file": {
                "filepath": "test.yml",
                "new_text": "openai_config:\\n\\tmodel: 'o3-mini'\\nplanning:\\n\\tactive: true",
                "from_line": 1,
                "to_line": 1
            }
        }
    '''
    result = format_message("Alice", 0, json_str)
    assert result == """> <span style="color:#000000">**Alice:**</span>
>
> ```json
> {
>   "edit_file": {
>     "filepath": "test.yml",
>     "new_text": "openai_config:\n\tmodel: 'o3-mini'\nplanning:\n\tactive: true",
>     "from_line": 1,
>     "to_line": 1
>   }
> }
> ```
> ```yml
> openai_config:
> 	model: 'o3-mini'
> planning:
> 	active: true
> ```
---"""