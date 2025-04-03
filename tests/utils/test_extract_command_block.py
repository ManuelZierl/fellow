import pytest
from fellow.utils.extract_command_block import extract_command_block


def test_extract_valid_json():
    response = '''
    Thought: Let's edit the file.
    Action:
    {
      "edit_file": {
        "path": "main.py",
        "modification": "add function x()"
      }
    }
    Thought: Next, we verify the changes.
    '''
    expected = {
        "edit_file": {
            "path": "main.py",
            "modification": "add function x()"
        }
    }
    assert extract_command_block(response) == expected

def test_extract_nested_json():
    response = '''
    Thought: Now, let's perform a nested operation.
    Action:
    {
      "complex_command": {
        "config": {
          "settings": {
            "option": true,
            "parameters": [1, 2, 3]
          }
        }
      }
    }
    Thought: We'll check the output next.
    '''
    expected = {
        "complex_command": {
            "config": {
                "settings": {
                    "option": True,
                    "parameters": [1, 2, 3]
                }
            }
        }
    }
    assert extract_command_block(response) == expected

def test_extract_missing_action_block():
    response = '''
    Thought: This response has no action.
    '''
    assert extract_command_block(response) == "[ERROR] No Action: block found in response"

def test_extract_malformed_json():
    response = '''
    Thought: Malformed JSON ahead.
    Action:
    {
      "invalid_json": {
        "path": "main.py",
        "modification": "add function x("
    }
    Thought: Let's see if this raises an error.
    '''
    assert extract_command_block(response) == "[ERROR] JSON block braces do not match."

def test_extract_unbalanced_braces():
    response = '''
    Thought: Unbalanced braces here.
    Action:
    {
      "edit_file": {
        "path": "main.py",
        "modification": "add function x()"
    Thought: This should raise an error due to braces.
    '''
    assert extract_command_block(response) == "[ERROR] JSON block braces do not match."

def test_foo():
    response = '''
    Thought: It seems there was an issue with the JSON formatting. I will correct it and attempt to list the files in the project directory again.
    
    Action:
    {
      "list_files": {
        "directory": ".",
        "max_depth": 1
      }
    }
    '''
    print(extract_command_block(response))