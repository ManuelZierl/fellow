---
title: Custom Commands
nav_order: 2
parent: Commands
---

# Custom Commands

Fellow supports custom commands that let you define your own tools for the AI to use.  
These commands follow the same structure as built-ins but live in your own project directory — typically
`.fellow/commands`.

You can use custom commands to automate repetitive tasks, interact with your specific environment, or override built-in
behavior.

---

## Purpose and Structure

A custom command in Fellow consists of two parts:

1. A **Pydantic model** that defines the expected input arguments (`CommandInput`)
2. A **handler function** that implements the logic of the command

These are combined using the `Command` class to form a complete callable tool.  
When a task is executed, Fellow validates the input against your schema and passes in a shared execution context.

Additionally, the **docstring of the function is extracted** at runtime and used as a description when the AI client
registers available tools — so make sure it's short, clear, and helpful.

### Example

Let's say you want to create a command that counts how many times a word appears in a file:

```python
from fellow.commands.command import CommandContext, CommandInput
from pydantic import Field


class CountWordInput(CommandInput):
    filepath: str = Field(..., description="Path to the file")
    word: str = Field(..., description="The word to count")


def count_word(args: CountWordInput, context: CommandContext) -> str:
    """Counts how often a given word appears in a file."""
    try:
        with open(args.filepath, "r") as f:
            content = f.read()
        count = content.count(args.word)
        return f"The word '{args.word}' appears {count} times."
    except FileNotFoundError:
        return f"[ERROR] File not found: {args.filepath}"
    except Exception as e:
        return f"[ERROR] Unexpected error: {e}"
```

- The `CommandInput` class defines which fields the AI must provide
- The handler function performs the task and returns a string response
- The function’s docstring explains to the AI what the command does
- The pydantic descriptions are used to generate tool documentation for the AI client

---

## How to Create a Custom Command

The easiest way to scaffold a command is with:

> fellow init-command my_custom_command

This will generate a Python file at the first path listed in `custom_commands_paths` in your config (typically
`.fellow/commands/`).

It creates a boilerplate file that includes:

- a properly named `CommandInput` class
- a handler function
- docstrings and descriptions

---

## File Location and Config Registration

All custom commands must be located in a folder listed in your config under `custom_commands_paths`.

For example, in your YAML config:

```yml
custom_commands_paths:
  - ".fellow/commands"
```

You must also register your command explicitly in the `commands` list:

```yml
commands:
  - "create_file"
  - "count_word"
  ...
```

If you forget to register the command, it won’t be available to the agent — even if it’s implemented correctly.

---

## Overriding Built-in Commands

You can override any built-in command by using the same command name in your custom implementation.

For example, if you create a custom `edit_file` in `.fellow/commands/edit_file.py` and register it in your config,
Fellow will use your version instead of the built-in one.

This makes it easy to tweak behavior without modifying the core codebase.

---

## The `run` Method and `CommandContext`

All commands are run through the same internal interface:

- The AI calls a command with arguments (as a JSON string)
- Fellow parses those into your `CommandInput`
- The function receives two arguments:
    - `args` — validated instance of your `CommandInput`
    - `context` — a dictionary containing:
        - `ai_client`: the active client
        - `config`: the loaded config object

This context allows commands to:

- Log output
- Access config settings
- Call other AI tools if needed

You don’t need to worry about calling the `run` method directly — Fellow handles it when executing the reasoning loop.

## Example Use Case

Suppose you want to create a command that commits and pushes changes to Git:

```python
from fellow.commands.command import CommandContext, CommandInput
from pydantic import Field
import subprocess


class GitPushInput(CommandInput):
    message: str = Field(..., description="The commit message")


def git_push(args: GitPushInput, context: CommandContext) -> str:
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", args.message], check=True)
        subprocess.run(["git", "push"], check=True)
        return "[OK] Changes pushed to Git."
    except Exception as e:
        return f"[ERROR] Git push failed: {e}"
```

Register it in your config:

```yml
    commands:
      - git_push
```

Now the assistant can use this command to commit code autonomously.
