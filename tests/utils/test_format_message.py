from fellow.utils.format_message import format_ai_message


def test_format_message_json_extraction():
    ai_answer = """
Thought: I'm thinking a little bit ...
Action: {
    "command_name": {
      "arg1": "value",
      "arg2": "value"
    }
  }
Thought: I need to do something else ...
"""
    result = format_ai_message("Alice", 1, ai_answer)
    assert result == """> <span style="color:#1f77b4">**Alice:**</span>
>
> > Thought: I'm thinking a little bit ...
> > Action: 
> > ```json
> > {
> >   "command_name": {
> >     "arg1": "value",
> >     "arg2": "value"
> >   }
> > }
> > ```
> > 
> > Thought: I need to do something else ...

---
"""


def test_plain_text_content():
    result = format_ai_message("Bob", 2, "Hello, how are you?")
    assert result == """> <span style="color:#ff7f0e">**Bob:**</span>
>
> > Hello, how are you?

---
"""


def test_valid_json_no_new_text():
    json_str = '''
    Action: {
        "message": "Hi",
        "number": 42
    }
    '''
    result = format_ai_message("Alice", 1, json_str)
    assert result == """> <span style="color:#1f77b4">**Alice:**</span>
>
> > Action: 
> > ```json
> > {
> >   "message": "Hi",
> >   "number": 42
> > }
> > ```
> > 

---
"""


def test_invalid_json_falls_back_to_text():
    result = format_ai_message("Alice", 1, "Action: {not valid json}")
    assert result == """> <span style="color:#1f77b4">**Alice:**</span>
>
> > Action: {not valid json}

---
"""


def test_color_wraparound():
    result = format_ai_message("Charlie", 5, "Plain text")
    assert '#ff7f0e' in result


def test_valid_json_with_new_text():
    json_str = '''Some thoughst lorem ipsum

Action: 
{
    "edit_file": {
        "filepath": "test.py",
        "from_line": 1,
        "to_line": 1,
        "new_text": "import os\\\\nprint('hi')"
    }
}

Some more thoughts'''
    result = format_ai_message("Alice", 1, json_str)
    assert result == """> <span style="color:#1f77b4">**Alice:**</span>
>
> > Some thoughst lorem ipsum
> > Action: 
> > ```json
> > {
> >   "edit_file": {
> >     "filepath": "test.py",
> >     "from_line": 1,
> >     "to_line": 1,
> >     "new_text": "import os\\\\nprint('hi')"
> >   }
> > }
> > ```
> > 
> > Some more thoughts
> > ````py
> > import os
> > print('hi')
> > ````
---
"""


def test_correct_extension():
    json_str = '''Action:
        {
            "edit_file": {
                "filepath": "test.yml",
                "new_text": "openai_config:\\n\\tmodel: 'o3-mini'\\nplanning:\\n\\tactive: true",
                "from_line": 1,
                "to_line": 1
            }
        }
    '''
    result = format_ai_message("Alice", 0, json_str)
    assert result == """> <span style="color:#000000">**Alice:**</span>
>
> > Action: 
> > ```json
> > {
> >   "edit_file": {
> >     "filepath": "test.yml",
> >     "new_text": "openai_config:\\n\\tmodel: 'o3-mini'\\nplanning:\\n\\tactive: true",
> >     "from_line": 1,
> >     "to_line": 1
> >   }
> > }
> > ```
> > 
> > ````yml
> > openai_config:
> > 	model: 'o3-mini'
> > planning:
> > 	active: true
> > ````
---
"""
