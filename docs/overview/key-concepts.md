---
title: Key Concepts
nav_order: 2
parent: Overview
---

# Key Concepts

Fellow is built around a few foundational ideas that shape how it works and how you interact with it. Understanding
these concepts will help you customize and extend it effectively.

---

## Task-Driven Execution

Everything in Fellow starts with a **task**, defined in a YAML file. This task is not just a goal — it's the seed for a
chain of reasoning. For example:

    task: |
      Generate a README for this project

This task is injected into a system prompt, which guides the AI in choosing and executing appropriate actions
step-by-step.

---

## Reasoning Loop

Fellow follows a simple but powerful loop:

1. Generate a message based on the task and current context
2. Optionally call a function (e.g. `edit_file`, `get_code`)
3. Execute function.
4. Log results and feed them back into the loop
5. Repeat until the AI outputs `END` or a step limit is reached

This enables autonomous workflows without needing to script each step.

---

## Plugin System: Commands

Commands are Python functions that the AI can call. Examples include:

- [create_file](/fellow/commands/builtin#create_file)
- [list_definitions](/fellow/commands/builtin#list_definitions)
- [run_pytest](/fellow/commands/builtin#run_pytest)

You can define your own custom commands or override existing ones. The AI sees these as callable tools and chooses when
to use them.

Learn more in the documentation:  
[Custom Commands](/fellow/commands/custom)

---

## Plugin System: Clients

Fellow is not tied to a single AI provider. It uses **clients** that wrap LLM APIs.

Built-in clients:

- [OpenAI](/fellow/clients/openai)

- [Gemini](/fellow/clients/gemini)

You can implement your own by creating a new client class. Learn more in the
documentation: [Custom Clients](/fellow/clients/custom)

---

## Memory

Fellow can persist a log of thoughts and actions between runs. This log (typically stored in `memory.json`) allows the
assistant to remember what it did in earlier steps and avoid redundant actions.

