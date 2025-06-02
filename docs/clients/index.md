---
title: Clients
nav_order: 5
has_children: true
---

# Clients

Clients are interfaces between Fellow and an AI backend.

Fellow currently supports:
- OpenAI (via `OPENAI_API_KEY`)
- Gemini (via `GEMINI_API_KEY`)

You can also implement your own by creating a custom client class.

Each client defines how to generate completions, call functions, and handle memory, making plans and how the function is schematized for function-calling.
