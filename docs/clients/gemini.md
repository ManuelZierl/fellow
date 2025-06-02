---
title: GeminiClient
nav_order: 2
parent: Clients
---

# GeminiClient

The `GeminiClient` is an alternative to the default OpenAI backend and connects to Google's Gemini API using the Google
Generative AI SDK. It supports:

- Full chat history handling
- Tool/function calling
- Configurable model selection

⚠️ **Note:** Summarization and token management are not yet implemented in the current version.

---

## Requirements

You must set the `GEMINI_API_KEY` environment variable:

```bash
export GEMINI_API_KEY="your-secret-key"
```

The key is **not** configured in YAML for security reasons.

---

## Configuration

To enable the `GeminiClient`, override the AI client config in your `config.yml`:

```yaml
ai_client:
  client: gemini
  config:
    model: "gemini-1.5-flash"
    system_content: "You are a helpful assistant."
```

### Field explanation:

- **`client`**: Set this to `"gemini"` to activate the Gemini backend.
- **`model`**: Must be a valid Gemini model identifier. Examples:
    - `"gemini-1.0-pro"`
    - `"gemini-1.5-pro"`
    - `"gemini-1.5-flash"`
- **`system_content`**: Initial system message injected into the context. This is currently sent as a plain message
  since Gemini doesn’t support `system` roles explicitly.

---

## How it works

GeminiClient wraps a persistent `genai.Client().chats.create()` session and sends messages or function results using
`send_message()`.

Each message can optionally contain:

- plain user text, or
- a function result (structured as a `Part`), which the model understands as a prior tool output.

Function calling is handled via the `function_declarations` tool, and responses are parsed for potential function calls
with `response.function_calls`.

---

## Features

- Persistent chat thread
- Function calling via tool integration
- JSON-based memory export via `store_memory()`
- Basic `set_plan()` support (sends a system message)

**Limitations:**

- No token tracking or summarization
- Limited support for `anyOf` types in schemas (e.g., `Optional[int]` is converted to `int`)
- Requires schema post-processing to strip unsupported fields (like `title`, `default`, or certain union types)
