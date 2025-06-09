---
title: OpenAIClient
nav_order: 1
parent: Clients
---

# OpenAIClient

The `OpenAIClient` is the default AI backend used in Fellow. It uses the OpenAI Chat Completion API to process user inputs, execute tools (functions), and reason step-by-step. It supports memory tracking, auto-summarization, and function calling with JSON-schema-based tool definitions.

---

## Requirements

You must set your OpenAI API key via the `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY=sk-...
```

The key is **not** configured in YAML for security reasons.

---

## Configuration

The `OpenAIClient` is used by default, so unless you override it, the following configuration is assumed:

```yaml
ai_client:
  client: openai
  config:
    memory_max_tokens: 15000
    summary_memory_max_tokens: 15000
    model: "gpt-4o"
```

### Explanation of fields:

- **`client`**: Identifier for the client to use. The string `"openai"` maps to `fellow.clients.openai.OpenAIClient`. You don’t need to change this unless you want to use a different backend.
  
- **`model`**: The OpenAI model to use (e.g., `"gpt-4"`, `"gpt-4o"`, `"gpt-3.5-turbo"`). Make sure the model supports function calling and system messages.

- **`memory_max_tokens`**: Maximum number of tokens allowed in active memory (`memory`). If this threshold is exceeded, older messages are summarized.

- **`summary_memory_max_tokens`**: Maximum number of tokens allowed in summarized memory (`summary_memory`). If this is exceeded, earlier summaries are recursively summarized again.

You can override these values in your own `config.yml` file to tweak performance, cost, or context handling to your needs.

---

## How it works

The `OpenAIClient` wraps the OpenAI `chat.completions.create` API and uses a structured message memory system. It interacts with the language model through a combination of **chat history**, **tool definitions**, and **function outputs**.

### Message Roles

The client supports four message roles:
- `"system"` – sets behavior instructions or plan context
- `"user"` – user prompts
- `"assistant"` – model responses or tool invocations
- `"function"` – result of a function executed by Fellow

All messages are token-counted and retained in memory until summarization is triggered.

---

## Memory System

The OpenAIClient keeps track of:
- `system_content` – static or dynamic instructions (e.g., task plan)
- `memory` – active working memory
- `summary_memory` – summarized chunks of past memory

### Summarization

If memory exceeds the configured `memory_max_tokens`, older memory is summarized into a compact system message and moved to `summary_memory`.

If even `summary_memory` grows beyond its token budget (`summary_memory_max_tokens`), it will be recursively summarized.

Summaries are generated using the same model via a separate chat prompt:
> “Summarize the following conversation for context retention.”

---

## Function Calling

Each command is automatically converted to an OpenAI tool definition using its `CommandInput` schema and the handler’s docstring.

When calling `chat()`, the client:
- Sends messages and tool definitions
- Lets the model choose whether to call a function
- If a function is called, executes it and feeds the result back
- Continues with a follow-up assistant message if needed

---

## `make_plan` Integration

The `make_plan` command stores a string inside `system_content`, which is prepended to every prompt. This allows a planning phase to guide execution without constantly re-injecting goals.

Internally, `make_plan` uses `OpenAIClient.set_plan(plan: str)`.

---

## Storing Memory

You can persist the memory to disk:

```python
client.store_memory("memory.json")
```

This writes the full history (including token counts) to a JSON file.