---
title: Commands
nav_order: 4
has_children: true
---

# Commands

In Fellow, commands are executable python functions that the AI agent can invoke. They are the primary mechanism through
which the assistant interacts with the codebase, filesystem, or external tools.

Commands are not just functions — they are structured components with:

- **Typed input validation** via Pydantic
- **Execution context** that includes the AI client and config
- **Standardized error handling**

This design makes commands reusable, testable, and safely invocable by the agent.

There are two main types of commands in Fellow:

- [Built-in Commands](/fellow/commands/builtin)
- [Custom Commands](/fellow/commands/custom)

---

## Command Structure

Each command is represented by a `Command` object that wraps:

- a **Pydantic model** describing its expected input (`CommandInput`)
- a **callable function** (the handler) that implements the command logic

Example:

```py
class MyHandlerInput(CommandInput):
    name: str


def my_handler(args: MyHandlerInput, context: CommandContext) -> str:
    return f"Hello World, {args.name}"


my_command = Command(MyInput, my_handler)
```

---

## CommandContext

Every command receives a `context` dictionary with two keys:

- `ai_client`: the current AI client instance
- `config`: the parsed configuration object

This allows commands to:

- Access the full task context
- Store logs or memory
- Make further API calls if needed
- use the AI client for eg summarization or reasoning

---

## Execution Flow

When a command is called by the AI agent:

1. The assistant chooses a command name and provides arguments as JSON.
2. Fellow parses the arguments using the command's `CommandInput` type.
3. If valid, the handler is called with `(args, context)`.
4. The result (a `str`) is logged and passed back to the assistant.
5. If parsing or execution fails, the error is caught and returned as `[ERROR]`.

---

## Error Handling

Fellow wraps both input validation and execution in `try/except` blocks:

- If input is malformed, a helpful error message is returned.
- If the handler raises an exception, it is caught and passed back as output.

This ensures that the assistant can continue reasoning and receive structured feedback even when a command fails.
