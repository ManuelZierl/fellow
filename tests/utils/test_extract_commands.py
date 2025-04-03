import pytest
from fellow.utils.extract_commands import extract_json_objects, flatten_command_dicts, extract_commands
from typing import List, Tuple, Union
from fellow.commands import ALL_COMMANDS, CommandInput, CommandHandler


def test_single_json_object():
    text = '{"foo": "bar"}'
    result = extract_json_objects(text)
    assert result == [{"foo": "bar"}]


def test_multiple_json_objects():
    text = '{"a": 1} some text {"b": 2}'
    result = extract_json_objects(text)
    assert result == [{"a": 1}, {"b": 2}]


def test_nested_json_object():
    text = '{"outer": {"inner": {"value": 42}}}'
    result = extract_json_objects(text)
    assert result == [{"outer": {"inner": {"value": 42}}}]


def test_json_object_with_list():
    text = '{"numbers": [1, 2, 3]}'
    result = extract_json_objects(text)
    assert result == [{"numbers": [1, 2, 3]}]


def test_json_array_as_root():
    text = '[{"cmd": "run"}, {"cmd": "stop"}]'
    result = extract_json_objects(text)
    assert result == [{"cmd": "run"}, {"cmd": "stop"}]


def test_json_inside_messy_text():
    text = """
    Here's a note.

    {
      "cmd": "edit",
      "args": {
        "filepath": "foo.py"
      }
    }

    And some more commentary.
    """
    result = extract_json_objects(text)
    assert len(result) == 1
    assert result[0]["cmd"] == "edit"
    assert result[0]["args"]["filepath"] == "foo.py"


def test_ignores_invalid_json():
    text = '{invalid json}'  # not valid
    result = extract_json_objects(text)
    assert result == []


def test_handles_unbalanced_braces():
    text = '{"foo": "bar"'  # missing closing }
    result = extract_json_objects(text)
    assert result == []

    text2 = '"foo": "bar"}'  # missing opening {
    result2 = extract_json_objects(text2)
    assert result2 == []

    text3 = '{ "foo": {"bar": 1} '  # missing outer }
    result3 = extract_json_objects(text3)
    assert result3 == []


def test_handles_back_to_back_json():
    text = '{"a": 1}{"b": 2}{"c": 3}'
    result = extract_json_objects(text)
    assert result == [{"a": 1}, {"b": 2}, {"c": 3}]


def test_single_command_dict():
    blocks = [{"edit_file": {"filepath": "a.py", "from_line": 1, "to_line": 2, "new_text": "print(1)"}}]
    result = flatten_command_dicts(blocks)
    assert result == blocks


def test_list_of_command_dicts():
    blocks = [
        {"edit_file": {"filepath": "a.py"}},
        {"create_file": {"filepath": "b.py"}}
    ]
    result = flatten_command_dicts(blocks)
    assert result == blocks


def test_commands_inside_wrapper_dict():
    blocks = [
        {
            "commands": [
                {"edit_file": {"filepath": "a.py"}},
                {"create_file": {"filepath": "b.py"}}
            ]
        }
    ]
    result = flatten_command_dicts(blocks)
    assert result == [
        {"edit_file": {"filepath": "a.py"}},
        {"create_file": {"filepath": "b.py"}}
    ]


def test_mixed_command_dicts_and_wrappers():
    blocks = [
        {
            "commands": [
                {"edit_file": {"filepath": "a.py"}}
            ]
        },
        {"create_file": {"filepath": "b.py"}}
    ]
    result = flatten_command_dicts(blocks)
    assert result == [
        {"edit_file": {"filepath": "a.py"}},
        {"create_file": {"filepath": "b.py"}}
    ]


def test_nested_list_of_dicts():
    blocks = [
        [
            {"edit_file": {"filepath": "x.py"}},
            {"create_file": {"filepath": "y.py"}}
        ]
    ]
    result = flatten_command_dicts(blocks)
    assert result == [
        {"edit_file": {"filepath": "x.py"}},
        {"create_file": {"filepath": "y.py"}}
    ]


def test_invalid_entries_are_ignored():
    blocks = [
        123,
        "not a dict",
        {"commands": "also not a list"},
        {"edit_file": {"filepath": "a.py"}}
    ]
    result = flatten_command_dicts(blocks)
    assert result == [{"edit_file": {"filepath": "a.py"}}]


def test_empty_and_none_blocks():
    blocks = []
    assert flatten_command_dicts(blocks) == []

    blocks = [None]
    assert flatten_command_dicts(blocks) == []

    blocks = [{"commands": []}]
    assert flatten_command_dicts(blocks) == []


def run_extract(text: str) -> Union[List[Tuple[CommandInput, CommandHandler]], str]:
    return extract_commands(text, ALL_COMMANDS)


def test_valid_single_command():
    text = """
    Here is what you should do:
    {
      "create_file": {
        "filepath": "test.py"
      }
    }
    """
    result = run_extract(text)
    assert isinstance(result, list)
    assert len(result) == 1
    input_obj, handler = result[0]
    assert input_obj.filepath == "test.py"
    assert handler.__name__ == "create_file"


def test_valid_commands_list():
    text = """
    {
      "commands": [
        {
          "create_file": {"filepath": "a.py"}
        },
        {
          "delete_file": {"filepath": "b.py"}
        }
      ]
    }
    """
    result = run_extract(text)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0][0].filepath == "a.py"
    assert result[1][0].filepath == "b.py"


def test_invalid_command_name():
    text = """
    {
      "unknown_command": {
        "something": "value"
      }
    }
    """
    result = run_extract(text)
    assert isinstance(result, str)
    assert "[ERROR] Unknown command" in result


def test_invalid_command_args_type():
    text = """
    {
      "create_file": "not a dict"
    }
    """
    result = run_extract(text)
    assert isinstance(result, str)
    assert "[ERROR] Command arguments must be an object." in result


def test_invalid_command_args_values():
    text = """
    {
      "create_file": {
        "not_a_valid_field": "oops"
      }
    }
    """
    result = run_extract(text)
    assert isinstance(result, str)
    assert "Invalid command arguments for 'create_file'" in result


def test_multiple_json_blocks_with_text_between():
    text = """
    Some thoughts...
    {
      "create_file": {"filepath": "one.py"}
    }
    More thoughts...
    {
      "delete_file": {"filepath": "two.py"}
    }
    """
    result = run_extract(text)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0][0].filepath == "one.py"
    assert result[1][0].filepath == "two.py"


def test_skips_non_dict_blocks():
    text = """
    Some text
    123
    "not json"
    {
      "create_file": {"filepath": "x.py"}
    }
    """
    result = run_extract(text)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0][0].filepath == "x.py"


def test_empty_string_returns_empty_list():
    result = run_extract("")
    assert result == []
